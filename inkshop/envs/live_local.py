from .live import *

# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
DEFAULT_FILE_STORAGE = 'utils.storage.InkshopFileStorage'
COMPRESS_STORAGE = DEFAULT_FILE_STORAGE
STATICFILES_STORAGE = DEFAULT_FILE_STORAGE
