from django.conf.urls import patterns, include, url
from django.contrib import admin

from .views import MapaListView, MapaJson, PosicioMapsView

admin.autodiscover()

urlpatterns = patterns('',

    url(r'mimapa/',PosicioMapsView.as_view()),

    url(r'^$',
        MapaListView.as_view(),
        name='mapa'),
    

)
