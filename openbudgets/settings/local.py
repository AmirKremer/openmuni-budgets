# Uncomment if you are overriding any settings that are defined in settings
from openbudgets.settings import *


######################################################################
##                                                                  ##
## RENAME THIS FILE TO local.py to provide your own local overrides ##
##                                                                  ##
######################################################################

EMAIL_HOST_USER = 'hello@prjts.com'

EMAIL_HOST_PASSWORD = 'wer74qPAL'

#ADMINS = (
#    ('', ''),
#)

# Uncomment MIDDLEWARE_CLASSES, INSTALLED_APPS, INTERNAL_IPS, and
# DEBUG_TOOLBAR_CONFIG for debugging tools.
#
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_pdb.middleware.PdbMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
    'django_pdb',
)

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# Uncomment to enable caching during development
#CACHES = {
#    'default': {
#        'BACKEND': 'redis_cache.RedisCache',
#        'LOCATION': REDIS['HOST'] + ':' + str(REDIS['PORT']),
#        'OPTIONS': {
#            'DB': REDIS['DB'],
#            'PARSER_CLASS': 'redis.connection.HiredisParser'
#        },
#    },
#}

# Uncomment to enable redis as a celery backend in development
# You'll also need some extra dependencies:
# pip install -r requirements/extended.txt
#BROKER_URL = REDIS_URL
#
#CELERY_RESULT_BACKEND = BROKER_URL
#
#CELERY_RESULT_DBURI = ''
