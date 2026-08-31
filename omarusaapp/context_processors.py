from django.utils.translation import get_language
from django.conf import settings
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

def language_context(request):
    """
    يضيف اللغة الحالية وقائمة اللغات المتاحة إلى جميع القوالب
    """
    current_language = get_language()
    languages = []
    
    for code, name in settings.LANGUAGES:
        languages.append({
            'code': code,
            'name': name,
            'active': code == current_language,
        })
    
    return {
        'current_language': current_language,
        'languages': languages,
    }