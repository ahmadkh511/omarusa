# omarusaapp/urls.py

from django.urls import path
from . import views

app_name = 'omarusaapp'

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.index, name='index'),
    
    # صفحة الخدمة (ديناميكية)
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    
    # صفحة من نحن
    path('about/', views.about, name='about'),
    
    # معالجة نموذج الاتصال
    path('contact/', views.contact_view, name='contact_view'),
]