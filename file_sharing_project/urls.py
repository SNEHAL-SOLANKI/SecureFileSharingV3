from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from sharing_app import views as sharing_views

urlpatterns = [
    # =====================================================
    # ⚙️ ADMIN PANEL
    # =====================================================
    path('admin/', admin.site.urls),

    # =====================================================
    # 🏠 HOME PAGE (Public Landing)
    # =====================================================
    path('', sharing_views.home, name='home'),

    # =====================================================
    # 👤 USER AUTH MODULE (Login / Register / OTP / Profile)
    # =====================================================
    path('user/', include(('user_app.urls', 'user'), namespace='user')),  # ✅ Correct namespace

    # =====================================================
    # 📁 FILE SHARING MODULE (Dashboard / Upload / Download)
    # =====================================================
    path('sharing/', include(('sharing_app.urls', 'sharing'), namespace='sharing')),
]

# =====================================================
# 🖼️ MEDIA & STATIC FILES (Development Only)
# =====================================================
if settings.DEBUG:
    # Serve uploaded user files (MEDIA)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Serve static assets (CSS, JS, Images)
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
