import calendar
import copy
import datetime
import time

from django.conf import settings
from django.db.models.signals import post_save

from django.contrib import auth
from django.contrib.auth.models import User

COOKIE_USER_DATA_KEY = '_UD'
COOKIE_USER_DATA_TS_KEY = '_UDT'
# Defaults to 4 hours in seconds
COOKIE_USER_REFRESH_TIME = getattr(settings, 'COOKIE_USER_REFRESH_TIME',
    14400)

auth_get_user = copy.deepcopy(auth.get_user)


def datetime_to_timestamp(dt):
    ts = calendar.timegm(dt.timetuple()) + (dt.microsecond / 1000000.0)
    return long(ts * 1000000.0)

def timestamp_to_datetime(ts):
    return datetime.datetime.utcfromtimestamp(ts / 1000000.0)

def cookie_set_user(request, force=False):
    user = request.user
    data = [
        user.username,
        user.first_name,
        user.last_name,
        user.email,
        user.password,
        user.is_staff,
        user.is_active,
        user.is_superuser,
        datetime_to_timestamp(user.last_login),
        datetime_to_timestamp(user.date_joined),
    ]
    if force or data != request.session.get(COOKIE_USER_DATA_KEY):
        request.session[COOKIE_USER_DATA_KEY] = data
        request.session[COOKIE_USER_DATA_TS_KEY] = time.time()

def cookie_get_user(request):
    # If it's been more than COOKIE_USER_REFRESH_TIME since the last time that
    # we set the user data stuff, then pull the user from the backend rather
    # than from the cookie.
    if COOKIE_USER_DATA_TS_KEY in request.session:
        diff = time.time() - request.session[COOKIE_USER_DATA_TS_KEY]
        if diff > COOKIE_USER_REFRESH_TIME:
            request._force_update_user = True
            return auth_get_user(request)

    user_id = request.session.get(auth.SESSION_KEY)
    if not user_id:
        return auth_get_user(request)

    data = request.session.get(COOKIE_USER_DATA_KEY)
    if not data:
        return auth_get_user(request)

    user = User()
    try:
        user.id = user_id
        user.username = data[0]
        user.first_name = data[1]
        user.last_name = data[2]
        user.email = data[3]
        user.password = data[4]
        user.is_staff = data[5]
        user.is_active = data[6]
        user.is_superuser = data[7]
        user.last_login = timestamp_to_datetime(data[8])
        user.date_joined = timestamp_to_datetime(data[9])
    except (IndexError, TypeError):
        return auth_get_user(request)
    return user


class SessionUserMiddleware(object):

    def __init__(self):
        """
        It makes me sad that ``auth.get_user`` can't be customized, but instead we
        have to monkeypatch it.
        """
        auth.get_user = cookie_get_user

    def process_request(self, request):
        if getattr(request, 'user', None) is None:
            return None

        # If the user isn't authenticated, then there's no way that the
        # "current user" could see any user attribute changes, since there is
        # no "current user"
        if not request.user.is_authenticated():
            # Set a property we can check later to see if the user logged in
            request._force_update_user = True
            return None
        
        # We create a function that's has a closure on the current request
        def post_user_save(sender, instance, **kwargs):
            # If the saved user is different from the current user, bail early
            if instance.id != request.user.id:
                return None
            # Otherwise, replace the request's user with the newly-saved user
            request.user = instance

        # And then we actually save a reference to it on the request
        request.post_user_save = post_user_save
        
        # Connect the signal
        post_save.connect(post_user_save, sender=User)

    def process_response(self, request, response):
        if getattr(request, 'user', None) is None:
            return response
        
        # If there's a post_user_save function on the request, disconnect it
        post_user_save = getattr(request, 'post_user_save', None)
        if post_user_save:
            post_save.disconnect(post_user_save, sender=User)
        
        # If the user is now logged in, make sure the cookie matches the data
        # that's stored on the request's user object
        if request.user.is_authenticated():
            # If we've explicitly set the force flag, make it True
            force = getattr(request, '_force_update_user', False)
            cookie_set_user(request, force=force)
        return response