from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import File

@receiver(post_save, sender=File)
def touch_folder_on_file_save(sender, instance, **kwargs):
    if instance.folder:
        instance.folder.save()

@receiver(post_delete, sender=File)
def touch_folder_on_file_delete(sender, instance, **kwargs):
    if instance.folder:
        instance.folder.save()
