

AUTH_USER_MODEL = 'accounts.User'

import os
from pathlib import Path
from datetime import timedelta

import cloudinary
import cloudinary
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vrt92(al=o#4@d72lzk0v5x@#+t-ql8#gdcf_x2&mkm3n4qvrl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'skilline-backend.onrender.com',
    'skilline-gamma.vercel.app',
    '.onrender.com',                   # ← wildcard for render subdomains (helps)
    '.vercel.app',                     # ← optional but useful
]


# Optional – during heavy debugging you can temporarily allow everything
# (remove this in production!)
# CORS_ALLOW_ALL_ORIGINS = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'cloudinary_storage',
    'cloudinary',
    'accounts',
    'corsheaders',
    'courses',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ────────────────────────────────────────────────
# Simple JWT configuration
# ────────────────────────────────────────────────

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ────────────────────────────────────────────────
# drf-spectacular (OpenAPI / Swagger)
# ────────────────────────────────────────────────

SPECTACULAR_SETTINGS = {
    'TITLE': 'Educator API',
    'DESCRIPTION': 'API for Educator platform – student, instructor & admin portals',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'SCHEMA_PATH_PREFIX': '/api',
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'REDOC_UI_SETTINGS': {
        'hideHostname': False,
    },

    # These help suppress warnings
    'WARN_UNRESOLVED_SERIALIZER': False,
    'WARN_SCHEMA_UNRESOLVABLE': False,

    # Most important: completely ignore groups & user_permissions in schema
    'SERVE_PUBLIC': True,
    'COMPONENT_SEPARATOR': '@',
    'EXCLUDE_ANNOTATIONS': True,
    'SCHEMA_COERCE_PATH_PK_SUFFIX': True,
    'COMPONENT_NO_NAME': True,

    # Exclude the problematic M2M fields
    'EXCLUDE_FIELDS_FROM_SCHEMA': {
        'accounts.User': ['groups', 'user_permissions'],
    },

    # NEW: Tell spectacular not to introspect these fields at all
    'FIELD_SCHEMA_PROCESSORS': [
        lambda field, direction: None if field.field_name in ['groups', 'user_permissions'] else field,
    ],
}
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://localhost:5173",         
    "https://skilline-gamma.vercel.app",
]
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://localhost:5173',          # in case Vite uses HTTPS proxy
    'https://skilline-gamma.vercel.app',
    'https://skilline-backend.onrender.com',  # optional but good for Swagger/Postman
]

CORS_ALLOW_ALL_ORIGINS = False  # ← turn off wildcard

CORS_ALLOW_CREDENTIALS = True  
ROOT_URLCONF = 'educator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'educator.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if os.getenv('RENDER') == 'true': 
    import dj_database_url
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL:
        DATABASES['default'] = dj_database_url.parse(
            DATABASE_URL.replace('postgres://', 'postgresql://'),
            conn_max_age=600,
        )
        print("ZEMPAA ON RENDER → USING POSTGRESQL")
    else:
        print("Render detected but no DATABASE_URL!")
else:
    print("LOCAL DEVELOPMENT → USING SQLITE (NO INTERNET NEEDED)")

print(f"Database engine: {DATABASES['default']['ENGINE']}")

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cloudinary config
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET'),
    secure = True
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Optional: Make uploads public by default
CLOUDINARY_STORAGE = {
    'PREFIX': 'skilline/',          
    'TAG': 'skilline_app',          
}

if not os.getenv('DATABASE_URL'):  
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'