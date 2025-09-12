from PiN.settings.base import *

MEDIA_ROOT = '/var/www/writable/media'
DATABASES['default']['NAME'] = '/var/www/writable/database/db.sqlite3'

DEBUG = False
ALLOWED_HOSTS = ["pin.rich.ru.nl"]