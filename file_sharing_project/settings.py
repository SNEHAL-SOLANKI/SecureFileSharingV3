import os
from pathlib import Path
from cryptography.fernet import Fernet


BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_TITLE = "Secure File Sharing System"
PROJECT_SUBTITLE = "Share your files securely and easily"



# ==============================
# 🔐 SECURITY SETTINGS
# ==============================
SECRET_KEY = 'django-insecure-change-this-for-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

# ==============================
# 🧩 INSTALLED APPS
# ==============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 🔹 Custom Apps
    'user_app',
    'sharing_app',
]

# ✅ Custom User Model
AUTH_USER_MODEL = 'user_app.CustomUser'

# ==============================
# ⚙️ MIDDLEWARE
# ==============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ==============================
# 🌐 URLS & WSGI
# ==============================
ROOT_URLCONF = 'file_sharing_project.urls'
WSGI_APPLICATION = 'file_sharing_project.wsgi.application'
ASGI_APPLICATION = 'file_sharing_project.asgi.application'

# ==============================
# 🎨 TEMPLATES CONFIGURATION
# ==============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# ==============================
# 🗄️ DATABASE
# ==============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==============================
# 🔑 PASSWORD VALIDATION
# ==============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================
# 🌍 INTERNATIONALIZATION
# ==============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ==============================
# 🖼️ STATIC & MEDIA CONFIG
# ==============================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'



# ✅ Secure uploaded files (protected folder)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'protected_media'

# ==============================
# 📧 EMAIL CONFIGURATION (for OTP)
# ==============================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '24034211120@gnu.ac.in'
EMAIL_HOST_PASSWORD = 'bcwmwryqxizjigmp'

# ==============================
# 🔁 LOGIN / LOGOUT REDIRECTS
# ==============================
LOGIN_URL = '/user/login/'
LOGIN_REDIRECT_URL = '/sharing/dashboard/'
LOGOUT_REDIRECT_URL = '/user/login/'

# ==============================
# ⚙️ DEFAULT FIELD TYPE
# ==============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================
# 🧠 FILE ENCRYPTION SETTINGS
# ==============================
# Fernet (AES-128 + HMAC) Encryption Key
FERNET_KEY = os.environ.get('FERNET_KEY')

if not FERNET_KEY:
    # Development fallback (auto-generate key if not found)
    FERNET_KEY = Fernet.generate_key().decode()
    print("⚠️ WARNING: No FERNET_KEY found. Generated a temporary key.")
    print("👉 Please set a permanent key in your system environment for production use.")
