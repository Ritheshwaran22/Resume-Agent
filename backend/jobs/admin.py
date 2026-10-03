from django.contrib import admin
from .models import JobDescription

@admin.register(JobDescription)
class JobDescriptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'description_preview')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'description', 'user__username', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def description_preview(self, obj):
        if len(obj.description) > 80:
            return obj.description[:80] + '...'
        return obj.description
    description_preview.short_description = 'Description Preview'
