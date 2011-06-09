===================
django-session-user
===================

This app is a simple piece of middleware that can be added to your Django
project which will store and retrieve the logged-in user's information from
the session.


Installation
------------

Add the sesionuser middleware line to your MIDDLEWARE_CLASSES after the
AuthenticationMiddleware:

    MIDDLEWARE_CLASSES = (
        # ...
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'sessionuser.middleware.UserSessionMiddleware',
        # ...
    )


Why do this?
------------

Your server is already fetching the contents of the user's session, which
already contains the user's identity.  Why not store the rest of the user
class's data along with it?  That way you don't have to make a request to the
database for every authenticated web request.

Additionally if you are using a cookie-based session backend (like
django-cookie-sessions, written by yours truly) you can have other systems,
maybe even non-Django systems, which read the cookie and know more information
about the user.


Customizable Settings
---------------------

COOKIE_USER_REFRESH_TIME [= 14400]:

    The number of seconds that need to elapse before the user is fetched from
    the database instead of trusting the cookie.  This is useful for making
    sure that even if the user's properties are changed in the database,
    the user's cookie will still be updated.