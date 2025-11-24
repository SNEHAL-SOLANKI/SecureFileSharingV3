import os
from tkinter import SEL_FIRST
from typing import Self
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from cryptography.fernet import Fernet


# ==========================================================
# 📁 Helper: File Upload Path
# ==========================================================
def user_upload_path(instance, filename):
    """Generate a unique upload path for each user's uploaded file."""
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    return f"user_{instance.user.id}/{unique_name}"


# ==========================================================
# 📂 Folder Model  (UPDATED with password protection)
# ==========================================================
class Folder(models.Model):
    """
    📂 Represents user-created folders.
    Supports nested folders + password protection.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ============================
    # 🔐 NEW FIELDS
    # ============================
    password_hash = models.CharField(max_length=128, blank=True, null=True)
    is_protected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'parent', 'name')
        ordering = ['name']

    def __str__(self):
        return self.name

    # ============================
    # 🔐 Set Folder Password
    # ============================
    def set_password(self, raw_password):
        """
        Save password for folder.
        If raw_password empty → remove protection.
        """
        if raw_password:
            self.password_hash = make_password(raw_password)
            self.is_protected = True
        else:
            self.password_hash = None
            self.is_protected = False

        self.save(update_fields=['password_hash', 'is_protected'])

    # ============================
    # 🔑 Validate Folder Password
    # ============================
    def check_password(self, raw_password):
        """
        Validate folder password.
        If folder not protected → return True.
        """
        if not self.is_protected or not self.password_hash:
            return True
        return check_password(raw_password, self.password_hash)


# ==========================================================
# 🗂️ File Model
# ==========================================================
class File(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    folder = models.ForeignKey(
        Folder,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='files'
    )

    file = models.FileField(upload_to=user_upload_path)
    name = models.CharField(max_length=512)
    original_name = models.CharField(max_length=512, blank=True, null=True)

    # NEW FIELD
    display_name = models.CharField(max_length=255, blank=True)   # <-- Add this

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

# ==========================================================
# 🔐 Shared File Model
# ==========================================================
class SharedFile(models.Model):
    """
    🔐 Represents shared/public access to files.
    Supports temporary links, encryption, access limits.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shared_files'
    )

    file = models.FileField(upload_to='shared/')
    name = models.CharField(max_length=512)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    share_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    shared_token = models.CharField(max_length=100, blank=True, null=True)
    shared_expiry = models.DateTimeField(blank=True, null=True)

    share_count = models.PositiveIntegerField(default=0)
    max_share_limit = models.PositiveIntegerField(default=5)

    is_public = models.BooleanField(default=False)

    # Encryption flag
    is_encrypted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (Shared by {self.owner.username})"

    # ======================================================
    # 🔒 Encrypt/Decrypt
    # ======================================================
    def encrypt_file(self):
        """Encrypt stored file using Fernet."""
        file_path = self.file.path
        if not os.path.exists(file_path):
            return False

        fernet = Fernet(settings.FERNET_KEY.encode())

        with open(file_path, "rb") as f:
            data = f.read()

        encrypted = fernet.encrypt(data)

        with open(file_path, "wb") as f:
            f.write(encrypted)

        self.is_encrypted = True
        self.save(update_fields=['is_encrypted'])
        return True

    def decrypt_file(self):
        """Return decrypted file bytes."""
        file_path = self.file.path
        if not os.path.exists(file_path):
            return None

        fernet = Fernet(settings.FERNET_KEY.encode())

        with open(file_path, "rb") as f:
            encrypted = f.read()

        try:
            return fernet.decrypt(encrypted)
        except Exception:
            return None

    # ======================================================
    # 🕒 Temporary Link
    # ======================================================
    def generate_temp_link(self):
        """Generate 10-minute temporary share token."""
        self.shared_token = uuid.uuid4().hex
        self.shared_expiry = timezone.now() + timezone.timedelta(minutes=10)
        self.save(update_fields=['shared_token', 'shared_expiry'])
        return self.shared_token

    def is_link_valid(self):
        """Check whether token is still valid."""
        return bool(self.shared_expiry and timezone.now() < self.shared_expiry)

    def get_share_url(self, request):
        """Return public share URL."""
        from django.urls import reverse
        share_path = reverse('sharing:download_public', args=[self.share_key])
        return request.build_absolute_uri(share_path)
