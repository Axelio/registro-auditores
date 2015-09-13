# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField
from lib.funciones import fecha_futura
from personas.models import Persona, Auditor
import datetime


class PersonaForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de personas
    '''

    #captcha = ReCaptchaField()
    lat = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'id': 'lat'}))
    lng = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'id': 'lng'}))


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
                    'class': 'validate',
                    }),
            'segundo_nombre': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'validate',
                    'id': 'second_name',
                    }),
            'primer_nombre': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'validate',
                    'id': 'first_name',
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
                    'type': 'number',
                    'min': 0,
                    'required': 'required',
                    'class': 'validate',
                    }),
            'tlf_movil': TextInput(
                attrs={
                    'type': 'number',
                    'min': 0,
                    'class': 'validate',
                    }),
            'tlf_oficina': TextInput(
                attrs={
                    'type': 'number',
                    'min': 0,
                    'class': 'validate',
                    }),
        }

    def clean(self):
        cedula = self.cleaned_data['cedula']

        # Revisar si la cédula coincide con alguna otra en la base de datos
        if Persona.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError(u'Esta persona ya se encuentra \
                                        registrada con esa cédula.')
        else:
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
