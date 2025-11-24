# ==========================================================
# 📄 forms.py — Secure File Sharing (Final Correct Version)
# ==========================================================
from django import forms
from .models import SharedFile
from django.core.exceptions import ValidationError
import os


# ==========================================================
# 📁 Allowed File Configuration
# ==========================================================
ALLOWED_EXT = [
    '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif',
    '.doc', '.docx', '.xlsx', '.csv', '.mp4', '.mp3'
]
MAX_MB = 25


# ==========================================================
# 📤 Upload Form (ModelForm)
# ==========================================================
class UploadForm(forms.ModelForm):
    """
    Handles validation for uploaded files.
    """

    # Custom display name (optional)
    display_name = forms.CharField(
        max_length=255,
        required=False,
        label="File name (optional)"
    )

    class Meta:
        model = SharedFile
        fields = ['file', 'is_public', 'display_name']

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ALLOWED_EXT:
                raise ValidationError("⚠️ File type not allowed.")

            if f.size > MAX_MB * 1024 * 1024:
                raise ValidationError(f"⚠️ File too large. Max {MAX_MB} MB allowed.")

        return f


# ==========================================================
# 🔁 Rename File Form
# ==========================================================
class RenameFileForm(forms.Form):
    """
    Only takes new file name.
    """

    display_name = forms.CharField(
        max_length=255,
        required=True,
        label="New file name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new file name'
        })
    )


# ==========================================================
# 📝 Create New Text File Form
# ==========================================================
class NewFileForm(forms.Form):
    filename = forms.CharField(
        max_length=255,
        initial='untitled.txt',
        label='Filename',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter filename (e.g., notes.txt)'
        })
    )
    content = forms.CharField(
        label='Content',
        widget=forms.Textarea(attrs={
            'rows': 10,
            'class': 'form-control',
            'placeholder': 'Write your text content here...'
        })
    )


# ==========================================================
# 🔧 FOLDER OPERATIONS FORMS
# ==========================================================
class RenameFolderForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label="New folder name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new folder name'
        })
    )


class FolderPasswordForm(forms.Form):
    password = forms.CharField(
        max_length=128,
        required=False,
        label="Password (leave empty to remove protection)",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password or leave empty to remove'
        })
    )


class ConfirmDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        label="I understand and want to permanently delete this folder"
    )
