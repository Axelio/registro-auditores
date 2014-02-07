# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from curriculum.models import *
from curriculum.forms import *
from personas.models import *
from personas.forms import *

class CurriculumView(View):
    '''
    Clase para postulación de currículum
    '''
    template='curriculum/postulacion.html'
    persona_form = PersonaForm() 

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'persona_form':persona_form})

    def get(self, request, *args, **kwargs):
        # persona = self.formulario
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )
