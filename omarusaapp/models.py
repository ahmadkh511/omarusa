# omarusaapp/models.py

from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields

class Service(TranslatableModel):
    """
    نموذج الخدمات - قابل للترجمة
    """
    # حقول مشتركة
    thumbnail = models.ImageField(
        upload_to='services/thumbnails/',
        verbose_name='الصورة المصغرة',
        blank=True,
        null=True
    )
    main_image = models.ImageField(
        upload_to='services/main/',
        verbose_name='الصورة الرئيسية',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True, verbose_name='مفعل')
    order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # حقول مترجمة - Slug غير مطلوب من المستخدم
    translations = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name='اسم الخدمة'),
        slug=models.SlugField(max_length=200, unique=True, blank=True, null=True),
        short_description=models.TextField(max_length=500, blank=True, verbose_name='وصف قصير'),
        full_description=models.TextField(blank=True, verbose_name='وصف كامل'),
    )
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'خدمة'
        verbose_name_plural = 'الخدمات'
    
    def __str__(self):
        return self.safe_translation_getter('name', 'خدمة')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        for lang in ['ar', 'en']:
            if self.has_translation(lang):
                translation = self.translations.get(language_code=lang)
                if not translation.slug and translation.name:
                    base_slug = slugify(translation.name, allow_unicode=True)
                    unique_slug = base_slug
                    counter = 1
                    while Service.objects.filter(
                        translations__slug=unique_slug,
                        translations__language_code=lang
                    ).exclude(id=self.id).exists():
                        unique_slug = f"{base_slug}-{counter}"
                        counter += 1
                    translation.slug = unique_slug
                    translation.save()


class About(TranslatableModel):
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    translations = TranslatedFields(
        title=models.CharField(max_length=200, verbose_name='العنوان', default='من نحن'),
        content=models.TextField(blank=True, verbose_name='المحتوى'),
    )
    
    class Meta:
        verbose_name = 'من نحن'
        verbose_name_plural = 'من نحن'
    
    def __str__(self):
        return self.safe_translation_getter('title', 'من نحن')


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='الاسم')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    message = models.TextField(verbose_name='الرسالة')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'رسالة اتصال'
        verbose_name_plural = 'رسائل الاتصال'
    
    def __str__(self):
        return f'رسالة من {self.name}'




# في أسفل ملف omarusaapp/models.py


class SiteSetting(TranslatableModel):
    # حقول الهيدر
    logo = models.ImageField(upload_to='site/', verbose_name='شعار الشركة', blank=True, null=True)
    
    # حقول مشتركة (الفوتر - روابط وتواصل)
    phone = models.CharField(max_length=20, verbose_name='رقم الهاتف', blank=True, null=True)
    email = models.EmailField(verbose_name='البريد الإلكتروني المعروض بالفوتر', blank=True, null=True)
    facebook_url = models.URLField(verbose_name='رابط فيسبوك', blank=True, null=True)
    instagram_url = models.URLField(verbose_name='رابط انستغرام', blank=True, null=True)
    twitter_url = models.URLField(verbose_name='رابط تويتر', blank=True, null=True)
    
    # ===== حقول إعدادات البريد الإلكتروني (SMTP) =====
    email_host = models.CharField(max_length=255, verbose_name='خادم البريد (SMTP Host)', blank=True, null=True, help_text="مثال: mail.yourdomain.com")
    email_port = models.IntegerField(default=465, verbose_name='بورت البريد (Port)', help_text="غالباً 465 لـ SSL أو 587 لـ TLS")
    email_use_ssl = models.BooleanField(default=True, verbose_name='استخدام SSL (للبورت 465)')
    email_host_user = models.CharField(max_length=255, verbose_name='بريد المرسل (Email User)', blank=True, null=True)
    email_host_password = models.CharField(max_length=255, verbose_name='كلمة مرور البريد', blank=True, null=True)
    admin_receive_email = models.EmailField(verbose_name='بريد استقبال الرسائل', blank=True, null=True, help_text="البريد الذي ستصلك إليه رسائل العملاء")
    # ================================================

    # حقول مترجمة (الهيدر والفوتر)
    translations = TranslatedFields(
        company_name=models.CharField(max_length=200, verbose_name='اسم الشركة', default='Clear Document Preparation LLC'),
        welcome_text=models.TextField(verbose_name='النص الترحيبي (الصفحة الرئيسية)', blank=True, null=True),
        address=models.TextField(verbose_name='العنوان', blank=True, null=True),
        copyright_text=models.CharField(
            max_length=255, 
            verbose_name='نص حقوق النشر', 
            default='© Clear Document Preparation LLC. All rights reserved'
        ),
    )

    class Meta:
        verbose_name = 'إعداد الموقع'
        verbose_name_plural = 'إعدادات الموقع'

    def __str__(self):
        return 'إعدادات الموقع'    