from django.contrib import admin
from .models import Custom_User, FileType, File, ReviewOperation,FileRequest,FileResponse

@admin.register(Custom_User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    search_fields = ('user__username', 'role')

@admin.register(FileType)
class FileTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'file_type', 'description', 'uploaded_by', 'upload_date', 'is_reviewed')
    search_fields = ('file', 'file_type__name', 'uploaded_by__username')
    list_filter = ('file_type', 'uploaded_by', 'upload_date', 'is_reviewed')

@admin.register(ReviewOperation)
class ReviewOperationAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'reviewed_by', 'forward_by', 'operation_type', 'comments', 'operation_date')
    search_fields = ('file__file', 'reviewed_by__username', 'forward_by__username', 'operation_type')
    list_filter = ('operation_type', 'operation_date')

admin.site.register(FileRequest)