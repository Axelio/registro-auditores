# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField
from lib.funciones import fecha_futura
from personas.models import Persona
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
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Dirección del solicitante'}),
            'fecha_nacimiento': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'ink-datepicker',
                    'data-format': 'dd/mm/yyyy',
                    'placeholder': 'Fecha de inicio'}),
            'tlf_reside': TextInput(
                attrs={
                    'type': 'text',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': u'Teléfono de residencia'}),
            'tlf_movil': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': u'Teléfono móvil'}),
            'tlf_oficina': TextInput(
                attrs={
                    'type': 'text',
                    'class': 'form-control',
                    'placeholder': u'Teléfono de oficina'}),
        }

    def clean_fecha_nacimiento(self):
        '''
        Función para validar el campo de fecha de nacimiento
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
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

    email2 = forms.EmailField(label='Confirme email',
            widget=TextInput(
                attrs={
                    'type': 'email',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Confirme su correo'}))
    captcha = ReCaptchaField()

    class Meta:
        # Se determina cuál es el modelo al que va a utilizar
        model = Persona

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
            'email': TextInput(
                attrs={
                    'type': 'email',
                    'required': 'required',
                    'class': 'form-control',
                    'placeholder': 'Email del solicitante'}),
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
        error = None

        email = self.cleaned_data['email']
        cedula = self.cleaned_data['cedula']

        # Revisar si la cédula coincide con alguna otra en la base de datos 
        if Persona.objects.filter(cedula=cedula).exists():
            error = u'Esta persona ya se encuentra '
            error += u'registrada con esa cédula.'

        # Revisar si el email coincide con algún otro de la base de datos
        if Persona.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
            error = u'Esta persona ya se encuentra '
            error += 'registrada con ese email.'

        # Revisar ambos mails coincidan
        if not self.cleaned_data['email'] == self.cleaned_data['email2']:
            error = u'Los correos electrónicos deben coincidir'

        if error:
            raise forms.ValidationError(error)

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
