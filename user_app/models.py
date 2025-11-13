from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta




# ==========================
# 🧑 Custom User Model
# ==========================
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    def set_otp(self, otp):
        # ✅ timezone.now() use kiya hai datetime.now() ke jagah
        self.otp_code = otp
        self.otp_expiry = timezone.now() + timedelta(minutes=10)
        self.save()

    def verify_otp(self, otp):
        # ✅ timezone-safe comparison
        if self.otp_code != otp or not self.otp_expiry:
            return False

        otp_expiry = self.otp_expiry
        if timezone.is_naive(otp_expiry):
            otp_expiry = timezone.make_aware(otp_expiry)

        return otp_expiry > timezone.now()

    def __str__(self):
        return self.username


# ==========================
# 📩 Email OTP Model
# ==========================
class EmailOTP(models.Model):
    user = models.ForeignKey('user_app.CustomUser', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
