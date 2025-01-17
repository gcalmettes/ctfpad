import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('CTFPAD_SECRET_KEY') or 'ow#8y081ih3nunjqh)u^ug)ln_$xri3-upt^e)7h)&l$05-7tf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') or False


CTFPAD_HOSTNAME = os.getenv("CTFPAD_HOSTNAME") or "localhost"
CTFPAD_PORT = os.getenv("CTFPAD_PORT") or "8000"
CTFPAD_USE_SSL = os.getenv("CTFPAD_USE_SSL")=="1" or False

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# SECURITY WARNING: harden for production!
ALLOWED_HOSTS = [CTFPAD_HOSTNAME, "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1"]
if CTFPAD_USE_SSL:
    CTFPAD_SSL_URL = f"https://{CTFPAD_HOSTNAME}"
    if CTFPAD_PORT != "443":
        CTFPAD_SSL_URL += f":{CTFPAD_PORT}"
    CSRF_TRUSTED_ORIGINS.append(CTFPAD_SSL_URL)
else:
    CSRF_TRUSTED_ORIGINS.append(f"http://{CTFPAD_HOSTNAME}:{CTFPAD_PORT}")

CSRF_COOKIE_NAME="ctfpad-csrf"
SESSION_COOKIE_NAME="ctfpad-session"

# Application definition

INSTALLED_APPS = [
#    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    'model_utils',
    'ctfpad',
]

SITE_ID = 1


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ctftools.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ctftools.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME':     os.getenv("CTFPAD_DB_NAME") or 'ctfpad',
        'USER':     os.getenv("CTFPAD_DB_USER") or 'ctfpad',
        'PASSWORD': os.getenv("CTFPAD_DB_PASSWORD"),
        'HOST':     os.getenv("CTFPAD_DB_HOST") or 'localhost',
        'PORT':     os.getenv("CTFPAD_DB_PORT") or '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_URL   = "/uploads/"
MEDIA_ROOT  = BASE_DIR / "uploads/"

CTF_CHALLENGE_FILE_URL = "/uploads/files/"
CTF_CHALLENGE_FILE_PATH = "files/"
CTF_CHALLENGE_FILE_ROOT = MEDIA_ROOT / CTF_CHALLENGE_FILE_PATH

USERS_FILE_URL  = "/uploads/media/"
USERS_FILE_PATH = "media/"
USERS_FILE_ROOT = MEDIA_ROOT / USERS_FILE_PATH

CTFPAD_URL = os.getenv("CTFPAD_URL") or 'http://localhost:8000'
HEDGEDOC_URL = os.getenv("HEDGEDOC_URL") or 'http://localhost:3000'
USE_INTERNAL_HEDGEDOC = os.getenv("USE_INTERNAL_HEDGEDOC") in ["1", "True", "true", True]
EXCALIDRAW_URL = os.getenv("EXCALIDRAW_URL") or 'http://localhost:5010'

CTFTIME_URL = "https://ctftime.org"
CTFTIME_API_EVENTS_URL = "https://ctftime.org/api/v1/events/"
CTFTIME_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0"

LOGIN_REDIRECT_URL = "ctfpad:dashboard"
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
CHALLENGE_FILE_MAX_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

FIRST_DAY_OF_WEEK = 1
SHORT_DATE_FORMAT = 'Y-m-d'
SHORT_DATETIME_FORMAT = 'Y-m-d P'

CTFPAD_DEFAULT_CTF_LOGO = "blank-ctf.png"
CTFPAD_ACCEPTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".gif", ".bmp")

# EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
# EMAIL_FILE_PATH = MEDIA_ROOT / "email_sent"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("CTFPAD_EMAIL_SERVER_HOST") or None
EMAIL_PORT = os.getenv("CTFPAD_EMAIL_SERVER_PORT") or 587
EMAIL_USE_TLS = os.getenv("CTFPAD_EMAIL_SERVER_USE_TLS") or True
EMAIL_HOST_USER = os.getenv("CTFPAD_EMAIL_USERNAME") or None
EMAIL_HOST_PASSWORD = os.getenv("CTFPAD_EMAIL_PASSWORD") or None
EMAIL_SUBJECT_PREFIX = "[CTFPad] "


# Jistsi integration

JITSI_URL = "https://meet.jit.si"


# Discord integration

DISCORD_WEBHOOK_URL = os.getenv("CTFPAD_DISCORD_WEBHOOK_URL") or None
DISCORD_BOT_NAME = os.getenv("CTFPAD_DISCORD_BOT_NAME") or "SpiderBot"

# Excalidraw integration

EXCALIDRAW_ROOM_ID_PATTERN = '[0-9a-f]{20}'
EXCALIDRAW_ROOM_KEY_PATTERN = '[a-zA-Z0-9_-]{22}'
