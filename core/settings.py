import os

from environs import Env
from pathlib import Path


env = Env()
env.read_env('./envs/.env')


BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = env.str("SECRET_KEY")


DEBUG = env.bool("DEBUG", default=False)

# ALLOWED_HOSTS = ["*"]
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS=env.list('CSRF_TRUSTED_ORIGINS')
CORS_ALLOWED_ORIGINS=env.list('CORS_ALLOWED_ORIGINS')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "corsheaders",
    'rest_framework',
    'click_up',
    'payme',
    'paytechuz.integrations.django',

    'product',
    'user',
    'shared',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.mysql',  # Connection pool
        'NAME': env.str("MYSQL_DATABASE"),
        'USER': env.str("MYSQL_USER"),
        'PASSWORD': env.str("MYSQL_PASSWORD"),
        'HOST': env.str("MYSQL_HOST"),
        'PORT': env.str("MYSQL_PORT"),
        'POOL_OPTIONS': {
            'POOL_SIZE': 20,        # Doimiy 20 ta ulanish
            'MAX_OVERFLOW': 30,     # Qo'shimcha 30 ta (jami 50)
            'RECYCLE': 300,         # 5 daqiqada yangilanadi
            'PRE_PING': True,       # "Server has gone away" oldini oladi
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



CLICK_SERVICE_ID = env.str("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = env.str("CLICK_MERCHANT_ID")
CLICK_SECRET_KEY = env.str("CLICK_SECRET_KEY")
CLICK_ACCOUNT_MODEL = env.str("CLICK_ACCOUNT_MODEL")
CLICK_AMOUNT_FIELD = env.str("CLICK_AMOUNT_FIELD")


PAYTECHUZ = {
    'PAYME': {
        'PAYME_ID': env.str("PAYME_ID"),
        'PAYME_KEY': env.str("PAYME_KEY"),
        'ACCOUNT_MODEL': env.str("PAYME_ACCOUNT_MODEL"),
        'ACCOUNT_FIELD': env.str("PAYME_ACCOUNT_FIELD"),
        'AMOUNT_FIELD': env.str("PAYME_AMOUNT_FIELD"),
        'ONE_TIME_PAYMENT': env.bool("PAYME_ONE_TIME_PAYMENT"),
        'IS_TEST_MODE': False,
    },
}

PAYTECH_LICENSE_API_KEY = env.str("PAYTECH_LICENSE_API_KEY")

