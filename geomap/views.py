#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import ListView
from django.core import serializers
from django.http import Http404, HttpResponse

from .models import Ubicacion

import simplejson, urllib


class MapaListView(ListView):

    model = Ubicacion
    context_object_name = 'latest_question_list'
    template_name = 'mapa.html'

    def get_queryset(self):
        return Ubicacion.objects.order_by('-id')



#GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/place/radarsearch/json'

def MapaJson(address, **geo_args):
    lat = 10.221396
    lng = -67.471481

    geo_args.update({
        'location': '%f,%f' % (lat, lng),
        'radius': 500,
        'types': 'food|restaurant',
        'key': 'AIzaSyDoklHqzjuOTLDx14BM4mBq1bRf1vFd0Ts'
    })
    #https://maps.googleapis.com/maps/api/place/radarsearch/json?location=51.503186,-0.126446&radius=5000&types=museum&key=AIzaSyDoklHqzjuOTLDx14BM4mBq1bRf1vFd0Ts
    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    url = urllib.url2pathname(url)
    result = simplejson.load(urllib.urlopen(url))

    data = []
    geometry = [s['geometry'] for s in result['results']]

    consulta = simplejson.dumps(geometry, indent=2)
    return HttpResponse(consulta, content_type="application/json")
