from django.conf.urls import patterns, include, url
from django.contrib import admin

from .views import MapaListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$',
        MapaListView.as_view(),
        name='mapa'),

)
