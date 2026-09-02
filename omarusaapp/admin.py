from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.html import escape
from parler.admin import TranslatableAdmin
from .models import Service, About, SiteSetting, ContactMessage

class CustomTranslatableAdmin(TranslatableAdmin):
    # تجاوز دالة حذف الترجمة لحل مشكلة Django 5.1+
    def delete_translation(self, request, object_id, language_code):
        opts = self.model._meta
        app_label = opts.app_label

        try:
            obj = self.get_queryset(request).get(pk=object_id)
        except self.model.DoesNotExist:
            obj = None

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': opts.object_name, 'key': escape(object_id)})

        try:
            translation = obj.translations.get(language_code=language_code)
        except obj.translations.model.DoesNotExist:
            raise Http404("No such translation")

        if request.POST:
            obj.delete_translation(language_code)
            self.message_user(request, _('The %(name)s "%(obj)s" was deleted successfully.') % {
                'name': opts.verbose_name,
                'obj': str(translation)
            })
            return HttpResponseRedirect("../../")

        context = {
            **self.admin_site.each_context(request),
            'title': _('Are you sure?'),
            'object_name': opts.verbose_name,
            'object': translation,
            'deleted_objects': [str(translation)],
            'perms_lacking': set(),
            'protected': [],
            'opts': opts,
            'app_label': app_label,
            'delete_confirmation_max_display': 100,
        }

        request.current_app = self.admin_site.name
        
        # إصلاح الخطأ: استخدام قالب Django الافتراضي للحذف لتفادي مشكلة TemplateDoesNotExist
        template = getattr(self, 'delete_translation_confirmation_template', None) or [
            "admin/%s/%s/delete_confirmation.html" % (app_label, opts.model_name),
            "admin/%s/delete_confirmation.html" % app_label,
            "admin/delete_confirmation.html"
        ]
        
        return render(request, template, context)

@admin.register(Service)
class ServiceAdmin(CustomTranslatableAdmin):
    list_display = ['name', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['translations__name', 'translations__short_description']
    list_editable = ['is_active', 'order']
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ('المعلومات الأساسية', {
                'fields': ('thumbnail', 'main_image', 'is_active', 'order')
            }),
            ('الترجمة', {
                'fields': (
                    'name',
                    'short_description',
                    'full_description'
                )
            }),
        )
        return fieldsets
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'slug' in form.base_fields:
            form.base_fields['slug'].widget = admin.widgets.AdminTextInputWidget(
                attrs={'readonly': 'readonly', 'style': 'display:none;'}
            )
            form.base_fields['slug'].required = False
        return form

@admin.register(About)
class AboutAdmin(CustomTranslatableAdmin):
    list_display = ['title', 'updated_at']
    fieldsets = (
        ('الصورة', {'fields': ('image',)}),
        ('الترجمة', {'fields': ('title', 'content')}),
    )

@admin.register(SiteSetting)
class SiteSettingAdmin(CustomTranslatableAdmin):
    list_display = ['company_name', 'phone', 'email']
    
    def has_add_permission(self, request):
        return not SiteSetting.objects.exists()

    def changelist_view(self, request, extra_context=None):
        if SiteSetting.objects.exists():
            obj = SiteSetting.objects.first()
            return redirect(reverse('admin:%s_%s_change' % (self.opts.app_label, self.opts.model_name), args=[obj.pk]))
        return super().changelist_view(request, extra_context)

    fieldsets = (
        ('معلومات الشركة', {
            'fields': ('logo', 'company_name', 'phone', 'email', 'address', 'welcome_text', 'copyright_text')
        }),
        ('وسائل التواصل', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'whatsapp_number')
        }),
        ('إعدادات البريد SMTP', {
            'fields': ('email_host', 'email_port', 'email_use_ssl', 'email_host_user', 'email_host_password', 'admin_receive_email')
        }),
        ('نصوص القائمة (Menu)', {
            'fields': ('menu_title', 'home_link', 'about_link')
        }),
        ('نصوص الفوتر (Footer)', {
            'fields': ('footer_get_in_touch', 'footer_follow', 'footer_send_message', 
                      'footer_name_placeholder', 'footer_email_placeholder', 
                      'footer_message_placeholder', 'footer_submit_btn', 'footer_success_msg')
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'message']
    readonly_fields = ['name', 'email', 'message', 'created_at']