from django.shortcuts import render
from django.views.generic import ListView

from .models import Ubicacion


class MapaListView(ListView):

    model = Ubicacion
    context_object_name = 'latest_question_list'
    template_name = 'mapa.html'

    def get_queryset(self):
        return Ubicacion.objects.order_by('-id')
