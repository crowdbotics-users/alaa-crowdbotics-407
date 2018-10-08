from .base import *

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
ALLOWED_HOSTS = ['*']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
