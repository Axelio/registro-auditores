# -*- coding: utf-8 -*-
from django import forms
from personas.models import Persona
from lib.funciones import fecha_futura
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput
import datetime

TELEFONO_PUBLICO = (('movil',u'Teléfono móvil'),
                    ('fijo',u'Teléfono fijo'),
                    ('oficina',u'Teléfono de oficina'),
                    )

class EditarPersonaForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de personas
    '''
    class Meta:
        # Se determina cuál es el modelo al que va a 
        model = Persona
        exclude = ('cedula','email')

        widgets = {
            'primer_nombre': TextInput(attrs={'type':'text','required':'required','class':'form-control','placeholder':'Primer nombre del solicitante'}),
            'segundo_nombre': TextInput(attrs={'type':'text','class':'form-control','placeholder':'Segundo nombre del solicitante'}),
            'primer_apellido': TextInput(attrs={'type':'text','required':'required','class':'form-control','placeholder':'Primer apellidos del solicitante'}),
            'segundo_apellido': TextInput(attrs={'type':'text','class':'form-control','placeholder':'Segundo apellidos del solicitante'}),
            'direccion': Textarea(attrs={'required':'required','class':'form-control','placeholder':'Dirección del solicitante'}),
            'fecha_nacimiento': TextInput(attrs={'type':'text','required':'required','class':'ink-datepicker','data-format':'dd/mm/yyyy','placeholder':'Fecha de inicio','id':'popupDatepicker'}),
            'tlf_reside': TextInput(attrs={'type':'text','required':'required','class':'form-control','placeholder':u'Teléfono de residencia del solicitante'}),
            'tlf_movil': TextInput(attrs={'type':'text','class':'form-control','placeholder':u'Teléfono móvil del solicitante'}),
            'tlf_oficina': TextInput(attrs={'type':'text','class':'form-control','placeholder':u'Teléfono de oficina del solicitante'}),
        }

    def clean_fecha_nacimiento(self):
        '''
        Función para validar el campo de fecha de nacimiento
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_nacimiento']):
            raise forms.ValidationError(u'La fecha de nacimiento no puede ser mayor ni igual al día de hoy')
        return self.cleaned_data['fecha_nacimiento']
class PersonaForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de personas
    '''
    class Meta:
        # Se determina cuál es el modelo al que va a 
        model = Persona

        widgets = {
            'cedula': TextInput(attrs={'type':'text','required':'required','class':'form-control','placeholder':'Cédula de Identidad'}),
            'primer_nombre': TextInput(attrs={'type':'text','required':'required','class':'form-control','placeholder':'Primer nombre del solicitante'}),
            'segundo_nombre': TextInput(attrs={'type':'text','class':'form-control','placeholder':'Segundo nombre del solicitante'}),
            'primer_apellido': TextInput(attrs={'type':'text','required':'required','class':'form-control','placeholder':'Primer apellidos del solicitante'}),
            'segundo_apellido': TextInput(attrs={'type':'text','class':'form-control','placeholder':'Segundo apellidos del solicitante'}),
            'direccion': Textarea(attrs={'required':'required','class':'form-control','placeholder':'Dirección del solicitante'}),
            'fecha_nacimiento': TextInput(attrs={'type':'text','required':'required','class':'form-control','placeholder':'Fecha de nacimiento','id':'popupDatepicker'}),
            'email': TextInput(attrs={'type':'email','required':'required','class':'form-control','placeholder':'Email del solicitante'}),
            'tlf_reside': TextInput(attrs={'type':'text','required':'required','class':'form-control','placeholder':u'Teléfono de residencia del solicitante'}),
            'tlf_movil': TextInput(attrs={'type':'text','class':'form-control','placeholder':u'Teléfono móvil del solicitante'}),
            'tlf_oficina': TextInput(attrs={'type':'text','class':'form-control','placeholder':u'Teléfono de oficina del solicitante'}),
        }

    def clean_fecha_nacimiento(self):
        '''
        Función para validar el campo de fecha de nacimiento
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_nacimiento']):
            raise forms.ValidationError(u'La fecha de nacimiento no puede ser mayor ni igual al día de hoy')
        return self.cleaned_data['fecha_nacimiento']
