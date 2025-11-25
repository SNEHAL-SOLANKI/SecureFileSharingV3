# ==========================================================
# 📁 Secure File Sharing - views.py (Final Updated Version)
# ==========================================================
import os
import subprocess
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
import clamd

from django.shortcuts import redirect, get_object_or_404
from .models import UploadedFile
from django.conf import settings

from .models import SharedFile, Folder, File
from .forms import RenameFolderForm, FolderPasswordForm, ConfirmDeleteForm, RenameFileForm

# ---------------------------
# Safe ClamAV scan function
# ---------------------------
try:
    import clamd
except ModuleNotFoundError:
    clamd = None
    print("⚠️ clamd module not installed. Virus scanning disabled.")


def scan_file_with_clamav(path):
    """
    Scans a file for viruses using ClamAV.
    Returns True if file is clean or scanning is disabled, False if infected.
    """
    if clamd is None:
        print(f"⚠️ Skipping virus scan for {path}.")
        return True  # Allow in development/testing

    try:
        cd = clamd.ClamdNetworkSocket()  
        result = cd.scan(path)
        # result example: {'filepath': ('OK', None)} or {'filepath': ('FOUND', 'EICAR-Test-Signature')}
        for res in result.values():
            if res[0] == 'FOUND':
                print(f"❌ Virus detected in file: {path}")
                return False  # infected
        print(f"✅ File is clean: {path}")
        return True  # clean
    except Exception as e:
        print(f"⚠️ ClamAV scan failed for {path}: {e}")
        return False



# ==========================================================
# 🏠 Public Home Page
# ==========================================================
def home(request):
    return render(request, 'home.html')


# ==========================================================
# 🚪 Logout
# ==========================================================
@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "👋 You’ve been logged out successfully.")
    return redirect('user:login')


# ==========================================================
# 📊 Dashboard (Root + Files) — FINAL UPDATED
# ==========================================================
@login_required
def dashboard(request, folder_id=None):
    """
    Default Dashboard (root folder).
    Folder password protection handled through folder_view().
    """
    user = request.user
    folder = None

    # If folder_id given → forward to folder_view
    if folder_id:
        return redirect('sharing:folder_view', folder_id=folder_id)

    # Root folders + files
    folders = Folder.objects.filter(user=user, parent=None).order_by('name')
    files = File.objects.filter(
        user=user, folder=None, is_deleted=False
    ).order_by('-uploaded_at')

    # Add uploader & safe_size for templates
    for f in files:
        uploader = getattr(f, 'user', None)
        f.uploader_name = getattr(uploader, 'username', '—') if uploader else '—'

        try:
            if f.file and getattr(f.file, 'path', None) and os.path.exists(f.file.path):
                f.safe_size = f.file.size
            else:
                f.safe_size = 0
        except Exception:
            f.safe_size = 0

    return render(request, 'sharing_app/dashboard.html', {
        'folders': folders,
        'files': files,
        'current_folder': None,
        'folder_name': "My Drive",
        'storage_total': '15 GB',
    })


# ==========================================================
# 📁 Folder View (PASSWORD PROTECTED) — FINAL UPDATED
# ==========================================================
@login_required
def folder_view(request, folder_id):
    """
    Folder handler:
    - Checks password
    - Protects subfolder access
    - Shows dashboard UI
    """
    folder = get_object_or_404(Folder, pk=folder_id, user=request.user)

    access_key = f'folder_access_{folder.id}'

    # Folder is secured and not unlocked yet
    if folder.is_protected and not request.session.get(access_key):
        if request.method == "POST":
            pwd = request.POST.get('folder_password', '')
            if folder.check_password(pwd):
                request.session[access_key] = True
                return redirect(request.GET.get("next") or request.path)
            else:
                messages.error(request, "❌ Wrong password for this folder!")

        return render(request, 'sharing_app/folder_password_prompt.html', {
            "folder": folder,
            "next": request.path
        })

    # Access granted → load child folders + files
    subfolders = Folder.objects.filter(
        parent=folder, user=request.user
    ).order_by('name')

    files = File.objects.filter(
        folder=folder, user=request.user, is_deleted=False
    ).order_by('-uploaded_at')

    # Add uploader + safe_size
    for f in files:
        uploader = getattr(f, 'user', None)
        f.uploader_name = getattr(uploader, 'username', '—') if uploader else '—'

        try:
            if f.file and getattr(f.file, 'path', None) and os.path.exists(f.file.path):
                f.safe_size = f.file.size
            else:
                f.safe_size = 0
        except Exception:
            f.safe_size = 0

    return render(request, 'sharing_app/dashboard.html', {
        'current_folder': folder,
        'folders': subfolders,
        'files': files,
        'folder_name': folder.name,
    })

 
# ==========================================================
# 📁 Create Folder (FINAL FIXED VERSION)
# ==========================================================
@login_required
def create_folder(request):
    parent_id = request.GET.get("parent") or request.POST.get("parent")

    # FIX: If parent_id is empty → set parent = None
    if not parent_id:
        parent_folder = None
    else:
        parent_folder = get_object_or_404(Folder, id=parent_id, user=request.user)

    if request.method == "POST":
        folder_name = request.POST.get("folder_name")

        new_folder = Folder.objects.create(
            name=folder_name,
            parent=parent_folder,
            user=request.user
        )

        messages.success(request, "Folder created successfully!")

        # Go to dashboard inside the same parent
        if parent_folder:
            return redirect("sharing:dashboard", folder_id=parent_folder.id)
        return redirect("sharing:dashboard_root")

    return render(request, "sharing_app/new_folder.html", {
        "parent_folder": parent_folder
    })

# ==========================================================
# ✏️ Rename Folder
# ==========================================================
@login_required
def rename_folder(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)

    if folder.user != request.user:
        return HttpResponseForbidden("You are not allowed.")

    if request.method == "POST":
        form = RenameFolderForm(request.POST)
        if form.is_valid():
            folder.name = form.cleaned_data['name']
            folder.save(update_fields=['name'])
            messages.success(request, "📁 Folder renamed successfully.")
            return redirect(request.GET.get('next') or reverse('sharing:dashboard'))
    else:
        form = RenameFolderForm(initial={'name': folder.name})

    return render(request, "sharing_app/rename_folder.html", {"form": form, "folder": folder})


# ==========================================================
# 🔐 Set / Remove Folder Password
# ==========================================================
@login_required
def set_folder_password(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)

    if folder.user != request.user:
        return HttpResponseForbidden("You are not allowed.")

    if request.method == "POST":
        form = FolderPasswordForm(request.POST)
        if form.is_valid():
            pwd = form.cleaned_data['password']
            folder.set_password(pwd)

            access_key = f'folder_access_{folder.id}'
            if access_key in request.session:
                del request.session[access_key]

            messages.success(request, "🔐 Password updated!" if pwd else "🔓 Password removed!")
            return redirect(request.GET.get('next') or reverse('sharing:dashboard'))
    else:
        form = FolderPasswordForm()

    return render(request, "sharing_app/set_folder_password.html", {"form": form, "folder": folder})


# ==========================================================
# 🗑️ Delete Folder
# ==========================================================
@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, pk=folder_id)

    if folder.user != request.user:
        return HttpResponseForbidden("You are not allowed.")

    if request.method == "POST":
        form = ConfirmDeleteForm(request.POST)
        if form.is_valid() and form.cleaned_data.get('confirm'):
            folder.delete()
            messages.success(request, "❌ Folder deleted permanently.")
            return redirect(reverse('sharing:dashboard'))
    else:
        form = ConfirmDeleteForm()

    return render(request, "sharing_app/confirm_delete.html", {"form": form, "folder": folder})



# ==========================================================
# ✏️ Rename File — FINAL WORKING VERSION (paste this)
# ==========================================================
@login_required
def rename_file(request, pk):
    file_obj = get_object_or_404(File, id=pk, user=request.user)

    if request.method == "POST":
        new_name = request.POST.get("display_name", "").strip()

        if not new_name:
            messages.error(request, "⚠️ File name cannot be empty.")
            return redirect(request.path)

        # extract old extension
        old_ext = os.path.splitext(file_obj.name)[1]

        # if user has not typed extension, keep old
        if not os.path.splitext(new_name)[1]:
            new_name = new_name + old_ext

        # prevent duplicates inside same folder
        if File.objects.filter(
            user=request.user,
            folder=file_obj.folder,
            name=new_name
        ).exclude(id=file_obj.id).exists():
            messages.error(request, "⚠️ A file with this name already exists.")
            return redirect(request.path)

        # UPDATE BOTH FIELDS
        file_obj.name = new_name
        file_obj.display_name = new_name
        file_obj.save()

        messages.success(request, "✅ File renamed successfully!")

        # Redirect properly
        if file_obj.folder:
            return redirect("sharing:folder_view", folder_id=file_obj.folder.id)
        return redirect("sharing:dashboard")

    return render(request, "sharing_app/rename_file.html", {
        "file": file_obj
    })


# ==========================================================
# 📤 Upload File (FINAL — with ClamAV virus scan)
# ==========================================================
@login_required
@login_required
def upload_file(request):
    if request.method == 'GET':
        folders = Folder.objects.filter(user=request.user)
        return render(request, 'sharing_app/upload.html', {'folders': folders})

    uploaded_file = request.FILES.get('file')
    display_name = request.POST.get('display_name', '').strip()
    folder_id = request.POST.get('folder_id') or None

    if not uploaded_file:
        messages.error(request, "⚠️ Please select a file.")
        return redirect('sharing:upload')

    folder = None
    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id, user=request.user)

    ext = os.path.splitext(uploaded_file.name)[1]
    final_name = display_name + ext if display_name else uploaded_file.name

    # Duplicate check
    if File.objects.filter(user=request.user, folder=folder, original_name=final_name).exists():
        messages.error(request, f"⚠️ File '{final_name}' already exists.")
        return redirect('sharing:upload')

    # ====== Virus Scan using clamd ======
    try:
        cd = clamd.ClamdNetworkSocket('127.0.0.1', 3310)
        # Scan the uploaded file directly (in memory)
        result = cd.instream(uploaded_file.file)
        if any('FOUND' in res for res in result.values()):
            messages.error(request, "⚠️ Virus detected! File upload blocked.")
            return redirect('sharing:upload')
    except Exception as e:
        messages.warning(request, f"⚠️ Virus scan unavailable: {e}. Uploading without scan.")

    # Save file
    f = File.objects.create(user=request.user, original_name=final_name, folder=folder)
    f.file.save(final_name, uploaded_file, save=True)

    messages.success(request, f"✅ File '{final_name}' uploaded successfully!")
    return redirect('sharing:folder_view', folder_id=folder.id) if folder else redirect('sharing:dashboard_root')
# ==========================================================
# 📝 Create Text File
# ==========================================================
@login_required
def create_text_file(request):
    if request.method == "POST":
        filename = request.POST.get("filename", "").strip()
        content = request.POST.get("content", "")
        parent_id = request.POST.get("parent_id")
        parent_folder = Folder.objects.filter(id=parent_id, user=request.user).first()

        if parent_folder and parent_folder.is_protected:
            key = f'folder_access_{parent_folder.id}'
            if not request.session.get(key):
                messages.error(request, "❌ Folder password required.")
                return redirect('sharing:folder_view', parent_folder.id)

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

        messages.success(request, f"📝 Text file '{filename}' created.")
        return redirect('sharing:folder_view', parent_folder.id) if parent_folder else redirect('sharing:dashboard')

    return render(request, "sharing_app/create_text.html")


# ==========================================================
# 🗑️ File Delete / Restore / Permanent Delete (FINAL)
# ==========================================================
# ================================
# 🗑 Move file to Trash
# ================================
@login_required
def move_to_trash(request, file_id):
    file_obj = get_object_or_404(File, id=file_id, user=request.user)

    file_obj.is_deleted = True
    file_obj.deleted_at = timezone.now()
    file_obj.save(update_fields=['is_deleted', 'deleted_at'])

    messages.success(request, "🗑 File moved to Trash.")
    return redirect("sharing:dashboard")


# ================================
# 🗑 Show Trash Page
# ================================
@login_required
def trash_view(request):
    trashed_files = File.objects.filter(user=request.user, is_deleted=True).order_by('-deleted_at')
    return render(request, "sharing_app/trash.html", {"trashed_files": trashed_files})


# ================================
# 🔄 Restore file from Trash
# ================================
@login_required
def restore_file(request, file_id):
    file_obj = get_object_or_404(File, id=file_id, user=request.user)

    file_obj.is_deleted = False
    file_obj.deleted_at = None
    file_obj.save(update_fields=['is_deleted', 'deleted_at'])

    messages.success(request, "♻️ File restored successfully!")
    return redirect("sharing:trash")


# ================================
# ❌ Permanent Delete
# ================================
@login_required
def permanent_delete(request, file_id):
    file_obj = get_object_or_404(File, id=file_id, user=request.user)

    # Delete physical file
    try:
        if file_obj.file and os.path.exists(file_obj.file.path):
            os.remove(file_obj.file.path)
    except:
        pass

    file_obj.delete()
    messages.success(request, "🗑 File deleted permanently!")
    return redirect("sharing:trash")

# ==========================================================
# ⬇️ Download / View Files
# ==========================================================
@login_required
def download_private(request, pk):
    file_obj = get_object_or_404(File, pk=pk, user=request.user, is_deleted=False)
    path = file_obj.file.path

    if not os.path.exists(path):
        raise Http404("File not found")

    mime, _ = mimetypes.guess_type(path)
    with open(path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=mime or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="%s"' % file_obj.original_name
        return response


@login_required
def file_view(request, file_id):
    f = get_object_or_404(File, id=file_id, user=request.user)
    return FileResponse(f.file.open('rb'), as_attachment=False, filename=f.original_name)


# ==========================================================
# 🔗 Share File - Generate Link
# ==========================================================
@login_required
def share_file(request, pk):
    file_obj = get_object_or_404(File, pk=pk, user=request.user, is_deleted=False)
    share_key = uuid.uuid4()

    shared = SharedFile.objects.create(
        owner=request.user,
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


# ==========================================================
# 🌐 Public Download
# ==========================================================
def download_public(request, share_key):
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
        response['Content-Disposition'] = f'attachment; filename="%s"' % shared.name
        return response


# ==========================================================
# 🔐 Access shared file by token
# ==========================================================
@login_required
def access_shared_file(request, shared_token):
    shared = get_object_or_404(SharedFile, shared_token=shared_token)

    if shared.shared_expiry and timezone.now() > shared.shared_expiry:
        return HttpResponseForbidden("This shared token has expired.")

    return render(request, 'sharing_app/access_shared_file.html', {'shared': shared})


# ==========================================================
# 🕒 Recent & Trash
# ==========================================================
@login_required
def recent_files(request):
    recent = File.objects.filter(user=request.user, is_deleted=False).order_by('-uploaded_at')[:20]
    return render(request, 'sharing_app/recent.html', {'files': recent})


@login_required
def trash(request):
    trash_files = File.objects.filter(user=request.user, is_deleted=True).order_by('-deleted_at')
    return render(request, 'sharing_app/trash.html', {'trash_files': trash_files})
