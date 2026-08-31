from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from django.utils.translation import gettext as _
from django.core.mail import send_mail, get_connection
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import get_language
from .models import Service, About, ContactMessage, SiteSetting

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
    current_language = get_language()
    service = None
    
    # محاولة 1: البحث باللغة الحالية
    try:
        service = Service.objects.translated(slug=slug, language_code=current_language).get(is_active=True)
    except Service.DoesNotExist:
        pass
    
    # محاولة 2: البحث بكل اللغات
    if not service:
        for lang in ['ar', 'en']:
            try:
                service = Service.objects.translated(slug=slug, language_code=lang).get(is_active=True)
                break
            except Service.DoesNotExist:
                continue
    
    # محاولة 3: البحث باستخدام ID إذا كان slug رقماً
    if not service and slug.isdigit():
        try:
            service = Service.objects.get(id=int(slug), is_active=True)
        except Service.DoesNotExist:
            pass
    
    # إذا لم يتم العثور على الخدمة
    if not service:
        raise Http404("الخدمة غير موجودة")
    
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
    معالجة نموذج الاتصال وإرسال بريد إلكتروني باستخدام إعدادات قاعدة البيانات
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # 1. حفظ الرسالة في قاعدة البيانات
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        
        # 2. جلب إعدادات البريد من قاعدة البيانات
        site_settings = SiteSetting.objects.first()
        
        if site_settings and site_settings.email_host and site_settings.email_host_user:
            try:
                # إنشاء اتصال SMTP مخصص بناءً على إعدادات الموقع
                connection = get_connection(
                    host=site_settings.email_host,
                    port=site_settings.email_port,
                    username=site_settings.email_host_user,
                    password=site_settings.email_host_password,
                    use_ssl=site_settings.email_use_ssl,
                    use_tls=not site_settings.email_use_ssl,
                    fail_silently=False,
                )
                
                subject = f'رسالة جديدة من الموقع: {name}'
                email_message = f"""
لقد تلقيت رسالة جديدة من نموذج الاتصال في الموقع:

الاسم: {name}
البريد الإلكتروني: {email}

نص الرسالة:
{message}
                """
                
                receive_email = site_settings.admin_receive_email or site_settings.email_host_user
                
                send_mail(
                    subject,
                    email_message,
                    site_settings.email_host_user,
                    [receive_email],
                    fail_silently=False,
                    connection=connection
                )
            except Exception as e:
                print(f"Email sending failed: {e}")
                return JsonResponse({
                    'success': True,
                    'message': _('تم استلام رسالتك بنجاح! (تعذر إرسال إشعار البريد الإلكتروني مؤقتاً)')
                })
            
            return JsonResponse({
                'success': True,
                'message': _('تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.')
            })
        else:
            return JsonResponse({
                'success': True,
                'message': _('تم استلام رسالتك بنجاح!')
            })
    
    return JsonResponse({
        'success': False,
        'message': _('حدث خطأ في الإرسال')
    })


def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def dashboard(request):
    settings = SiteSetting.objects.first()
    if not settings:
        settings = SiteSetting.objects.create()

    if request.method == 'POST':
        settings.phone = request.POST.get('phone', '')
        settings.email = request.POST.get('email', '')
        settings.whatsapp_number = request.POST.get('whatsapp_number', '')
        settings.admin_receive_email = request.POST.get('admin_receive_email', '')
        
        settings.email_host = request.POST.get('email_host', '')
        settings.email_port = int(request.POST.get('email_port') or 587)
        settings.email_use_ssl = request.POST.get('email_use_ssl') == 'on'
        settings.email_host_user = request.POST.get('email_host_user', '')
        settings.email_host_password = request.POST.get('email_host_password', '')
        
        settings.set_current_language('ar')
        settings.company_name = request.POST.get('company_name', '')
        settings.address = request.POST.get('address', '')
        
        settings.save()
        
        messages.success(request, 'تم حفظ الإعدادات بنجاح!')
        return redirect('omarusaapp:dashboard')

    context = {
        'settings': settings
    }
    return render(request, 'omarusaapp/dashboard.html', context)