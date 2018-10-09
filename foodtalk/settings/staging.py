from .base import *

MIDDLEWARE += ['whitenoise.middleware.WhiteNoiseMiddleware']
ALLOWED_HOSTS = ['*']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
GDAL_LIBRARY_PATH = os.getenv('GDAL_LIBRARY_PATH')