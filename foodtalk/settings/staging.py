from .base import *

MIDDLEWARE += ["whitenoise.middleware.WhiteNoiseMiddleware"]
ALLOWED_HOSTS = ["*"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
GDAL_LIBRARY_PATH = os.environ.get("GDAL_LIBRARY_PATH")
GEOS_LIBRARY_PATH = os.environ.get("GEOS_LIBRARY_PATH")
