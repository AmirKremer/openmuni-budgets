from openbudget.settings.base import *


SESSION_COOKIE_DOMAIN = 'obudget.dev'

ADMINS = (
    ('', ''),
    ('', ''),
)

MANAGERS = ADMINS

MIDDLEWARE_CLASSES += (
    'openbudget.api.middleware.XsSharing',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_pdb.middleware.PdbMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
    'django_pdb',
)

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

SENTRY_DSN = ''

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

DEVSTRAP = {
    'FIXTURES': (
        'dev/sites',
        'israel/domains',
        'israel/divisions',
        'israel/entities',
        'locale/he/strings',
        'dev/interactions',
        'dev/sources'
    ),
    'TESTS': (
        'accounts',
        'api',
        'budgets',
        'commons',
        'contexts',
        'entities',
        'interactions',
        'international',
        'pages',
        'sources',
        'taxonomies',
        'transport'
    )
}
