from pathlib import Path
import os
from environ import Env
import redis
from datetime import timedelta
from corsheaders.defaults import default_headers
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

REDIS_OBJ = redis.Redis()

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
Env().read_env(os.path.join(BASE_DIR,
".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = True
#env("DEBUG") == "1"

ALLOWED_HOSTS = [
    "*"
]

INSTALLED_APPS = [
    "jazzmin",
    # "material",
    # "material.admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework_simplejwt",
    "drf_yasg",
    "rest_framework",
    "parler",
    "rosetta",
    "mptt",
    "django_user_agents",
    "django_celery_results",
    "django_summernote",
   
    "django_cleanup.apps.CleanupConfig",
    "api.apps.ApiConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "api.middlewares.LanguageHeaderMiddleware"
]

ROOT_URLCONF = "whc.urls"

TEMPLATES = [

    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates")
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "whc.wsgi.application"

if DEBUG:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    	}
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASS"),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]



REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (
 
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_PERMISSION_CLASSES': (
         'rest_framework.permissions.AllowAny',
   )
}
AUTH_USER_MODEL = "api.User"

LANGUAGE_CODE = "en"

LANGS = [
    {
        "code": "en",
        "title": "English"
    },
    {
        "code": "ru",
        "title": "Русский"
    },
    {
        "code": "uz",
        "title": "O'zbekcha"
    },
    {
        "code": "es",
        "title": "Española"
    },
    {
        "code": "ar",
        "title": "عربى"
    },
    {
        "code": "it",
        "title": "Italiana"
    },
    {
        "code": "de",
        "title": "Deutsch"
    },
    # {
    #     "code": "ch",
    #     "title": "English"
    # },
    {
        "code": "pl",
        "title": "Polskie"
    },
    {
        "code": "et",
        "title": "አማርኛ"
    },
    {
        "code": "nl",
        "title": "Dutch"
    },
    {
        "code": "he",
        "title": "עִברִית"
    },
    {
        "code": "ko",
        "title": "한국인"
    },
    {
        "code": "cs",
        "title": "Čeština"
    },
    {
        "code": "ro",
        "title": "Română"
    },
    {
        "code": "fr",
        "title": "Français"
    },
    {
        "code": "ja",
        "title": "日本"
    },
    # {
    #     "code": "kz",
    #     "title": "Қазақ тілі"
    # },
    # {
    #     "code": "cn",
    #     "title": "中国人"
    # }
]

PARLER_LANGUAGES = {
    None: tuple(map(lambda x: {"code": x["code"]}, LANGS)),
    "default": {
        "fallbacks": [LANGUAGE_CODE],
        "hide_untranslated": False,
    }
}

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale")
]

LANGUAGES = [
    *list(map(lambda x: (x["code"], x["title"]), LANGS))
]

COUNTRIES_TO_LANGS = {
    "en": ["us", "gb", "au", "nz", "ca", "vi"],
    "ru": ["ru", "by", "kz", "kg"],
    "uz": ["uz"],
    "es": ["ar", "bo", "cl", "co", "cr", "cu", "do", "ec", "sv", "gt", "hn", "mx", "ni", "pa", "py", "pe", "uy", "ve"],
    "ar": ["eg", "dz", "sd", "ss", "iq", "ma", "sa", "ye", "sy", "tn", "so", "td", "ae", "jo", "er", "ly", "lb", "ps", "om", "mr", "kw", "qa", "bh", "tz", "dj", "km"],
    "it": ["it", "sm", "va"],
    "de": ["de", "be", "at", "ch", "lu", "li"],
    "pl": ["at", "pl", "cz", "fi"],
    "et": ["et"],
    "nl": ["nl", "an", "sr"],
    "ko": ["kr", "kp"],
    "cs": [],
    "ro": ["ro"],
    "fr": ["fr", "cd", "cg", "cm", "ci", "mg", "ht"],
    "ja": ["ja", "gu"],
    # "kz": [],
    # "cn": []
}

ROSETTA_ENABLE_TRANSLATION_SUGGESTIONS = True
ROSETTA_AUTO_COMPILE = True
ROSETTA_SHOW_AT_ADMIN_PANEL = True

TIME_ZONE = "Asia/Tashkent"

USE_I18N = True

USE_TZ = True

BACKEND_URL = "https://whitebridge.site"
# BACKEND_URL = "http://localhost:8000"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles")
]

SUMMERNOTE_CONFIG = {
    "iframe": True,
}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
#         "LOCATION": "127.0.0.1:11211",
#     }
# }

USER_AGENTS_CACHE = "default"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    # "ALGORITHM": "RS512"
}

SWAGGER_SETTINGS = {
   "USE_SESSION_AUTH": False
}

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    "accept-country",
]

# sentry_sdk.init(
#     dsn=env("SENTRY_DSN"),
#     integrations=[DjangoIntegration()],
#     traces_sample_rate=1.0,
#     send_default_pii=True
# )


SITE_FRONT_END_URL = "https://whitebridge.club"

GOOGLE_OAUTH2_CLIENT_ID = env("GOOGLE_OAUTH2_CLIENT_ID")
GOOGLE_OAUTH2_CLIENT_SECRET = env("GOOGLE_OAUTH2_CLIENT_SECRET")

CELERY_BROKER_URL = "redis://localhost:6379/0"

CELERY_RESULT_BACKEND = "django-db"


EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = int(env("EMAIL_PORT"))
EMAIL_USE_TLS = env("EMAIL_USE_TLS") == "1"
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

from .jazzmin_settings import *
