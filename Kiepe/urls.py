"""Kiepe URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.views.generic import TemplateView
from Kiepe.main.views import *
from Kiepe.api import urls as api_urls

urlpatterns = [
    path('reverseuserstatus/<int:kid>/', reverse_user_status, name='kibanda_menu'),
    path('kibandainfo/<int:kid>/', restaurants_info, name='kibanda_info'),
    url(r'validateVibanda/$', validate_restaurants, name='validateVibanda'),
    url(r'^api/', include(api_urls)),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)