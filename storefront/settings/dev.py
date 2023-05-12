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
        "HOST": "mysql",
        "USER": "root",
        "PASSWORD": "MyPassword",
        "OPTIONS": {
            "init_command": "SET GLOBAL max_connections = 100000",
        },
    }
}

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # "silk.middleware.SilkyMiddleware",
]

CELERY_BROKER_URL = "redis://redis:6379/1"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/2",
        "TIMEOUT": 10 * 60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

EMAIL_HOST = "smtp4dev"
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_PORT = 2525
DEFAULT_FROM_EMAIL = "from@omar.com"

DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: True}
