from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.utils.translation import gettext as _
from django.core.mail import send_mail, get_connection
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import get_language
from .models import Service, About, ContactMessage, SiteSetting

def index(request):
    services = Service.objects.filter(is_active=True).order_by('order')
    context = {'services': services}
    return render(request, 'omarusaapp/index.html', context)

def service_detail(request, slug):
    service = None
    
    # إصلاح: البحث المباشر في جدول الترجمات لتجاوز مشاكل فلترة parler
    # هذه الطريقة تبحث عن الـ slug في أي لغة كانت
    try:
        service = Service.objects.filter(is_active=True, translations__slug=slug).distinct().first()
    except Exception:
        pass
    
    # محاولة البحث باستخدام ID إذا كان slug رقماً
    if not service and slug.isdigit():
        try:
            service = Service.objects.get(id=int(slug), is_active=True)
        except Service.DoesNotExist:
            pass
    
    # إذا لم يتم العثور على الخدمة
    if not service:
        raise Http404("الخدمة غير موجودة")
    
    context = {'service': service}
    return render(request, 'omarusaapp/service_detail.html', context)

def about(request):
    about_content = About.objects.first()
    context = {'about': about_content}
    return render(request, 'omarusaapp/about.html', context)

def contact_view(request):
    # إصلاح: إذا كان الطلب GET يتم توجيه المستخدم للرئيسية
    if request.method == 'GET':
        return redirect('omarusaapp:index')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(name=name, email=email, message=message)
        site_settings = SiteSetting.objects.first()
        
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

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def dashboard(request):
    settings = SiteSetting.objects.first()
    if not settings:
        settings = SiteSetting.objects.create()

    if request.method == 'POST':
        # الحقول الثابتة (غير المترجمة)
        settings.phone = request.POST.get('phone', '')
        settings.email = request.POST.get('email', '')
        settings.whatsapp_number = request.POST.get('whatsapp_number', '')
        settings.admin_receive_email = request.POST.get('admin_receive_email', '')
        
        settings.email_host = request.POST.get('email_host', '')
        
        # معالجة آمنة لتحويل البورت إلى رقم صحيح
        try:
            settings.email_port = int(request.POST.get('email_port') or 587)
        except (ValueError, TypeError):
            settings.email_port = 587
            
        settings.email_use_ssl = request.POST.get('email_use_ssl') == 'on'
        settings.email_host_user = request.POST.get('email_host_user', '')
        settings.email_host_password = request.POST.get('email_host_password', '')
        
        # حقول ثابتة أخرى
        settings.menu_title = request.POST.get('menu_title', 'Menu')
        settings.home_link = request.POST.get('home_link', 'Home')
        settings.about_link = request.POST.get('about_link', 'About')
        settings.footer_get_in_touch = request.POST.get('footer_get_in_touch', 'GET IN TOUCH')
        settings.footer_follow = request.POST.get('footer_follow', 'FOLLOW')
        settings.footer_send_message = request.POST.get('footer_send_message', 'SEND MESSAGE')
        settings.footer_name_placeholder = request.POST.get('footer_name_placeholder', 'الاسم')
        settings.footer_email_placeholder = request.POST.get('footer_email_placeholder', 'البريد الإلكتروني')
        settings.footer_message_placeholder = request.POST.get('footer_message_placeholder', 'الرسالة')
        settings.footer_submit_btn = request.POST.get('footer_submit_btn', 'إرسال')
        settings.footer_success_msg = request.POST.get('footer_success_msg', '✅ تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.')
        
        # حفظ الترجمات باللغتين
        settings.set_current_language('ar')
        settings.company_name = request.POST.get('company_name_ar', '')
        settings.address = request.POST.get('address_ar', '')
        settings.welcome_text = request.POST.get('welcome_text_ar', '')
        settings.copyright_text = request.POST.get('copyright_text_ar', '')
        
        settings.set_current_language('en')
        settings.company_name = request.POST.get('company_name_en', settings.company_name)
        settings.address = request.POST.get('address_en', settings.address)
        settings.welcome_text = request.POST.get('welcome_text_en', settings.welcome_text)
        settings.copyright_text = request.POST.get('copyright_text_en', settings.copyright_text)
        
        settings.set_current_language(get_language())
        settings.save()
        
        messages.success(request, 'تم حفظ الإعدادات بنجاح!')
        return redirect('omarusaapp:dashboard')

    context = {'settings': settings}
    return render(request, 'omarusaapp/dashboard.html', context)



    