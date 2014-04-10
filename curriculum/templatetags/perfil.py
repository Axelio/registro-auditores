# -*- coding: utf-8 -*-
from django.template import Library
from django.utils.html import format_html
from curriculum.models import NIVELES_COMPETENCIA, Competencia

register = Library()


@register.filter(name="nivel_elegido", is_safe=True)
def nivel_elegido(competencia_id, persona):

    texto = ''
    seleccionado = ''
    competencia = Competencia.objects.get(
            usuario=persona.userprofile,
            competencia=competencia_id)
    nivel_guardado = competencia.nivel

    for nivel in NIVELES_COMPETENCIA:
        if nivel[0] == nivel_guardado:
            seleccionado = 'selected="selected"'
        else:
            seleccionado = ''
        texto = texto + '<option value="%s_%s" %s> %s </option>' % (
                nivel[0], competencia_id, seleccionado, nivel[1])
    return format_html(texto)
register.filter(nivel_elegido)


@register.filter(name="mail_antispam", is_safe=True)
def mail_antispam(email):
    '''
    Función para cambiar el @ por un (arroba)
    y de esta forma, evitar el spam por parte de
    bots
    '''
    usuario = email.split('@')[0]
    servicio = email.split('@')[1]

    texto = usuario + ' en ' + servicio
    return texto
register.filter(mail_antispam)
