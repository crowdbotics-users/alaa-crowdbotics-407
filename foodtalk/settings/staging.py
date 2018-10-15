from .base import *

MIDDLEWARE += ["whitenoise.middleware.WhiteNoiseMiddleware"]
ALLOWED_HOSTS = ["*"]
AWS_LOCATION = 'static'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'core.storage_backends.MediaStorage'
STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
