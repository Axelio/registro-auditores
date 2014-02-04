# -*- coding: UTF8 -*-
from django.db import models
from lugares.models import *

# Modelo de Persona
        
ESTADO_CIVIL = (('s','Soltero'),
                ('c','Casado'),
                ('d','Divorciado'),
                ('v','Viudo')
               )

TELEFONO_PUBLICO = (('movil',u'Teléfono móvil'),
                    ('fijo',u'Teléfono fijo'),
                    ('oficina',u'Teléfono de oficina'),
                    )

class Persona(models.Model):
    '''
    Tabla de registro de personas
    '''
    cedula = models.CharField(max_length=50,unique=True,verbose_name=u'Cédula')
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50,blank=True)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50,blank=True)
    genero = models.IntegerField(choices=((0,'Masculino'),(1,'Femenino')),default=0,verbose_name=u'género')
    direccion = models.TextField(verbose_name=u'dirección',blank=True)
    fecha_nacimiento = models.DateField()
    email = models.EmailField()
    tlf_fijo = models.CharField(max_length=15, verbose_name=u'teléfono fijo')
    tlf_movil = models.CharField(max_length=15, blank=True, verbose_name=u'teléfono móvil')
    tlf_oficina = models.CharField(max_length=15, blank=True, verbose_name=u'teléfono de oficina')
    tlf_publico = models.CharField(choices=TELEFONO_PUBLICO, max_length=10, help_text=u'Seleccione el teléfono que establecerá como público', default='fijo', verbose_name=u'teléfono público')
    reside = models.ForeignKey(Estado, help_text=u'Estado de residencia')
    estado_civil = models.CharField(choices=ESTADO_CIVIL, max_length=15)
    class Meta:
        db_table = u'personas'
        verbose_name = "persona"
    def __unicode__(self):
        return u'%s %s %s' %(self.cedula, self.primer_apellido, self.primer_nombre)
