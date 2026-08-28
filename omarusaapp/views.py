# omarusaapp/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils.translation import gettext as _
from .models import Service, About, ContactMessage

def index(request):
    """
    الصفحة الرئيسية - تعرض جميع الخدمات النشطة
    """
    services = Service.objects.filter(is_active=True).order_by('order')
    context = {
        'services': services,
    }
    return render(request, 'omarusaapp/index.html', context)


def service_detail(request, slug):
    """
    صفحة الخدمة - تعرض تفاصيل خدمة محددة بناءً على الـ slug
    """
    # استخدام طريقة parler الآمنة لجلب الخدمة بناءً على الـ slug
    service = get_object_or_404(
        Service.objects.translated(slug=slug), 
        is_active=True
    )
    context = {
        'service': service,
    }
    return render(request, 'omarusaapp/service_detail.html', context)


def about(request):
    """
    صفحة من نحن
    """
    about_content = About.objects.first()
    context = {
        'about': about_content,
    }
    return render(request, 'omarusaapp/about.html', context)


def contact_view(request):
    """
    معالجة نموذج الاتصال
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        
        return JsonResponse({
            'success': True,
            'message': _('تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.')
        })
    
    return JsonResponse({
        'success': False,
        'message': _('حدث خطأ في الإرسال')
    })