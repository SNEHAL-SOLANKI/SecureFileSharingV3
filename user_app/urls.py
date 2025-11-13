from django.urls import path
from . import views

# =====================================================
# ✅ App namespace
# Important: templates use {% url 'user_app:login' %} etc.
# =====================================================
app_name = 'user_app'

urlpatterns = [
    # =================================================
    # 🧑‍💻 Authentication Routes
    # =================================================
    path('register/', views.register_view, name='register'),           # User Registration
    path('login/', views.login_view, name='login'),                    # User Login
    path('logout/', views.logout_view, name='logout'),                 # User Logout

    # =================================================
    # 🔐 OTP Verification (for secure login/registration)
    # =================================================
    path('otp/', views.verify_otp_view, name='otp'),                   # Short route
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),     # Alternate route (for form action)

    # =================================================
    # 👤 User Profile
    # =================================================
    path('profile/', views.profile, name='profile'),                   # User Profile Page
]
