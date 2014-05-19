# -*- coding: utf-8 -*-
from django.template import Library
from django.utils.html import format_html
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


@register.filter(name="seleccionado", is_safe=True)
def seleccionado(puntaje_id, puntaje):
    '''
    Función para determinar si
    un puntaje está o no seleccionado
    '''
    if puntaje_id == puntaje:
        return "selected"
    else:
        return ""
register.filter(seleccionado)


@register.filter(name="evaluado", is_safe=True)
def evaluado(usuario_id):
    '''
    Función para determinar si
    un puntaje está o no seleccionado
    '''
    evaluaciones = Evaluacion.objects.filter(usuario__id=usuario_id)
    if evaluaciones.exists():
        return True
    else:
        return False
register.filter(evaluado)


@register.filter(name="puntaje_evaluacion", is_safe=True)
def puntaje_evaluacion(usuario_id):
    '''
    Función para determinar si
    un puntaje está o no seleccionado
    '''
    evaluaciones = Evaluacion.objects.filter(usuario__id=usuario_id)
    if evaluaciones:
        evaluaciones = evaluaciones[0]
        return evaluaciones.puntaje

register.filter(puntaje_evaluacion)


@register.filter(name="entrevistado", is_safe=True)
def entrevistado(usuario_id):
    '''
    Función para determinar si
    un puntaje está o no seleccionado
    '''
    competencias = Competencia.objects.filter(
            usuario__id=usuario_id)
    if competencias.exists():
        return True
    else:
        return False
register.filter(entrevistado)


@register.filter(name="puntaje_entrevistado", is_safe=True)
def puntaje_entrevistado(usuario_id):
    '''
    Función para determinar si
    un puntaje está o no seleccionado
    '''
    competencias = Competencia.objects.filter(
            usuario__id=usuario_id)

    puntaje = 0.0
    for competencia in competencias:
        puntaje += competencia.puntaje

    return puntaje
register.filter(puntaje_entrevistado)


@register.filter(name="citado", is_safe=True)
def citado(usuario_id):
    '''
    Función para determinar si
    la persona tiene una cita fijada
    '''
    cita = Cita.objects.filter(
            usuario__id=usuario_id)

    if cita.exists():
        cita = cita[0]

        # Si la fecha no ha sido fijada,
        # se retorna False
        if cita.cita_fijada == '':
            return False
        else:
            return True
register.filter(citado)
