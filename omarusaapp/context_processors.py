from django.utils.translation import get_language
from django.conf import settings
from .models import Service, SiteSetting

def global_settings(request):
    """
    يجلب الخدمات المفعلة وإعدادات الموقع (الهيدر والفوتر)
    ويجعلها متاحة في جميع قوالب الموقع.
    """
    # إصلاح: استخدام get_solo لضمان إرجاع سجل الإعدادات دائماً وعدم يكون None
    site_settings = SiteSetting.objects.get_solo()
    
    return {
        # إصلاح: استخدام _default_manager لجلب جميع الخدمات للقائمة العلوية بغض النظر عن الترجمة
        'menu_services': Service._default_manager.filter(is_active=True).order_by('order'),
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