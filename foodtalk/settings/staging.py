from .base import *

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
ALLOWED_HOSTS = ['*']
