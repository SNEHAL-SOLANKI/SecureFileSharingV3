# ==========================================================
# 📄 forms.py — Secure File Sharing (Final Complete Version)
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
    """Handles validation for uploaded files."""
    class Meta:
        model = SharedFile
        fields = ['file', 'name', 'is_public']

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
# 📝 New Text File Creation Form
# ==========================================================
class NewFileForm(forms.Form):
    """Simple form for creating text files manually."""
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
