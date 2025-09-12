from PiN.settings.base import *

MEDIA_ROOT = '/var/www/writable/media'
DATABASES['default']['NAME'] = '/var/www/writable/database/db.sqlite3'

DEBUG = True
ALLOWED_HOSTS = ["pin-dev.rich.ru.nl"]
