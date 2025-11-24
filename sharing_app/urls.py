from django.urls import path
from . import views

app_name = 'sharing'

urlpatterns = [

    # =====================================================
    # 🏠 DASHBOARD
    # =====================================================
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_root'),

    # =====================================================
    # 📁 FOLDER VIEWS
    # =====================================================
    path('folder/<int:folder_id>/', views.folder_view, name='folder_view'),
    path('dashboard/<int:folder_id>/', views.folder_view, name='dashboard_folder'),

    # =====================================================
    # 📁 FOLDER MANAGEMENT
    # =====================================================
    path('create-folder/', views.create_folder, name='create_folder'),
    path('new-folder/', views.create_folder, name='new_folder'),

    # ⭐ RENAME / PASSWORD / DELETE FOLDER
    path('folder/<int:folder_id>/rename/', views.rename_folder, name='rename_folder'),
    path('folder/<int:folder_id>/password/', views.set_folder_password, name='set_folder_password'),
    path('folder/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),

    # =====================================================
    # ⬆️ FILE UPLOAD & CREATION
    # =====================================================
    path('upload/', views.upload_file, name='upload_file'),
    path('new-file/', views.create_text_file, name='new_file'),
    path('create-text-file/', views.create_text_file, name='create_text_file'),
    

    # =====================================================
    # ✏️ FILE RENAME (NEW URL)
    # =====================================================
    path("file/<int:pk>/rename/", views.rename_file, name="rename_file"),
      

    # =====================================================
    # 📄 FILE VIEW
    # =====================================================
    path('file/<int:file_id>/', views.file_view, name='file_view'),

    # =====================================================
    # 🔗 SHARING
    # =====================================================
    path('share/<int:pk>/', views.share_file, name='share_file'),

    # =====================================================
    # 🗑️ FILE ACTIONS
    # =====================================================
    path('delete/<int:pk>/', views.delete_file, name='delete'),
    path('restore/<int:pk>/', views.restore_file, name='restore_file'),
    path('delete-permanent/<int:pk>/', views.delete_permanent, name='delete_permanent'),

    # =====================================================
    # ⬇️ DOWNLOAD
    # =====================================================
    path('download/private/<int:pk>/', views.download_private, name='download_private'),
    path('download/public/<uuid:share_key>/', views.download_public, name='download_public'),

    # =====================================================
    # 🕒 RECENT & TRASH
    # =====================================================
    path('recent/', views.recent_files, name='recent_files'),
    path('trash/', views.trash, name='trash'),

    # =====================================================
    # 🚪 LOGOUT
    # =====================================================
    path('logout/', views.user_logout, name='logout'),

]
