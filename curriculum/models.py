# -*- coding: UTF8 -*-
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, DELETION, CHANGE
from django.contrib import messages
from django.core.mail import send_mail

from personas.models import Persona
from lugares.models import Estado, Institucion, Pais
from authentication.models import UserProfile, Mensaje
from auditores_suscerte import settings

import datetime

# Modelos para construir el Curriculum

NIVELES_COMPETENCIA = (
        ('experto', 'Experto'),
        ('alto', 'Alto'),
        ('medio', 'Medio'),
        ('basico', u'Básico'),
        ('nada', 'Nada'),
        )


class Certificacion(models.Model):
    '''
    Modelo que registra cada uno de
    los certificados de la persona
    '''
    persona = models.ForeignKey(Persona)
    titulo = models.CharField(max_length=500, verbose_name=u'título')
    codigo_certificacion = models.CharField(max_length=30,
            blank=True,
            verbose_name=u'código de certificación')
    institucion = models.ForeignKey(Institucion, verbose_name=u'institución')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True)
    pais = models.ForeignKey(Pais)

    class Meta:
        db_table = u'certificacion'
        verbose_name = u'certificación'
        verbose_name_plural = 'certificaciones'

    def __unicode__(self):
        return u'%s - %s' % (self.persona, self.titulo)


class Tiempo(models.Model):
    dia = models.DateField()
    hora = models.TimeField()

    class Meta:
        abstract = True


class Cita(Tiempo):
    usuario = models.ForeignKey(UserProfile)
    cita_fijada = models.BooleanField(default=False)

    class Meta:
        db_table = u'cita'

    def __unicode__(self):
        return u'%s' % (self.usuario)


@receiver(post_save, sender=Cita)
def post_save_cita(sender, **kwargs):
    '''
    Función para procesar antes de guardar en base de datos
    '''
    cita = kwargs['instance']

    citas = Cita.objects.filter(
            usuario=cita.usuario,
            dia=cita.dia,
            hora=cita.hora,
            )

    destinatarios = []

    if cita.cita_fijada == True and settings.NOTIFY == True:
        # Si hay una fecha fijada, se envía un mail
        # al usuario indicándole la fecha definitiva
        asunto = u'%sFijada fecha para cita' % (settings.EMAIL_SUBJECT_PREFIX)
        emisor = settings.EMAIL_HOST_USER
        destinatarios = [cita.usuario.user.email]

        # Búsqueda de fecha definitiva:
        fecha_fijada = ''
        fecha_fijada = '%s a las %s' % (cita.dia, cita.hora)

        # Envío de mail
        mensaje = Mensaje.objects.get(caso='Postulación de cita')

        # Sustitución de variables clave y usuario
        mensaje = mensaje.mensaje.replace('<fecha>','%s'%(fecha_fijada))

        send_mail(subject=asunto, message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=destinatarios)


class ListaIdiomas(models.Model):
    nombre = models.CharField(max_length=20)

    class Meta:
        db_table = u'lista_idiomas'
        verbose_name = 'lista de idiomas'
        verbose_name_plural = 'lista de idiomas'

    def __unicode__(self):
        return u'%s' % (self.nombre)

NIVEL_IDIOMA = (('4', 'Fluido'),
                ('3', 'Alto'),
                ('2', 'Medio'),
                ('1', 'Bajo'))


class Idioma(models.Model):
    persona = models.ForeignKey(Persona)
    idioma = models.ForeignKey('ListaIdiomas')
    nivel_leido = models.CharField(max_length=10,
            choices=NIVEL_IDIOMA,
            verbose_name=u'nivel de lectura')
    nivel_escrito = models.CharField(max_length=10,
            choices=NIVEL_IDIOMA,
            verbose_name=u'nivel de escritura')
    nivel_hablado = models.CharField(max_length=10,
            choices=NIVEL_IDIOMA,
            verbose_name=u'nivel de conversación')

    class Meta:
        db_table = u'idioma'
        ordering = ('-idioma',)

    def __unicode__(self):
        return u'%s' % (self.idioma)


class Conocimiento(models.Model):
    usuario = models.ForeignKey(UserProfile)
    otros_conocimientos = models.TextField(
            help_text=u'Escriba aquí los conocimientos extras')

    class Meta:
        db_table = 'conocimiento'

    def __unicode__(self):
        return u'%s' % (self.otros_conocimientos)


class Habilidad(models.Model):
    usuario = models.ForeignKey(UserProfile)
    habilidad = models.CharField(max_length=50)

    class Meta:
        db_table = 'habilidad'
        verbose_name_plural = 'habilidades'

    def __unicode__(self):
        return u'%s' % (self.habilidad)

TIPO_CONOCIMIENTO = (
            ('academico', u'Nivel Académico'),
            ('basico', u'Conocimiento Básico'),
            ('complementario', 'Conocimiento Complementario'),
            ('requerido', 'Conocimiento Requerido'))


class TipoCompetencia(models.Model):
    nombre = models.CharField(max_length=50)
    puntaje_maximo = models.FloatField(verbose_name=u'puntaje máximo')

    class Meta:
        db_table = 'tipo_competencia'
        verbose_name = 'tipo de competencia'
        verbose_name_plural = 'tipos de competencias'

    def __unicode__(self):
        return u'%s' % (self.nombre)

TIPOS_PUNTAJE = (('int', 'Cantidades'), ('float', 'Puntos'))


class ListaCompetencia(models.Model):
    nombre = models.CharField(max_length=200)
    tipo = models.ForeignKey(TipoCompetencia)
    puntaje_maximo = models.FloatField(verbose_name=u'puntaje máximo')
    puntaje_minimo = models.FloatField(verbose_name=u'puntaje mínimo',
            default=0.0)
    tipo_puntaje = models.CharField(max_length=10, choices=TIPOS_PUNTAJE)

    class Meta:
        db_table = 'lista_competencia'
        verbose_name = 'lista de competancia'
        verbose_name_plural = 'lista de competancias'

    def __unicode__(self):
        return u'%s' % (self.nombre)


class Competencia(models.Model):
    usuario = models.ForeignKey(UserProfile)
    tipo = models.ForeignKey('TipoCompetencia')
    puntaje = models.FloatField()
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'competencia'

    def __unicode__(self):
        return u'%s' % (self.tipo)


class Aprobacion(models.Model):
    '''
    Clase para definir puntajes de aprobación
    tanto para evaluación como entrevista
    '''
    instrumento = models.ForeignKey('Instrumento')
    puntaje_aprobatorio = models.FloatField()
    puntaje_total = models.FloatField(verbose_name=u'puntaje máximo')
    fecha = models.DateField(auto_now_add=True, verbose_name='fijada')

    class Meta:
        db_table = 'aprobacion'
        verbose_name = u'aprobación'
        verbose_name_plural = 'aprobaciones'
        get_latest_by = 'fecha'

    def __unicode__(self):
        return u'%s' %(self.instrumento)


class Instrumento(models.Model):
    nombre = models.CharField(max_length=30,
            help_text=u'Ej: Inscripción, renovación, etc.')
    ambito = models.ForeignKey('Ambito', verbose_name=u'ámbito')

    class Meta:
        db_table = u'instrumento'

    def __unicode__(self):
        return u'%s' % (self.nombre)


class Evaluacion(models.Model):
    usuario = models.ForeignKey(UserProfile)
    tipo_prueba = models.ForeignKey('Instrumento')
    puntaje = models.FloatField()
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'evaluacion'
        verbose_name = u'evaluación'
        verbose_name_plural = u'evaluaciones'

    def __unicode__(self):
        return u'%s' % (self.usuario)


class Curso(models.Model):
    usuario = models.ForeignKey(UserProfile)
    titulo = models.CharField(max_length=150, verbose_name=u'título')
    institucion = models.ForeignKey(Institucion, verbose_name=u'institución')
    estado = models.ForeignKey(Estado)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    horas = models.PositiveIntegerField()

    class Meta:
        db_table = 'curso'

    def __unicode__(self):
        return u'%s: %s' % (self.usuario, self.titulo)


class Laboral(models.Model):
    usuario = models.ForeignKey(UserProfile)
    empresa = models.CharField(max_length=100)
    sector = models.CharField(max_length=60,
            help_text=u'Financiero, Industrial, Tecnológico, entre otros.')
    estado = models.ForeignKey(Estado)
    telefono = models.CharField(max_length=15, verbose_name=u'teléfono')
    cargo = models.CharField(max_length=60)
    funcion = models.TextField(verbose_name=u'función',
            help_text=u'indique la función o funciones que desempeñaba')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True)
    trabajo_actual = models.BooleanField(default=False)
    retiro = models.CharField(max_length=60, verbose_name=u'razón de retiro')
    direccion_empresa = models.TextField(verbose_name=u'dirección de empresa')

    class Meta:
        db_table = 'laboral'
        verbose_name_plural = 'laborales'

    def __unicode__(self):
        return u'%s: %s' % (self.usuario, self.empresa)


class Educacion(models.Model):
    persona = models.ForeignKey(Persona)
    titulo = models.CharField(max_length=50,
            help_text=u'título académico que obtuvo',
            verbose_name=u'título académico')
    institucion = models.ForeignKey(Institucion,
            help_text=u'indique la institución en la cual participó',
            verbose_name=u'institución')
    tipo = models.ForeignKey('TipoEducacion',
            verbose_name=u'nivel académico')
    fecha_inicio = models.DateField(help_text=u'fecha en la que inició')
    fecha_fin = models.DateField(help_text=u'fecha en la que terminó')

    class Meta:
        db_table = 'educacion'
        verbose_name = u'educación'
        verbose_name_plural = u'educaciones'

    def __unicode__(self):
        return u'%s: %s (%s)' % (self.persona, self.institucion, self.titulo)


class TipoEducacion(models.Model):
    tipo = models.CharField(max_length=30,
            help_text=u'Ej: Pregrado, Doctorado, Maestría, entre otros.')

    class Meta:
        db_table = u'tipo_educacion'
        verbose_name = u'tipos de educación'
        verbose_name_plural = 'tipos de educaciones'

    def __unicode__(self):
        return u'%s' % (self.tipo)


class Ambito(models.Model):
    '''
    Contiene el ámbito de un proceso: inscripción, renovación, etc.
    '''
    tipo = models.CharField(max_length=30,
            help_text=u'Ej: Inscripción, renovación, etc.')

    class Meta:
        db_table = u'ambito'
        verbose_name = u'ámbito'

    def __unicode__(self):
        return u'%s' % (self.tipo)
