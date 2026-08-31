from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Service, About, SiteSetting, ContactMessage

class CustomTranslatableAdmin(TranslatableAdmin):
    # إضافة هذا المتغير لحل مشكلة delete_confirmation_max_display
    delete_confirmation_max_display = 100

@admin.register(Service)
class ServiceAdmin(CustomTranslatableAdmin):
    list_display = ['name', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['translations__name', 'translations__short_description']
    list_editable = ['is_active', 'order']
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('المعلومات الأساسية', {
                'fields': ('thumbnail', 'main_image', 'is_active', 'order')
            }),
            ('الترجمة', {
                'fields': (
                    'name',
                    'short_description',
                    'full_description'
                )
            }),
        )
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # إخفاء حقل slug من النموذج
        if 'slug' in form.base_fields:
            form.base_fields['slug'].widget = admin.widgets.AdminTextInputWidget(
                attrs={'readonly': 'readonly', 'style': 'display:none;'}
            )
            form.base_fields['slug'].required = False
        return form

@admin.register(About)
class AboutAdmin(CustomTranslatableAdmin):
    list_display = ['title', 'updated_at']
    
    fieldsets = (
        ('الصورة', {
            'fields': ('image',)
        }),
        ('الترجمة', {
            'fields': ('title', 'content')
        }),
    )

@admin.register(SiteSetting)
class SiteSettingAdmin(CustomTranslatableAdmin):
    list_display = ['company_name', 'phone', 'email']
    
    fieldsets = (
        ('معلومات الشركة', {
            'fields': ('logo', 'company_name', 'phone', 'email', 'address', 'copyright_text')
        }),
        ('وسائل التواصل', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'whatsapp_number')
        }),
        ('إعدادات البريد SMTP', {
            'fields': ('email_host', 'email_port', 'email_use_ssl', 'email_host_user', 'email_host_password', 'admin_receive_email')
        }),
        ('نصوص القائمة (Menu)', {
            'fields': ('menu_title', 'home_link', 'about_link')
        }),
        ('نصوص الفوتر (Footer)', {
            'fields': ('footer_get_in_touch', 'footer_follow', 'footer_send_message', 
                      'footer_name_placeholder', 'footer_email_placeholder', 
                      'footer_message_placeholder', 'footer_submit_btn', 'footer_success_msg')
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'message', 'created_at']