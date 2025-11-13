import os
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from cryptography.fernet import Fernet

# ==========================================================
# 📁 Helper: File Upload Path
# ==========================================================
def user_upload_path(instance, filename):
    """Generate a unique upload path for each user's uploaded file."""
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    return f"user_{instance.user.id}/{unique_name}"


# ==========================================================
# 📂 Folder Model
# ==========================================================
class Folder(models.Model):
    """
    📂 Represents user-created folders.
    Supports nested folders (via 'parent' self-reference).
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
    updated_at = models.DateTimeField(auto_now=True)  # 🕒 Last modified timestamp

    class Meta:
        unique_together = ('user', 'parent', 'name')  # Prevent duplicate folder names
        ordering = ['name']

    def __str__(self):
        return self.name


# ==========================================================
# 🗂️ File Model
# ==========================================================
class File(models.Model):
    """
    🗂️ Stores uploaded files belonging to users and folders.
    Supports soft deletion, encryption, and original filename tracking.
    """
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
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # 🕒 Update on every save
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_name or self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        """Auto-fill 'original_name' on first save."""
        if not self.original_name:
            self.original_name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)


# ==========================================================
# 🔐 Shared File Model
# ==========================================================
class SharedFile(models.Model):
    """
    🔐 Represents shared or public access to files.
    Supports encryption, temporary links, and access limits.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shared_files'
    )
    file = models.FileField(upload_to='shared/')
    name = models.CharField(max_length=512)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  # 🕒 Update on changes

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
    # 🔒 Encryption / Decryption Methods
    # ======================================================
    def encrypt_file(self):
        """Encrypt the stored file using Fernet (AES-128 + HMAC)."""
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
        """Decrypt and return file bytes for download."""
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
    # 🕒 Temporary Share Token
    # ======================================================
    def generate_temp_link(self):
        """Generate a 10-minute valid temporary share token."""
        self.shared_token = uuid.uuid4().hex
        self.shared_expiry = timezone.now() + timezone.timedelta(minutes=10)
        self.save(update_fields=['shared_token', 'shared_expiry'])
        return self.shared_token

    def is_link_valid(self):
        """Check whether the temporary share link is still valid."""
        return bool(self.shared_expiry and timezone.now() < self.shared_expiry)

    def get_share_url(self, request):
        """Return the full public share URL."""
        from django.urls import reverse
        share_path = reverse('sharing:download_public', args=[self.share_key])
        return request.build_absolute_uri(share_path)
