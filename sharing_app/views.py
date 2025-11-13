# ==========================================================
# 📁 Secure File Sharing - views.py (✅ Final Updated Version)
# ==========================================================
import os
import uuid
import mimetypes
from datetime import timedelta
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse, Http404, HttpResponseForbidden, FileResponse
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

from .models import SharedFile, Folder, File


# ==========================================================
# 🏠 Public Home Page
# ==========================================================
def home(request):
    """Landing (public) home page."""
    return render(request, 'home.html')


# ==========================================================
# 🚪 Logout View
# ==========================================================
@login_required
def user_logout(request):
    """Logs out the user and redirects to login page."""
    logout(request)
    messages.info(request, "👋 You’ve been logged out successfully.")
    return redirect('user:login')


# ==========================================================
# 📊 Dashboard (Root + Folder)
# ==========================================================
@login_required
def dashboard(request, folder_id=None):
    """Main Drive dashboard showing folders and files."""
    user = request.user
    folder = None

    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id, user=user)

    folders = Folder.objects.filter(user=user, parent=folder).order_by('name')
    files = File.objects.filter(user=user, folder=folder, is_deleted=False).order_by('-uploaded_at')

    for f in files:
        uploader = getattr(f, 'user', None)
        f.uploader_name = getattr(uploader, 'username', '—') if uploader else '—'

    context = {
        'folders': folders,
        'files': files,
        'current_folder': folder,
        'current_folder_id': folder_id,
        'folder_name': folder.name if folder else "My Drive",
        'storage_used': None,
        'storage_total': '15 GB',
    }
    return render(request, 'sharing_app/dashboard.html', context)


# ==========================================================
# 📁 Folder View (Open inside folder)
# ==========================================================
@login_required
def folder_view(request, folder_id):
    """Open a specific folder & display its contents."""
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    subfolders = Folder.objects.filter(parent=folder, user=request.user)
    files = File.objects.filter(folder=folder, user=request.user, is_deleted=False)

    context = {
        'current_folder': folder,
        'folders': subfolders,
        'files': files,
        'folder_name': folder.name,
    }
    return render(request, 'sharing_app/dashboard.html', context)


# ==========================================================
# 📁 Create Folder
# ==========================================================
@login_required
def create_folder(request):
    """Handles folder creation."""
    if request.method == "POST":
        folder_name = request.POST.get("name", "").strip()
        parent_id = request.POST.get("parent_id")
        parent_folder = None

        if parent_id:
            parent_folder = Folder.objects.filter(id=parent_id, user=request.user).first()

        if not folder_name:
            messages.error(request, "⚠️ Folder name cannot be empty.")
        else:
            exists = Folder.objects.filter(user=request.user, parent=parent_folder, name=folder_name).exists()
            if exists:
                messages.warning(request, f"A folder named '{folder_name}' already exists.")
            else:
                Folder.objects.create(user=request.user, name=folder_name, parent=parent_folder)
                messages.success(request, f"📁 Folder '{folder_name}' created successfully!")
                if parent_folder:
                    return redirect('sharing:folder_view', folder_id=parent_folder.id)
                return redirect('sharing:dashboard')

    return render(request, "sharing_app/new_folder.html")


# ==========================================================
# 📤 Upload File
# ==========================================================
@login_required
def upload_file(request):
    """Handles file uploads via form and prevents duplicates."""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded = request.FILES['file']
        folder_id = request.POST.get('folder_id') or None
        folder = Folder.objects.filter(id=folder_id, user=request.user).first() if folder_id else None

        existing_names = File.objects.filter(user=request.user, folder=folder).values_list('original_name', flat=True)
        final_name = uploaded.name
        base, ext = os.path.splitext(uploaded.name)
        count = 1
        while final_name in existing_names:
            final_name = f"{base}_{count}{ext}"
            count += 1

        File.objects.create(
            user=request.user,
            file=uploaded,
            original_name=final_name,
            folder=folder
        )
        messages.success(request, f"✅ File '{final_name}' uploaded successfully!")

        return redirect('sharing:folder_view', folder.id) if folder else redirect('sharing:dashboard')

    folders = Folder.objects.filter(user=request.user)
    return render(request, 'sharing_app/upload.html', {'folders': folders})


# ==========================================================
# 📝 Create Text File
# ==========================================================
@login_required
def create_text_file(request):
    """Allows user to create a new text file manually."""
    if request.method == "POST":
        filename = request.POST.get("filename", "").strip()
        content = request.POST.get("content", "")
        parent_id = request.POST.get("parent_id")
        parent_folder = Folder.objects.filter(id=parent_id, user=request.user).first() if parent_id else None

        if not filename:
            messages.error(request, "⚠️ File name cannot be empty.")
            return redirect('sharing:dashboard')

        if not filename.endswith('.txt'):
            filename += '.txt'

        new_file = File.objects.create(
            user=request.user,
            original_name=filename,
            folder=parent_folder
        )
        new_file.file.save(filename, ContentFile(content), save=True)

        messages.success(request, f"📝 Text file '{filename}' created successfully.")
        return redirect('sharing:folder_view', parent_folder.id) if parent_folder else redirect('sharing:dashboard')

    return render(request, "sharing_app/create_text.html")


# ==========================================================
# 🗑️ Trash Operations
# ==========================================================
@login_required
def delete_file(request, pk):
    """Moves a file to Trash."""
    file_obj = get_object_or_404(File, pk=pk, user=request.user)
    file_obj.is_deleted = True
    file_obj.deleted_at = timezone.now()
    file_obj.save()
    messages.warning(request, f"🗑️ '{file_obj.original_name}' moved to Trash.")
    return redirect('sharing:dashboard')


@login_required
def restore_file(request, pk):
    """Restores a file from Trash."""
    file_obj = get_object_or_404(File, pk=pk, user=request.user, is_deleted=True)
    file_obj.is_deleted = False
    file_obj.deleted_at = None
    file_obj.save()
    messages.success(request, f"♻️ '{file_obj.original_name}' restored successfully.")
    return redirect('sharing:trash')


@login_required
def delete_permanent(request, pk):
    """Permanently deletes a file."""
    file_obj = get_object_or_404(File, pk=pk, user=request.user, is_deleted=True)
    file_obj.file.delete(save=False)
    file_obj.delete()
    messages.success(request, f"❌ '{file_obj.original_name}' deleted permanently.")
    return redirect('sharing:trash')


# ==========================================================
# ⬇️ File Download / View
# ==========================================================
@login_required
def download_private(request, pk):
    """Allows the owner to download their private file."""
    file_obj = get_object_or_404(File, pk=pk, user=request.user, is_deleted=False)
    path = file_obj.file.path
    if not os.path.exists(path):
        raise Http404("File not found")

    mime, _ = mimetypes.guess_type(path)
    with open(path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_obj.original_name}"'
        return response


@login_required
def file_view(request, file_id):
    """Displays or previews the file in browser (owner only)."""
    f = get_object_or_404(File, id=file_id, user=request.user)
    try:
        return FileResponse(f.file.open('rb'), as_attachment=False, filename=f.original_name)
    except Exception:
        raise Http404("File not found")


# ==========================================================
# 🔗 Share & Public Access
# ==========================================================
@login_required
def share_file(request, pk):
    """Generates a public share link for a file."""
    file_obj = get_object_or_404(File, pk=pk, user=request.user, is_deleted=False)
    share_key = uuid.uuid4()

    shared = SharedFile.objects.create(
        owner=request.user,  # SharedFile still uses 'owner'
        file=file_obj.file,
        name=file_obj.original_name,
        share_key=share_key,
        shared_expiry=timezone.now() + timedelta(minutes=10),
        share_count=0,
        max_share_limit=5,
    )

    share_url = request.build_absolute_uri(reverse('sharing:download_public', args=[share_key]))
    whatsapp_url = f"https://api.whatsapp.com/send?text=📁 Download this file ({file_obj.original_name}): {share_url}"

    messages.success(request, "✅ Share link created successfully!")
    return render(request, 'sharing_app/share_success.html', {
        'file_name': file_obj.original_name,
        'share_url': share_url,
        'whatsapp_url': whatsapp_url,
        'expiry': shared.shared_expiry,
    })


def download_public(request, share_key):
    """Allows anyone with the share link to download."""
    shared = get_object_or_404(SharedFile, share_key=share_key)

    if shared.shared_expiry and timezone.now() > shared.shared_expiry:
        return HttpResponseForbidden("⚠️ This link has expired.")

    if shared.share_count >= shared.max_share_limit:
        return HttpResponseForbidden("⚠️ Share limit exceeded.")

    shared.share_count += 1
    shared.save(update_fields=['share_count'])

    path = shared.file.path
    if not os.path.exists(path):
        raise Http404("File not found")

    mime, _ = mimetypes.guess_type(path)
    with open(path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{shared.name}"'
        return response


# ==========================================================
# 🧩 Access Shared File (with token)
# ==========================================================
@login_required
def access_shared_file(request, shared_token):
    """Access a file via shared token (only owner or permitted user)."""
    try:
        shared_file = SharedFile.objects.get(shared_token=shared_token)
    except SharedFile.DoesNotExist:
        raise Http404("Shared file not found")

    if request.user != shared_file.owner:
        return HttpResponseForbidden("🚫 You don't have permission to access this file.")

    file_obj = shared_file.file
    return FileResponse(file_obj.open('rb'), as_attachment=False, filename=shared_file.name)


# ==========================================================
# 🕒 Recent & Trash
# ==========================================================
@login_required
def recent_files(request):
    """Displays recently uploaded files."""
    recent = File.objects.filter(user=request.user, is_deleted=False).order_by('-uploaded_at')[:20]
    return render(request, 'sharing_app/recent.html', {'files': recent})


@login_required
def trash(request):
    """Displays deleted files in Trash."""
    trash_files = File.objects.filter(user=request.user, is_deleted=True).order_by('-deleted_at')
    return render(request, 'sharing_app/trash.html', {'trash_files': trash_files})
