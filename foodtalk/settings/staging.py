from .base import *

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
ALLOWED_HOSTS = ['*']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
