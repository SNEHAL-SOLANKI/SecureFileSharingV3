from django.contrib import admin
from .models import Folder, File, SharedFile

admin.site.register(Folder)
admin.site.register(File)
admin.site.register(SharedFile)
