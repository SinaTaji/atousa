import os
from pathlib import Path
from decouple import config



BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
CSRF_TRUSTED_ORIGINS = []
LOGIN_URL = '/user/login'
DEBUG = config('DEBUG', cast=bool)
MERCHANT_ID = config('MERCHANT_ID')
CALLBACK_URL = config('CALLBACK_URL')
ALLOWED_HOSTS = ['*', 'atousa.liara.run']
INTERNAL_IPS = [
    "127.0.0.1",
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # in app ==========
    'home.apps.HomeConfig',
    'authentication.apps.AuthenticationConfig',
    'products.apps.ProductsConfig',
    'orders.apps.OrdersConfig',
    'site_settings.apps.SiteSettingsConfig',
    'account.apps.AccountConfig',
    'aboutus_contactus.apps.AboutusContactusConfig',
    'article.apps.ArticleConfig',
    'admin_panel',
    # out app =========
    'django_render_partial',
    'debug_toolbar',
    'django_filters',
    'django_jalali',
    'django.contrib.sitemaps',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bache_poosh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products.context_processors.global_categories',
                'orders.context_processors.cart_context',
                'site_settings.context_processors.footer',
                'aboutus_contactus.context_processors.wishlist_count',
                'aboutus_contactus.context_processors.messages_count',
                'aboutus_contactus.context_processors.partner',
                'admin_panel.context_processors.unseen_notifications_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'bache_poosh.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/mnt/atousa-disk/db.sqlite3',
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

AUTH_USER_MODEL = 'account.User'
# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True

NTFY_TOPIC = config('NTFY_TOPIC')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = '/mnt/atousa-disk/static'
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

MEDIA_ROOT = '/mnt/atousa-disk/media'
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://:fcnzHtC1G2GIvgctCculdp4d@atousa-redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
