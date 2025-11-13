from django.apps import AppConfig

class FileSharingProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'file_sharing_project'

    def ready(self):
        # Import admin customization safely after apps are loaded
        from . import admin_custom
