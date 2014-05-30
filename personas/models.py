# -*- coding: UTF8 -*-
from django.db import models
from django.core.validators import MaxLengthValidator
from lugares.models import *

# Modelo de Persona
ESTADO_CIVIL = (('s', 'Soltero(a)'),
                ('c', 'Casado(a)'),
                ('d', 'Divorciado(a)'),
                ('v', 'Viudo(a)'))

TELEFONO_PUBLICO = (('movil', u'Teléfono móvil'),
                    ('fijo', u'Teléfono de residencia'),
                    ('oficina', u'Teléfono de oficina'),
                    )


class Persona(models.Model):
    '''
    Tabla de registro de personas
    '''
    cedula = models.CharField(
            max_length=50,
            unique=True,
            verbose_name=u'Cédula',
            help_text=u'Los datos deben ser únicamente números')
    primer_nombre = models.CharField(
            max_length=50,
            help_text='Indique su primer nombre')
    segundo_nombre = models.CharField(
            max_length=50,
            blank=True,
            help_text='Indique su segundo nombre, si posee')
    primer_apellido = models.CharField(
            max_length=50,
            help_text='Indique su primer apellido')
    segundo_apellido = models.CharField(
            max_length=50,
            blank=True,
            help_text='Indique su segundo apellido')
    genero = models.IntegerField(choices=((0, 'Masculino'),
                (1, 'Femenino')),
            default=0,
            verbose_name=u'género',
            help_text='Seleccione su género')
    reside = models.ForeignKey(Estado,
            help_text=u'Estado de residencia')
    direccion = models.TextField(
            verbose_name=u'dirección',
            blank=True,
            help_text=u'Indique dirección donde reside')
    fecha_nacimiento = models.DateField(
            blank=True,
            null=True,
            help_text='Indique su fecha de nacimiento')
    tlf_reside = models.CharField(
            max_length=15,
            verbose_name=u'teléfono de residencia',
            help_text=u'Número telefónico de residencia')
    tlf_movil = models.CharField(
            max_length=15,
            blank=True,
            verbose_name=u'teléfono móvil',
            help_text=u'Número telefónico celular')
    tlf_oficina = models.CharField(
            max_length=15,
            blank=True,
            verbose_name=u'teléfono de oficina',
            help_text=u'Número telefónico de oficina')
    tlf_contacto = models.CharField(
            choices=TELEFONO_PUBLICO,
            max_length=10,
            help_text=u'Seleccione el teléfono que establecerá \
                    el cual será contactado',
            default='fijo',
            verbose_name=u'teléfono de contacto (tome en cuenta que \
                    esta información será pública)')
    estado_civil = models.CharField(
            choices=ESTADO_CIVIL,
            max_length=15,
            blank=True,
            help_text='Señale su estado civil',
            default='s')
    email = models.EmailField(
            help_text='Indique un correo electrónico válido',
            unique=True,
            verbose_name=u'Email (tome en cuenta que \
                    esta información será pública)',
            validators=[MaxLengthValidator(2000)])

    class Meta:
        db_table = u'personas'
        verbose_name = "persona"

    def __unicode__(self):
        return u'%s %s %s' % (
                self.cedula,
                self.primer_apellido,
                self.primer_nombre)


class Auditor(models.Model):
    persona = models.ForeignKey('Persona')
    acreditado = models.BooleanField()
    fecha_acreditacion = models.DateField(
            verbose_name = u'fecha de acreditación')
    fecha_desacreditacion = models.DateField(
            verbose_name = u'fecha de desacreditación')
    observacion = models.TextField(
            help_text='Razones por la cual se acredita o desacredita al auditor',
            verbose_name=u'observación')

    class Meta:
        db_table = u'auditor'
        verbose_name = 'auditor'
        verbose_name_plural = 'auditores'

    def __unicode__(self):
        return u'%s' % (self.persona)


class CertificadoElectronico(models.Model):
    from auth.models import UserProfile
    usuario = models.ForeignKey(UserProfile)
    certificado = models.CharField(max_length=5000)

    class Meta:
        db_table = u'certificado_electonico'
        verbose_name = u'certificado electrónico'
        verbose_name_plural = u'certificados electrónicos'

    def __unicode__(self):
        return u'%s' % (self.usuario)
