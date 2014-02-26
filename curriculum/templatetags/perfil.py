# -*- coding: utf-8 -*-
from django.template import Library 
from django.utils.html import format_html
from curriculum.models import NIVELES_COMPETENCIA, Competencia

register = Library()     

@register.filter(name="nivel_elegido", is_safe=True)
def nivel_elegido(competencia_id, persona):

    texto = ''
    seleccionado = ''
    competencia = Competencia.objects.get(usuario=persona.userprofile, competencia = competencia_id)
    nivel_guardado = competencia.nivel

    import pdb
    #pdb.set_trace()
    for nivel in NIVELES_COMPETENCIA:
        if nivel[0] == nivel_guardado:
            seleccionado = 'selected="selected"'
        else:
            seleccionado = ''
        texto = texto + '<option value="'+ nivel[0] +'_'+ str(competencia_id) +'" '+ seleccionado +'>'+ nivel[1] +'</option>'
    return format_html(texto)
register.filter(nivel_elegido)

