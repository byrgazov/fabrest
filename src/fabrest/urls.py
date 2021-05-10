# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls    import path, re_path, include
from django.views.generic.base import RedirectView

from .polls import urls as polls_urls

urlpatterns = [
	path('',          RedirectView.as_view(url='api/', permanent=False), name='index'),
	path('admin/',    admin.site.urls),
	path('api-auth/', include('rest_framework.urls')),
	path('api/',      include(polls_urls.urlpatterns)),
]
