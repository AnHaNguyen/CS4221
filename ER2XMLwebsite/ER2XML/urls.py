"""ER2XML URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^schema/create/$', views.schema_create, name='schema_create'),
    url(r'^edit/(?P<pk>\d+)/$', views.schema_edit, name='schema_edit'),
    url(r'^edit/(?P<pk>\d+)/detail/$', views.schema_detail, name='schema_detail'),
    url(r'^edit/(?P<pk>\d+)/save/$', views.schema_save, name='schema_save'),
    url(r'^model/$', views.model_list, name='model_list'),
    url(r'^model/(?P<pk>\d+)/remove/$', views.model_remove, name='model_remove'),
    url(r'^model/(?P<pk>\d+)/$', views.model_detail, name='model_detail'),
    url(r'^model/(?P<pk>\d+)/update/$', views.model_edit, name='model_edit'),
    url(r'', views.upload_model, name='upload_model'),
]