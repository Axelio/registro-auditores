# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.base import View, TemplateView
from django.core import serializers
from django.http import Http404, HttpResponse

from .models import Ubicacion

import simplejson
import urllib


class MapaListView(ListView):

    model = Ubicacion
    context_object_name = 'latest_question_list'
    template_name = 'mapa.html'

    def get_queryset(self):
        return Ubicacion.objects.order_by('-id')


GEOCODE_BASE_URL = \
        'https://maps.googleapis.com/maps/api/place/radarsearch/json'


def MapaJson(**geo_args):

    geometry = []
    epicentro = {}
    for ubicacion in Ubicacion.objects.all():
        geo_args.update({
            'location': '{0},{1}'.format(ubicacion.lat, ubicacion.lng),
            'radius': 500,
            'types': 'restaurant|cafe|food',
            'key': 'AIzaSyDoklHqzjuOTLDx14BM4mBq1bRf1vFd0Ts'
                })

        url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
        url = urllib.url2pathname(url)
        result = simplejson.load(urllib.urlopen(url))
        epicentro['epi_lat'] = float(ubicacion.lat)
        epicentro['epi_lng'] = float(ubicacion.lng)
        for resultado in result['results']:
            resultado.update(epicentro)

        geometry.append([s for s in result['results']])
    consulta = simplejson.dumps(geometry, indent=2)
    return HttpResponse(consulta, content_type="application/json")
