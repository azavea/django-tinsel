DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

MIDDLEWARE_CLASSES = ()

SECRET_KEY = 'NO_SECRET_KEY'

INSTALLED_APPS = ('django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django_tinsel_tests',)

DEBUG = True
