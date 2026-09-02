from django.urls import path, re_path
from . import views

app_name = 'omarusaapp'

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.index, name='index'),
    
    # صفحة الخدمة - تدعم slugs للغتين
    re_path(r'^service/(?P<slug>[-\w]+)/$', views.service_detail, name='service_detail'),
    
    # صفحة من نحن
    path('about/', views.about, name='about'),
    
    # صفحة التواصل
    path('contact/', views.contact_view, name='contact_view'),

    
]