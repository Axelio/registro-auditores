# -*- coding: UTF8 -*-
from django.db import models
from personas.models import Persona
from lugares.models import Estado, Institucion
from auth.models import UserProfile


# Modelos para construir el Curriculum

class Certificacion(models.Model):
    '''
    Modelo que registra cada uno de los certificados de la persona
    '''
    persona = models.ForeignKey(Persona)
    titulo = models.CharField(max_length=500, verbose_name=u'título')
    codigo_certificacion = models.CharField(max_length=30, verbose_name=u'código de certificación')
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
        return u'%s - %s' %(self.persona, self.titulo)

class Cita(models.Model):
    usuario = models.ForeignKey(Persona)
    primera_cita = models.DateTimeField()
    segunda_cita = models.DateTimeField()
    tercera_cita = models.DateTimeField()
    cita_fijada = models.DateTimeField()
    class Meta:
        db_table = u'cita'
    def __unicode__(self):
        return u'%s - %s' %(self.usuario, self.cita_fijada)

class ListaIdiomas(models.Model):
    nombre = models.CharField(max_length=20)
    class Meta:
        db_table = u'lista_idiomas'
        verbose_name = 'lista de idiomas'
        verbose_name_plural = 'lista de idiomas'
    def __unicode__(self):
        return u'%s' %(self.nombre)

NIVEL_IDIOMA = (
                ('4','Nativo'),
                ('3','Fluido'),
                ('2','Medio'),
                ('1','Bajo')
                )

class Idioma(models.Model):
    conocimiento = models.ForeignKey('Conocimiento')
    idioma = models.ForeignKey('ListaIdiomas')
    nivel_leido = models.CharField(max_length=10, choices=NIVEL_IDIOMA)
    nivel_escrito = models.CharField(max_length=10, choices=NIVEL_IDIOMA)
    nivel_hablado = models.CharField(max_length=10, choices=NIVEL_IDIOMA)
    class Meta:
        db_table = u'idioma'
    def __unicode__(self):
        return u'%s' %(sel.idioma)

class Conocimiento(models.Model):
    usuario = models.ForeignKey(UserProfile)
    habilidades = models.TextField()
    otros_conocimientos = models.TextField(help_text=u'Escriba aquí los conocimientos que no se contemplan en las competencias profesionales')
    class Meta:
        db_table = 'conocimiento'
    def __unicode__(self):
        return u'%s' %(usuario)

TIPO_CONOCIMIENTO = (
            ('academico',u'Nivel Académico'),
            ('basico',u'Conocimiento Básico'),
            ('complementario','Conocimiento Complementario'),
            ('requerido','Conocimiento Requerido')
        )

class ListaCompetencia(models.Model):
    nombre = models.CharField(max_length=200)
    class Meta:
        db_table = 'lista_competencia'
        verbose_name = 'lista de competancia'
        verbose_name_plural = 'lista de competancias'
    def __unicode__(self):
        return u'%s' %(self.nombre)


class Competencia(models.Model):
    conocimiento = models.ForeignKey('Conocimiento', blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CONOCIMIENTO)
    competencia = models.ForeignKey('ListaCompetencia', unique=True)
    puntaje = models.DecimalField(decimal_places=1, max_digits=2)
    class Meta:
        db_table = 'competencia'
    def __unicode__(self):
        return u'%s' %(self.competencia)

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
        return u'%s: %s' %(self.usuario, self.titulo)

class Laboral(models.Model):
    usuario = models.ForeignKey(UserProfile)
    empresa = models.CharField(max_length=100)
    sector = models.CharField(max_length=60)
    estado = models.ForeignKey(Estado)
    telefono = models.CharField(max_length=15, verbose_name=u'teléfono')
    cargo = models.CharField(max_length=60)
    funcion = models.TextField(verbose_name=u'función', help_text=u'indique la función o funciones que desempeñaba')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True)
    trabajo_actual = models.BooleanField()
    retiro = models.CharField(max_length=60, verbose_name=u'razón de retiro')
    direccion_empresa = models.TextField(verbose_name=u'dirección de empresa')
    class Meta:
        db_table = 'laboral'
        verbose_name_plural = 'laborales'
    def __unicode__(self):
        return u'%s: %s' %(self.usuario, self.empresa)

class Educacion(models.Model):
    persona = models.ForeignKey(Persona)
    titulo = models.CharField(max_length=50, help_text=u'título universitario que obtuvo', verbose_name=u'título')
    institucion = models.ForeignKey(Institucion, help_text=u'indique la institución en la cual participó', verbose_name=u'institución')
    carrera = models.CharField(max_length=50, help_text=u'carrera que estudió')
    tipo = models.ForeignKey('TipoEducacion')
    fecha_inicio = models.DateField(help_text=u'fecha en la que inició')
    fecha_fin = models.DateField(help_text=u'fecha en la que terminó')
    class Meta:
        db_table = 'educacion'
        verbose_name=u'educación'
        verbose_name_plural=u'educaciones'
    def __unicode__(self):
        return u'%s: %s (%s)' %(self.persona, self.institucion, self.carrera)

class TipoEducacion(models.Model):
    tipo= models.CharField(max_length=20, help_text=u'Ej: Pregrado, Doctorado, Maestría, entre otros.')
    class Meta:
        db_table = u'tipo_educacion'
        verbose_name = u'tipos de educación'
        verbose_name_plural = 'tipos de educaciones'
    def __unicode__(self):
        return u'%s'%(self.tipo)
