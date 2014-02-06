# -*- coding: UTF8 -*-
from django.db import models

class Pais(models.Model):
    '''
    Modelo para la clase País
    '''
    nombre = models.CharField(max_length=50)
    class Meta:
    	db_table = u'país'
    	verbose_name = u'país'
    	verbose_name_plural = u'países'
    def __unicode__(self):
    	return "%s" % (self.nombre)

class Estado(models.Model):
    '''
    Modelo para la clase Estado
    '''
    nombre = models.CharField(max_length=100,)
    pais = models.ForeignKey(Pais,verbose_name=u'país')
    class Meta:
        db_table = u'estado'
    def __unicode__(self):
        return u'%s'%(self.nombre)

class TipoInstitucion(models.Model):
    nombre = models.CharField(max_length=20)
    class Meta:
        db_table = u'tipo_institucion'
        verbose_name = 'tipos de instituciones'
        verbose_name_plural = 'tipos de instituciones'
    def __unicode__(self):
        return u'%s'%(self.nombre)

class Institucion(models.Model):
    '''
    Modelo para la clase Estado
    '''
    nombre = models.CharField(max_length=150,)
    estado = models.ForeignKey('Estado')
    tipo = models.ForeignKey('TipoInstitucion')
    class Meta:
        db_table            = u'institucion'
        verbose_name_plural = u'instituciones'
        verbose_name        = u'institución'
    def __unicode__(self):
        return self.nombre

class Nacionalidad(models.Model):
    '''
    Modelo para la clase Nacionalidad
    '''
    nombre = models.CharField(max_length=50,)
    class Meta:
        db_table            = u'nacionalidad'
        verbose_name_plural = u'nacionalidades'
    def __unicode__(self):
        return self.nombre
