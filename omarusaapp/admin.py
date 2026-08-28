# omarusaapp/admin.py

from django.contrib import admin
from django import forms  # ✅ استيراد forms
from parler.admin import TranslatableAdmin
from .models import Service, About, ContactMessage

class ServiceAdmin(TranslatableAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    ordering = ['order']
    search_fields = ['translations__name']
    
    # إخفاء Slug من نموذج الإضافة
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'slug' in form.base_fields:
            form.base_fields['slug'].widget = forms.HiddenInput()  # ✅ استخدام forms.HiddenInput
        return form


class AboutAdmin(TranslatableAdmin):
    list_display = ['title', 'updated_at']


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'is_read']
    list_editable = ['is_read']
    readonly_fields = ['name', 'email', 'message', 'created_at']
    
    def has_add_permission(self, request):
        return False


admin.site.register(Service, ServiceAdmin)
admin.site.register(About, AboutAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)