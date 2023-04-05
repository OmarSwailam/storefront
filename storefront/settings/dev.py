from .common import *

DEBUG = True

SECRET_KEY = "django-insecure-x_4+_ok4!5v3&@$hwx=auhl=+7(6%s7(j%4dp5)=bg5n%+l^x_"

INTERNAL_IPS = [
    "127.0.0.1",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "storefront",
        "HOST": "localhost",
        "USER": "root",
        "PASSWORD": "mysql",
        "OPTIONS": {
            "init_command": "SET GLOBAL max_connections = 100000",
        },
    }
}

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # "silk.middleware.SilkyMiddleware",
]
