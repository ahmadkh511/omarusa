# omarusaapp/context_processors.py

from .models import Service, SiteSetting

def global_settings(request):
    """
    يجلب الخدمات المفعلة وإعدادات الموقع (الهيدر والفوتر)
    ويجعلها متاحة في جميع قوالب الموقع.
    """
    # جلب أول سجل من إعدادات الموقع (لأننا نستخدم نمط Singleton)
    site_settings = SiteSetting.objects.first()
    
    return {
        'menu_services': Service.objects.filter(is_active=True).order_by('order'),
        'site_settings': site_settings
    }