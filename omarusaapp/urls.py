# omarusaapp/urls.py

from django.urls import path, re_path
from . import views

app_name = 'omarusaapp' # تأكد أن هذا هو الاسم المستخدم في القوالب

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.index, name='index'),
    
    # صفحة الخدمة (استخدمنا re_path لدعم الحروف العربية في الـ slug)
    re_path(r'^service/(?P<slug>[-\w]+)/$', views.service_detail, name='service_detail'),
    
    # صفحة من نحن
    path('about/', views.about, name='about'),
    
    # صفحة التواصل (تم تعديل الاسم ليطابق القوالب)
    path('contact/', views.contact_view, name='contact_view'),


    path('dashboard/', views.dashboard, name='dashboard'),
]