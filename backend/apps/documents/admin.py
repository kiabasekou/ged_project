# backend/apps/documents/admin.py

from django.contrib import admin
from .models import Folder, Document

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'dossier', 'parent', 'created_at')
    list_filter = ('dossier',)
    search_fields = ('name', 'dossier__reference_code')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'dossier', 'folder_path', 'file_extension', 'uploaded_by', 'uploaded_at', 'version')
    list_filter = ('file_extension', 'dossier', 'folder', 'sensitivity')
    search_fields = ('title', 'description', 'original_filename', 'dossier__reference_code')
    readonly_fields = ('file_size', 'file_hash', 'file_url')

    def file_url(self, obj):
        return obj.file.url if obj.file else '-'
    file_url.short_description = "URL"

    def folder_path(self, obj):
        return obj.folder.full_path if obj.folder else 'Racine'
    folder_path.short_description = "Répertoire"