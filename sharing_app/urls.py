from django.urls import path
from . import views

app_name = 'sharing'

urlpatterns = [

    # =====================================================
    # 🏠 DASHBOARD (Root + Folder Views)
    # =====================================================
    path('', views.dashboard, name='dashboard'),                                     # Default root
    path('dashboard/', views.dashboard, name='dashboard_root'),                      # /sharing/dashboard/
    path('dashboard/<int:folder_id>/', views.dashboard, name='dashboard_folder'),    # /sharing/dashboard/1/

    # =====================================================
    # 📁 FOLDER MANAGEMENT
    # =====================================================
    path('create-folder/', views.create_folder, name='create_folder'),               # Create new folder
    path('new-folder/', views.create_folder, name='new_folder'),                     # Alias for UI/Sidebar
    path('folder/<int:folder_id>/', views.folder_view, name='folder_view'),          # Open specific folder

    # =====================================================
    # ⬆️ FILE UPLOAD & CREATION
    # =====================================================
    path('upload/', views.upload_file, name='upload_file'),                          # Upload file to folder
    path('new-file/', views.create_text_file, name='new_file'),                      # Alias (for UI/Sidebar)
    path('create-text-file/', views.create_text_file, name='create_text_file'),      # Manual text file creation

    # =====================================================
    # 📄 FILE VIEW / DETAILS
    # =====================================================
    path('file/<int:file_id>/', views.file_view, name='file_view'),                  # View file details or preview

    # =====================================================
    # 🔗 FILE SHARING (Private/Public)
    # =====================================================
    path('share/<int:pk>/', views.share_file, name='share_file'),                    # Generate & view share link

    # =====================================================
    # 🗑️ FILE ACTIONS (Delete / Restore / Permanent Delete)
    # =====================================================
    path('delete/<int:pk>/', views.delete_file, name='delete'),                      # Move file to trash
    path('restore/<int:pk>/', views.restore_file, name='restore_file'),              # Restore from trash
    path('delete-permanent/<int:pk>/', views.delete_permanent, name='delete_permanent'),  # Permanent delete

    # =====================================================
    # ⬇️ FILE DOWNLOAD (Private + Public)
    # =====================================================
    path('download/private/<int:pk>/', views.download_private, name='download_private'),   # Owner-only download
    path('download/public/<uuid:share_key>/', views.download_public, name='download_public'),  # Via public link

    # =====================================================
    # 🕒 RECENT & TRASH VIEWS
    # =====================================================
    path('recent/', views.recent_files, name='recent_files'),                        # Recently uploaded files
    path('trash/', views.trash, name='trash'),                                       # Deleted files view

    # =====================================================
    # 🚪 AUTH / LOGOUT
    # =====================================================
    path('logout/', views.user_logout, name='logout'),                               # Logout user session

    # =====================================================
    # 🔗 TOKEN-BASED ACCESS (Temporary Share Links)
    # =====================================================
    path('access/<str:shared_token>/', views.access_shared_file, name='access_shared_file'),  # Temp share access
]
