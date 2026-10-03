from django.contrib import admin
from .models import Resume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('filename', 'user', 'uploaded_at', 'file_size_display')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('filename', 'user__username', 'user__email')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)

    def file_size_display(self, obj):
        try:
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            return f"{size / (1024 * 1024):.2f} MB"
        except Exception:
            return "N/A"
    file_size_display.short_description = 'Size'
