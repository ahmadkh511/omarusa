from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.utils.translation import gettext as _
from django.core.mail import send_mail, get_connection
from django.contrib import messages
from .models import Service, About, ContactMessage, SiteSetting

def index(request):
    # جلب جميع الخدمات المفعلة (الاستعلام القياسي)
    services = Service.objects.filter(is_active=True).order_by('order')
    context = {'services': services}
    return render(request, 'omarusaapp/index.html', context)

def service_detail(request, slug):
    service = None
    
    try:
        service = Service.objects.filter(is_active=True, translations__slug=slug).distinct().first()
    except Exception:
        pass
    
    if not service and slug.isdigit():
        try:
            service = Service.objects.get(id=int(slug), is_active=True)
        except Service.DoesNotExist:
            pass
    
    if not service:
        raise Http404("الخدمة غير موجودة")
    
    context = {'service': service}
    return render(request, 'omarusaapp/service_detail.html', context)

def about(request):
    about_content = About.objects.first()
    context = {'about': about_content}
    return render(request, 'omarusaapp/about.html', context)

def contact_view(request):
    if request.method == 'GET':
        return redirect('omarusaapp:index')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(name=name, email=email, message=message)
        site_settings = SiteSetting.objects.get_solo()
        
        if site_settings and site_settings.email_host and site_settings.email_host_user:
            try:
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
                send_mail(subject, email_message, site_settings.email_host_user, [receive_email], fail_silently=False, connection=connection)
            except Exception as e:
                print(f"Email sending failed: {e}")
                return JsonResponse({'success': True, 'message': _('تم استلام رسالتك بنجاح! (تعذر إرسال إشعار البريد الإلكتروني مؤقتاً)')})
            
            return JsonResponse({'success': True, 'message': _('تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.')})
        else:
            return JsonResponse({'success': True, 'message': _('تم استلام رسالتك بنجاح!')})
    
    return JsonResponse({'success': False, 'message': _('حدث خطأ في الإرسال')})