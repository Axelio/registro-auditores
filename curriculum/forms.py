# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.shortcuts import render_to_response
from django.forms import ModelForm, DateInput, TextInput, Textarea, Select
from django.forms.extras.widgets import SelectDateWidget
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.admin import widgets
from authentication.models import User
from curriculum.models import (
        Certificacion, Conocimiento, Competencia,
        ListaCompetencia, Educacion, Laboral,
        Competencia, Habilidad, Idioma, Cita,
        Curso, Evaluacion, Aprobacion,
)
from lugares.models import Institucion
from lib.funciones import fecha_futura, fecha_pasada, fechas_superiores
import datetime

NIVELES_COMPTETENCIA = (
        ('experto', 'Experto'),
        ('alto', 'Alto'),
        ('medio', 'Medio'),
        ('basico', u'Básico'),
        ('nada', 'Nada'),
        )


class FijarCitaForm(forms.ModelForm):
    '''
    Formulario para la fijación de una fecha para la entrevista
    '''
    
    class Meta:
        model = Cita
        fields = ('cita_fijada',)
        widgets = {
            'cita_fijada': Select(
                attrs={
                    'required': 'required',
                   }
                )
            }


class CitasForm(forms.Form):
    '''
    Formulario para la selección de fechas tentativas para la cita
    '''
    fecha = forms.DateField(widget=forms.TextInput(
        attrs={
            'class':'ink-datepicker',
            'data-format': 'dd/mm/yyyy',
            'data-position':'bottom'
            }
        ))
    hora = forms.TimeField(widget=forms.TextInput(attrs={'class':'timepicker'}))

    def clean(self):
        '''
        Función para validaciones generales del modelo Cita
        '''

        fecha = self.cleaned_data['fecha']
        fecha_actual = datetime.date.today()

        # La fecha elegida no puede ser menor a la actual:
        if fecha < fecha_actual:
            raise forms.ValidationError(u'La fecha elegida \
                                        no puede ser menor a la actual')

        # Si fecha es pasada (función en lib/funciones.py)
        if fecha_pasada(fecha):
            error = u'La fecha no puede ser \
                    menor ni igual al día de hoy'
            raise forms.ValidationError(error)

        return self.cleaned_data


class CompetenciaPruebaForm(forms.ModelForm):
    '''
    Formulario para el ingreso de Competencias en el panel administrativo
    '''

    class Meta:
        model = Competencia
        exclude = ('usuario', 'competencia')


class CompetenciaForm(forms.ModelForm):
    '''
    Formulario para el ingreso de Competencias en el panel administrativo
    '''

    class Meta:
        model = Competencia
        exclude = ('usuario',)


class HabilidadForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de Habilidades
    '''

    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario
        model = Habilidad
        exclude = ('usuario',)


class ConocimientoForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de Conocimientos
    '''

    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario
        model = Conocimiento
        exclude = ('usuario',)


class IdiomaForm(forms.ModelForm):
    '''
    Formulario para el ingreso de Idiomas
    '''

    class Meta:
        # Se dsetermina cuál es el modelo al que va a referirse el formulario
        model = Idioma
        exclude = ('persona',)


class ConocimientoAdminForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de Conocimientos en el admin
    '''

    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario
        model = Conocimiento
        fields = ['usuario', 'otros_conocimientos']


class CursoForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de certificaciones
    '''

    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario
        model = Curso
        exclude = ('usuario',)
        widgets = {
            'horas': TextInput(
                attrs={
                    'type': 'number',
                    'required': 'required',
                    'min': 0}),
            'fecha_inicio': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'data-position': 'bottom'}),
            'fecha_fin': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'data-position': 'bottom'}),

        }

    def clean_fecha_inicio(self):
        '''
        Función para validar el campo de fecha inicio
        '''
        # Fecha actual
        error = u'La fecha de inicio no puede ser mayor ni igual a hoy'

        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(error)

        error = u'La fecha de inicio no puede ser mayor a la final'
        if fechas_superiores(self.cleaned_data['fecha_inicio'],
                self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(error)
        return self.cleaned_data['fecha_inicio']

    def clean_fecha_fin(self):
        '''
        Función para validar el campo de fecha fin
        '''
        # Fecha actual
        error = u'La fecha final no puede ser mayor ni igual a hoy'

        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_fin']):
            raise forms.ValidationError(error)

        return self.cleaned_data['fecha_fin']


class CertificacionForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de certificaciones
    '''

    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario
        model = Certificacion
        exclude = ('persona',)
        widgets = {
            'fecha_inicio': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'data-position': 'bottom'}),
            'fecha_fin': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'data-position': 'bottom'}),
        }

    def clean_fecha_inicio(self):
        '''
        Función para validar el campo de fecha inicio
        '''
        # Fecha actual
        error = u'La fecha de inicio no puede ser mayor ni igual a hoy'

        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(error)

        error = u'La fecha de inicio no puede ser mayor a la final'
        if fechas_superiores(self.cleaned_data['fecha_inicio'],
                self.cleaned_data['fecha_fin']):
            raise forms.ValidationError(error)
        return self.cleaned_data['fecha_inicio']

    def clean_fecha_fin(self):
        '''
        Función para validar el campo de fecha fin
        '''
        # Fecha actual
        error = u'La fecha final no puede ser mayor ni igual a hoy'

        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_fin']):
            raise forms.ValidationError(error)

        return self.cleaned_data['fecha_fin']


class EducacionForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de Educacion
    '''

    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario
        model = Educacion
        exclude = ('persona',)
        widgets = {
            'titulo': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Título obtenido'}),
            'carrera': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': 'Carrera estudiada'}),
            'fecha_inicio': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de inicio',
                    'data-position': 'bottom'}),
            'fecha_fin': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de culminación',
                    'data-position': 'bottom'}),
        }

    def clean_fecha_inicio(self):
        '''
        Función para validar el campo de fecha inicio
        '''
        # Fecha actual
        error = u'La fecha de inicio no puede ser mayor ni igual a hoy'

        # Si fecha_fin es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(error)

        error = u'La fecha de inicio no puede ser mayor a la final'
        if fechas_superiores(self.cleaned_data['fecha_inicio'],
                self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(error)
        return self.cleaned_data['fecha_inicio']

    def clean_fecha_fin(self):
        '''
        Función para validar el campo de fecha inicio
        '''
        # Fecha actual
        error = u'La fecha fin no puede ser mayor ni igual a hoy'

        # Si fecha_fin es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_fin']):
            raise forms.ValidationError(error)
        return self.cleaned_data['fecha_fin']


class EvaluacionForm(forms.ModelForm):
    '''
    Formulario para el ingreso de Competencias en el panel administrativo
    '''

    class Meta:
        model = Evaluacion
        exclude = ('usuario', 'tipo_prueba')
        widgets = {
            'puntaje': TextInput(
                attrs={
                    'type': 'number',
                    'required': 'required',
                    'min': '0'}),
                }


class LaboralForm(forms.ModelForm):
    '''
    Formulario general para Laboral
    '''

    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario
        model = Laboral
        exclude = ('usuario', 'trabajo_actual')
        widgets = {
            'empresa': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'placeholder': 'Empresa en la que laboró'}),

            'sector': TextInput(
                attrs={
                    'type': 'text',
                    'placeholder': 'Sector desempeñado'}),

            'telefono': TextInput(
                attrs={
                    'type': 'text',
                    'placeholder': 'Número telefónico de trabajo'}),

            'cargo': TextInput(
                attrs={
                    'type': 'text',
                    'placeholder': 'Cargo trabajado'}),

            'funcion': Textarea(
                attrs={
                    'type': 'text',
                    'placeholder': 'Funciones desempeñadas'}),

            'fecha_inicio': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de inicio',
                    'data-position': 'bottom'}),

            'fecha_fin': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de culminación',
                    'data-position': 'bottom'}),

            'retiro': TextInput(
                attrs={
                    'type': 'text',
                    'placeholder': 'Razón de retiro'}),

            'direccion_empresa': Textarea(
                attrs={
                    'type': 'text',
                    'placeholder': 'Dirección de la empresa'}),
        }

    def clean_fecha_inicio(self):
        '''
        Función para validar el campo de fecha inicio
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
        error = u'La fecha de inicio no puede ser mayor ni igual a hoy'

        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(error)

        error = u'La fecha de inicio no puede ser mayor a la final'
        if fechas_superiores(self.cleaned_data['fecha_inicio'],
                self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(error)
        return self.cleaned_data['fecha_inicio']

    def clean_fecha_fin(self):
        '''
        Función para validar el campo de fecha fin
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
        error = u'La fecha final no puede ser mayor ni igual a hoy'

        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_fin']):
            raise forms.ValidationError(error)
        return self.cleaned_data['fecha_fin']


class EmailForm(forms.Form):
    email = forms.EmailField()
    email2 = forms.EmailField(help_text='Por favor, ingrese el \
                              email nuevamente',
                              label=u'Repita email')

    def clean(self):
        '''
        Función para validar que el correo introducido no exista
        en la base de datos actualmente
        '''
        if User.objects.filter(Q(username=self.cleaned_data['email']) | Q(email=self.cleaned_data['email'])):
            raise forms.ValidationError(u'El correo electrónico "%s" \
                    ya existe en la base de datos, por favor, verifique \
                    y vuelva a intentarlo' % (self.cleaned_data['email']))
        return self.cleaned_data

    def clean_email2(self):
        '''
        Función para validar que ambos correos electrónicos sean iguales
        '''
        if self.cleaned_data['email'] != self.cleaned_data['email2']:
            raise forms.ValidationError(u'Los correos electrónicos no \
                                        coinciden, por favor, revise \
                                        y vuelva a intentarlo')
        return self.cleaned_data
