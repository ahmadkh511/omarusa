from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Service, About, ContactMessage, SiteSetting

# تخصيص كيفية ظهور الخدمات في لوحة التحكم
class ServiceAdmin(TranslatableAdmin):
    list_display = ('__str__', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('translations__name',)
    list_editable = ('is_active', 'order') 
    exclude = ('slug',)

admin.site.register(Service, ServiceAdmin)

# تخصيص كيفية ظهور "من نحن" في لوحة التحكم
class AboutAdmin(TranslatableAdmin):
    pass

admin.site.register(About, AboutAdmin)

# تسجيل رسائل التواصل
admin.site.register(ContactMessage)

# تسجيل إعدادات الموقع (الفوتر والإيميل والواتساب)
class SiteSettingAdmin(TranslatableAdmin):
    list_display = ('__str__', 'phone', 'email')
    
    # تنظيم الحقول في أقسام لتسهيل التعديل على العميل
    fieldsets = (
        (None, {
            'fields': ('logo', 'phone', 'email', 'whatsapp_number', 'facebook_url', 'instagram_url', 'twitter_url', 'admin_receive_email')
        }),
        ('إعدادات خادم البريد (SMTP)', {
            'fields': ('email_host', 'email_port', 'email_use_ssl', 'email_host_user', 'email_host_password'),
            'description': 'هذه الإعدادات تُستخدم لإرسال رسائل العملاء من الموقع إلى بريدك. (مثال: smtp-relay.brevo.com و Port 587 مع إيقاف SSL)'
        }),
    )

admin.site.register(SiteSetting, SiteSettingAdmin)