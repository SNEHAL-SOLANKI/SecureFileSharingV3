from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from random import randint

from .forms import RegisterForm, OTPForm
from .models import CustomUser


# 🟢 User Registration View
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()
            messages.success(request, "✅ Registration successful! You can now log in.")
            return redirect('user:login')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'user_app/register.html', {'form': form})


# 🟢 Login View (email-based + OTP send)
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "❌ Invalid email or password.")
            return render(request, 'user_app/login.html')

        if user.check_password(password):
            otp = str(randint(100000, 999999))
            user.set_otp(otp)

            # ✅ Send OTP email
            send_mail(
                "Your Secure File Sharing System OTP",
                f"Your OTP is {otp}. It expires in 10 minutes.",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            request.session['otp_user_id'] = user.id
            messages.info(request, "📩 OTP sent to your registered email.")
            return redirect('user:verify_otp')
        else:
            messages.error(request, "❌ Invalid email or password.")
    return render(request, 'user_app/login.html')


# 🟢 OTP Verification View
def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, "⚠️ Session expired. Please login again.")
        return redirect('user:login')

    user = CustomUser.objects.get(id=user_id)
    form = OTPForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        otp = form.cleaned_data['otp']
        if user.verify_otp(otp):
            user.otp_code = None
            user.save()
            login(request, user)

            # ✅ Clean session
            if 'otp_user_id' in request.session:
                del request.session['otp_user_id']

            messages.success(request, "✅ Login successful!")

            # 🔧 FIX: Redirect to dashboard (no folder_id needed)
            return redirect('sharing:dashboard_root')

        else:
            messages.error(request, "❌ Invalid or expired OTP.")

    return render(request, 'user_app/otp_verify.html', {'form': form})


# 🟢 Profile Page (Only for logged-in users)
@login_required
def profile(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        request.user.username = username
        request.user.email = email
        request.user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('user:profile')

    return render(request, 'user_app/profile.html')

# 🟢 Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('user:login')
