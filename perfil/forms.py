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


class EditarPerfilForm(forms.ModelForm):
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
                    'class': 'validate',
                    'id': 'first_name',
                    }),
            'segundo_nombre': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'validate',
                    'id': 'second_name',
                    }),
            'primer_apellido': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'validate',
                    'id': 'last_name',
                    }),
            'segundo_apellido': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'validate',
                    'id': 'second_last_name',
                    }),
            'direccion': Textarea(
                attrs={
                    'class': 'materialize-textarea',
                    'id': 'textarea',
                    }),
            'fecha_nacimiento': DateInput(
                attrs={
                    'type': 'date',
                    'required': 'required',
                    'class': 'datepicker',
                    }),
            'tlf_reside': TextInput(
                attrs={
                    'max': '9999999999',
                    'type': 'text',
                    'required': 'required',
                    'class': 'form-control',
                    }),
            'tlf_movil': TextInput(
                attrs={
                    'max': '9999999999',
                    'type': 'text',
                    'class': 'form-control',
                    }),
            'tlf_oficina': TextInput(
                attrs={
                    'max': '9999999999',
                    'type': 'text',
                    'class': 'form-control',
                    }),
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
