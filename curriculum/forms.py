# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render_to_response
from django.forms import ModelForm, TextInput, Textarea
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard.views import SessionWizardView
from lib.funciones import fecha_futura
from curriculum.models import (
        Certificacion, Conocimiento, Competencia,
        ListaCompetencia, Educacion, Laboral,
        Competencia, Habilidad, Idioma, Cita,
)
from lugares.models import Institucion
import datetime

NIVELES_COMPTETENCIA = (
        ('experto', 'Experto'),
        ('alto', 'Alto'),
        ('medio', 'Medio'),
        ('basico', u'Básico'),
        ('nada', 'Nada'),
        )


class CitasForm(forms.ModelForm):
    '''
    Formulario para la selección de fechas tentativas para la cita
    '''

    class Meta:
        model = Cita
        exclude = ('usuario', 'cita_fijada')
        widgets = {
            'primera_fecha': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de inicio',
                    'data-position': 'bottom'}),

            'segunda_fecha': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'data-position': 'bottom',
                    'placeholder': 'Fecha de inicio',
                    'data-position': 'bottom'}),

            'tercera_fecha': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de inicio',
                    'data-position': 'bottom'}),
            }

    def clean(self):
        '''
        Función para validaciones generales del modelo Cita
        '''

        primera_fecha = self.cleaned_data['primera_fecha']
        segunda_fecha = self.cleaned_data['segunda_fecha']
        tercera_fecha = self.cleaned_data['tercera_fecha']
        fecha_actual = datetime.date.today()

        # La fecha elegida no puede ser menor a la actual:
        if primera_fecha < fecha_actual:
            raise forms.ValidationError(
                    u'La fecha elegida no puede ser menor a la actual')
        if segunda_fecha < fecha_actual:
            raise forms.ValidationError(
                    u'La fecha elegida no puede ser menor a la actual')
        if tercera_fecha < fecha_actual:
            raise forms.ValidationError(
                    u'La fecha elegida no puede ser menor a la actual')

        # Ninguna fecha puede ser igual a otra
        error_fechas_iguales = u'Las fechas no se pueden repetir'
        if primera_fecha == segunda_fecha:
            raise forms.ValidationError(error_fechas_iguales)

        if primera_fecha == tercera_fecha:
            raise forms.ValidationError(error_fechas_iguales)

        if segunda_fecha == tercera_fecha:
            raise forms.ValidationError(error_fechas_iguales)

        return self.cleaned_data


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

    def clean(self):
        '''
        Función para validaciones generales del modelo Certificacion
        '''
        fecha_inicio = self.cleaned_data['fecha_inicio']
        fecha_fin = self.cleaned_data['fecha_fin']
        error = u'La fecha final no puede ser mayor ni igual al día de hoy'

        # La fecha inicial no puede ser mayor a la final:
        if fecha_inicio > fecha_fin:
            raise forms.ValidationError(error)
        return self.cleaned_data

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
        return self.cleaned_data['fecha_inicio']


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
