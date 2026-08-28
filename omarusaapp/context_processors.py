# omarusaapp/context_processors.py

from .models import Service

def services_processor(request):
    """
    إضافة الخدمات النشطة إلى جميع القوالب
    """
    try:
        services = Service.objects.filter(is_active=True).order_by('order')
        return {
            'services': services,
        }
    except Exception:
        return {
            'services': [],
        }