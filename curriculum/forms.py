# -*- coding: utf-8 -*-
from django import forms
from curriculum.models import Certificacion
from lib.funciones import fecha_futura
import datetime

class CertificacionForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de personas
    '''
    class Meta:
        # Se determina cuál es el modelo al que va a 
        model = Certificacion

    def clean_fecha_inicio(self):
        '''
        Función para validar el campo de fecha inicio
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(u'La fecha de inicio no puede ser mayor ni igual al día de hoy')

    def clean_fecha_fin(self):
        '''
        Función para validar el campo de fecha fin
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_fin']):
            raise forms.ValidationError(u'La fecha final no puede ser mayor ni igual al día de hoy')
