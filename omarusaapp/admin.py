# omarusaapp/admin.py

from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Service, About, ContactMessage, SiteSetting

# تخصيص كيفية ظهور الخدمات في لوحة التحكم
class ServiceAdmin(TranslatableAdmin):
    list_display = ('__str__', 'is_active', 'order')
    
    # السطر التالي يجعل الحقول قابلة للتعديل مباشرة من الجدول
    list_editable = ('is_active', 'order') 
    
    list_filter = ('is_active',)
    search_fields = ('translations__name',)
    
    # إخفاء حقل Slug من نموذج الإضافة والتعديل
    exclude = ('slug',)

admin.site.register(Service, ServiceAdmin)

# تخصيص كيفية ظهور "من نحن" في لوحة التحكم
class AboutAdmin(TranslatableAdmin):
    pass

admin.site.register(About, AboutAdmin)

# تسجيل رسائل التواصل
admin.site.register(ContactMessage)

# تسجيل إعدادات الموقع (الفوتر)
class SiteSettingAdmin(TranslatableAdmin):
    # حقل القائمة ليعرض بسهولة
    list_display = ('__str__', 'phone', 'email')

admin.site.register(SiteSetting, SiteSettingAdmin)