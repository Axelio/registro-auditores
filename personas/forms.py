# -*- coding: utf-8 -*-
from django import forms
from personas.models import Persona
from lib.funciones import fecha_futura
import datetime

class PersonaForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de personas
    '''
    class Meta:
        # Se determina cuál es el modelo al que va a 
        model = Persona

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
