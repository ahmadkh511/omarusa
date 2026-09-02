from django.db import models
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields
from parler.managers import TranslatableManager

class Service(TranslatableModel):
    thumbnail = models.ImageField(upload_to='services/thumbnails/', verbose_name='الصورة المصغرة', blank=True, null=True)
    main_image = models.ImageField(upload_to='services/main/', verbose_name='الصورة الرئيسية', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='مفعل')
    order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    translations = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name='اسم الخدمة'),
        slug=models.SlugField(max_length=200, blank=True, null=True),
        short_description=models.TextField(max_length=500, blank=True, verbose_name='وصف قصير'),
        full_description=models.TextField(blank=True, verbose_name='وصف كامل'),
    )
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'خدمة'
        verbose_name_plural = 'الخدمات'
    
    def __str__(self):
        return self.safe_translation_getter('name', 'خدمة') or 'خدمة'
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new or self.translations.filter(slug__isnull=True).exists() or self.translations.filter(slug__exact='').exists():
            self.generate_slugs()
    
    def generate_slugs(self):
        languages = ['ar', 'en']
        for lang in languages:
            try:
                translation = self.translations.get(language_code=lang)
            except self.translations.model.DoesNotExist:
                continue
            
            if translation.name and not translation.slug:
                base_slug = slugify(translation.name, allow_unicode=True)
                if not base_slug:
                    base_slug = f'service-{self.id}'
                
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
        return self.safe_translation_getter('title', 'من نحن') or 'من نحن'

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


class SiteSettingManager(TranslatableManager):
    """مدير مخصص لضمان وجود سجل واحد فقط (Singleton Pattern)"""
    def get_solo(self):
        instance = self.first()
        if instance is None:
            instance = self.create()
        return instance

class SiteSetting(TranslatableModel):
    logo = models.ImageField(upload_to='site/', verbose_name='شعار الشركة', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='رقم الهاتف', blank=True, null=True)
    email = models.EmailField(verbose_name='البريد الإلكتروني المعروض بالفوتر', blank=True, null=True)
    facebook_url = models.URLField(verbose_name='رابط فيسبوك', blank=True, null=True)
    instagram_url = models.URLField(verbose_name='رابط انستغرام', blank=True, null=True)
    twitter_url = models.URLField(verbose_name='رابط تويتر', blank=True, null=True)
    
    whatsapp_number = models.CharField(max_length=20, verbose_name='رقم واتساب (مع رمز الدولة)', blank=True, null=True, help_text="اتركه فارغاً لإخفاء الأيقونة. مثال للصيغة: 193318181")

    email_host = models.CharField(max_length=255, verbose_name='خادم البريد (SMTP Host)', blank=True, null=True, help_text="مثال: smtp-relay.brevo.com")
    email_port = models.IntegerField(default=587, verbose_name='بورت البريد (Port)', help_text="غالباً 465 لـ SSL أو 587 لـ TLS")
    email_use_ssl = models.BooleanField(default=False, verbose_name='استخدام SSL (للبورت 465)')
    email_host_user = models.CharField(max_length=255, verbose_name='بريد المرسل (Email User)', blank=True, null=True)
    email_host_password = models.CharField(max_length=255, verbose_name='كلمة مرور البريد', blank=True, null=True)
    admin_receive_email = models.EmailField(verbose_name='بريد استقبال الرسائل', blank=True, null=True, help_text="البريد الذي ستصلك إليه رسائل العملاء")

    # الحقول الثابتة (غير المترجمة) تبقى هنا
    # لاحظ أنه تم نقل حقول القائمة والفوتر للأسفل

    translations = TranslatedFields(
        company_name=models.CharField(max_length=200, verbose_name='اسم الشركة', default='Clear Document Preparation LLC'),
        welcome_text=models.TextField(verbose_name='النص الترحيبي (الصفحة الرئيسية)', blank=True, null=True),
        address=models.TextField(verbose_name='العنوان', blank=True, null=True),
        copyright_text=models.CharField(max_length=255, verbose_name='نص حقوق النشر', default='© Clear Document Preparation LLC. All rights reserved'),
        
        # تم نقل نصوص القائمة والفوتر هنا لتصبح مترجمة
        menu_title=models.CharField(max_length=50, verbose_name='عنوان القائمة', default='Menu', blank=True),
        home_link=models.CharField(max_length=50, verbose_name='نص رابط الرئيسية', default='Home', blank=True),
        about_link=models.CharField(max_length=50, verbose_name='نص رابط من نحن', default='About', blank=True),
        
        footer_get_in_touch=models.CharField(max_length=50, verbose_name='عنوان قسم التواصل', default='GET IN TOUCH', blank=True),
        footer_follow=models.CharField(max_length=50, verbose_name='عنوان قسم المتابعة', default='FOLLOW', blank=True),
        footer_send_message=models.CharField(max_length=50, verbose_name='عنوان نموذج الرسالة', default='SEND MESSAGE', blank=True),
        footer_name_placeholder=models.CharField(max_length=50, verbose_name='نص placeholder الاسم', default='الاسم', blank=True),
        footer_email_placeholder=models.CharField(max_length=50, verbose_name='نص placeholder البريد', default='البريد الإلكتروني', blank=True),
        footer_message_placeholder=models.CharField(max_length=50, verbose_name='نص placeholder الرسالة', default='الرسالة', blank=True),
        footer_submit_btn=models.CharField(max_length=50, verbose_name='نص زر الإرسال', default='إرسال', blank=True),
        footer_success_msg=models.CharField(max_length=200, verbose_name='رسالة النجاح', default='✅ تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.', blank=True),
    )

    objects = SiteSettingManager()

    class Meta:
        verbose_name = 'إعداد الموقع'
        verbose_name_plural = 'إعدادات الموقع'

    def __str__(self):
        return 'إعدادات الموقع'