import os
from .common import *
import dj_database_url
import requests


DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ["omarbuy-prod.herokuapp.com"]

DATABASES = {"default": dj_database_url.config()}

REDIS_URL = os.environ["REDISCLOUD_URL"]

CELERY_BROKER_URL = REDIS_URL

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 10 * 60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

response = requests.get(
    "https://mailtrap.io/api/v1/inboxes.json?api_token=<MAILTRAP_API_TOKEN>"
)
credentials = response.json()[0]

EMAIL_HOST = credentials["domain"]
EMAIL_HOST_USER = credentials["username"]
EMAIL_HOST_PASSWORD = credentials["password"]
EMAIL_PORT = credentials["smtp_ports"][0]
EMAIL_USE_TLS = True
