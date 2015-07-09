# -*- coding: utf-8 -*-
from django.template import Library
from django.utils.html import format_html
from authentication.models import User
from curriculum.models import Aprobacion
from curriculum.models import NIVEL_IDIOMA
from curriculum.models import (NIVELES_COMPETENCIA,
    Competencia, ListaCompetencia, Evaluacion, Competencia,
    Cita)

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


@register.filter(name="puntaje_limite", is_safe=True)
def puntaje_limite(competencia_id):
    '''
    Función para limitar el puntaje
    segun la opcion que tenga
    '''
    competencia = ListaCompetencia.objects.get(id=competencia_id)
    puntos = []
    puntos.append(0.0)
    puntaje = 0.0

    while puntaje < competencia.puntaje_maximo:
        puntaje = puntaje + 0.5
        puntos.append(puntaje)

    return puntos
register.filter(puntaje_limite)


@register.filter(name="puntaje_entrevistado", is_safe=True)
def puntaje_entrevistado(usuario_id):
    '''
    Función para determinar 
    el puntaje de un usuario
    '''
    usuario = User.objects.get(id=usuario_id)
    competencias = usuario.get_profile().competencia_set.get_query_set()
    ultima_competencia = competencias.latest('fecha')
    competencias = competencias.filter(fecha=ultima_competencia.fecha)

    if competencias.exists():
        puntaje = 0.0
        for competencia in competencias:
            puntaje += competencia.puntaje

        return puntaje
register.filter(puntaje_entrevistado)


@register.filter(name="aprobado", is_safe=True)
def aprobado(usuario_id):
    '''
    Función para determinar si
    el aspirante aprobó o no entrevista y evaluación
    '''
    usuario = User.objects.get(id=usuario_id)

    if competencias.exists():
        aprobacion = Aprobacion.objects.last()

        # Si el puntaje de la persona es menor
        # que la aprobatoria, se retorna False
        if usuario.get_profile().evaluacion_set.get_query_set().last().puntaje < aprobacion.evaluacion_aprobatoria: 
            return False

        competencias = usuario.get_profile().competencia_set.get_query_set()
        ultima_competencia = competencias.latest('fecha')
        competencias = competencias.filter(fecha=ultima_competencia.fecha)

        # Si el puntaje de la persona NO es menor
        # que la aprobatoria, se cambia aprobado a True
        if not puntaje_entrevistado(usuario_id) < aprobacion.entrevista_aprobatoria:
            return True
        else:
            return False
register.filter(aprobado)


@register.filter(name="obtener_idioma", is_safe=True)
def obtener_idioma(key):
    for nivel in NIVEL_IDIOMA:
        if nivel[0] == key:
            return nivel[1]
register.filter(obtener_idioma)
