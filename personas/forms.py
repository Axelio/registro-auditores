# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField
from lib.funciones import fecha_futura
from personas.models import Persona, Auditor
import datetime

TELEFONO_PUBLICO = (('movil', u'Teléfono móvil'),
                    ('fijo', u'Teléfono fijo'),
                    ('oficina', u'Teléfono de oficina'),
                    )


class EditarPersonaForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de personas
    '''

    class Meta:
        # Se determina cuál es el modelo al que va a utilizar
        model = Persona
        exclude = ('cedula', 'email')

        widgets = {
            'primer_nombre': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Primer nombre del solicitante'}),
            'segundo_nombre': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': 'Segundo nombre del solicitante'}),
            'primer_apellido': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Primer apellidos del solicitante'}),
            'segundo_apellido': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': 'Segundo apellidos del solicitante'}),
            'direccion': Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Dirección del solicitante'}),
            'fecha_nacimiento': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de nacimiento'}),
            'tlf_reside': TextInput(
                attrs={
                    'max': '9999999999',
                    'type': 'text',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': u'Teléfono de residencia'}),
            'tlf_movil': TextInput(
                attrs={
                    'max': '9999999999',
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': u'Teléfono móvil'}),
            'tlf_oficina': TextInput(
                attrs={
                    'max': '9999999999',
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': u'Teléfono de oficina'}),
        }

    def clean_fecha_nacimiento(self):
        '''
        Función para validar el campo de fecha de nacimiento
        '''
        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_nacimiento']):
            error = u'La fecha de nacimiento no '
            error += u'puede ser mayor ni igual al día de hoy'
            raise forms.ValidationError(error)
        return self.cleaned_data['fecha_nacimiento']


class PersonaForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de personas
    '''

    captcha = ReCaptchaField()

    class Meta:
        # Se determina cuál es el modelo al que va a utilizar
        model = Persona
        exclude = ('email',)

        widgets = {
            'cedula': TextInput(
                attrs={
                    'type': 'number',
                    'min': 0,
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Cédula de Identidad'}),
            'primer_nombre': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Primer nombre del solicitante'}),
            'segundo_nombre': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': 'Segundo nombre del solicitante'}),
            'primer_apellido': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Primer apellidos del solicitante'}),
            'segundo_apellido': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': 'Segundo apellidos del solicitante'}),
            'direccion': Textarea(
                attrs={
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Dirección del solicitante'}),
            'fecha_nacimiento': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-position': 'bottom',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de nacimiento',
                    'id':'popupDatepicker'}),
            'tlf_reside': TextInput(
                attrs={
                    'type': 'number',
                    'min': 0,
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': u'Teléfono de residencia'}),
            'tlf_movil': TextInput(
                attrs={
                    'type': 'number',
                    'min': 0,
                    'class': 'form-control',
                    'placeholder': u'Teléfono móvil'}),
            'tlf_oficina': TextInput(
                attrs={
                    'type': 'number',
                    'min': 0,
                    'class': 'form-control',
                    'placeholder': u'Teléfono de oficina'}),
        }

    def clean(self):
        cedula = self.cleaned_data['cedula']

        # Revisar si la cédula coincide con alguna otra en la base de datos 
        if Persona.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError(u'Esta persona ya se encuentra \
                                        registrada con esa cédula.')

        return self.cleaned_data

    def clean_fecha_nacimiento(self):
        '''
        Función para validar el campo de fecha de nacimiento
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_nacimiento']):
            error = u'La fecha de nacimiento '
            error += u'no puede ser mayor ni igual al día de hoy'
            raise forms.ValidationError(error)
        return self.cleaned_data['fecha_nacimiento']


class AcreditacionForm(forms.ModelForm):
    '''
    Clase para definir el formulario para 
    acreditar a un auditor
    '''
    
    class Meta:
        # Se determina cuál es el modelo al que va a utilizar
        model = Auditor
        fields = ('observacion',)

        widgets = {
            'observacion': Textarea(
                attrs={
                    'required': 'required',
                    }
                )
             }
