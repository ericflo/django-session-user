from setuptools import setup, find_packages

setup(
    name='django-session-user',
    version=__import__('sessionuser').__version__,
    description='Stores the user\'s information in the session, reucing database queries by a lot.',
    long_description=open('README.txt').read(),
    author='Eric Florenzano',
    author_email='floguy@gmail.com',
    url='https://github.com/ericflo/django-session-user',
    packages=['sessionuser'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)