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
    url(r'^columne/(?P<pk>\d+)/update/$', views.column_update, name='column_update'),
    url(r'^type/$', views.type_list, name='type_list'),
    url(r'^type/add/$', views.type_add, name='type_add'),
    url(r'^type/set/$', views.type_set, name='type_set'),
    url(r'^type/(?P<pk>\d+)/remove/$', views.type_remove, name='type_remove'),
    url(r'^type/(?P<pk>\d+)/$', views.type_detail, name='type_detail'),
    url(r'^type/(?P<pk>\d+)/update/$', views.type_edit, name='type_edit'),
    url(r'', views.upload_model, name='upload_model'),
]