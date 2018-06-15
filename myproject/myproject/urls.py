"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from myapp import views
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', RedirectView.as_view(url='/api/production/', permanent=True), name='index'),
    url(r'^api/production/$', views.get_production_data),
    url(r'^api/development/$', views.get_development_data),
    url(r'^api/legacy/$', views.get_legacy_data),
    url(r'^api/staging/$', views.get_staging_data),
    url(r'^api/domain/$', views.get_domain_info),
]
