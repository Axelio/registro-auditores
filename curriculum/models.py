# -*- coding: UTF8 -*-
from django.db import models
from personas.models import Persona
from lugares.models import Estado, Institucion

# Modelos para construir el Curriculum

class Certificacion(models.Model):
    '''
    Modelo que registra cada uno de los certificados de la persona
    '''
    persona = models.ForeignKey(Persona)
    titulo = models.CharField(max_length=500, verbose_name=u'título')
    codigo_certificacion = models.CharField(max_length=30)
    institucion = models.ForeignKey(Institucion, verbose_name=u'institución')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    horas = models.IntegerField()
    lugar = models.ForeignKey(Estado)
    class Meta:
        db_table = u'certificacion'
        verbose_name = u'certificación'
        verbose_name_plural = 'certificaciones'
    def __unicode__(self):
        return u'%s %s %s' %(self.persona, self.titulo)
