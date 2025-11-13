from django.apps import AppConfig


class SharingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sharing_app'
    verbose_name = "📁 Secure File Sharing Module"

    def ready(self):
        """
        🔔 Automatically load Django signals when the app starts.
        This ensures file/folder events or audit tracking work properly.
        """
        import sharing_app.signals  # 👈 Important: register signals here
