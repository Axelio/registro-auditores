# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import render_to_response
from curriculum.models import Certificacion, Conocimiento, Competencia, ListaCompetencia, Educacion
from django.shortcuts import render_to_response
from django.contrib.formtools.wizard.views import SessionWizardView
from lib.funciones import fecha_futura
import datetime

NIVELES_COMPTETENCIA = (
        ('experto','Experto'),
        ('alto','Alto'),
        ('medio','Medio'),
        ('basico',u'Básico'),
        ('nada','Nada'),
        )

class CompetenciaForm(forms.ModelForm):
    '''
    Formulario para el ingreso de Competencias en el panel administrativo
    '''
    competencia = forms.ModelChoiceField(queryset=ListaCompetencia.objects.all(), label='competencia')
    nivel = forms.CharField(max_length=10, label='nivel')
    class Meta:
        model = Competencia
        exclude = ['puntaje', 'competencia', 'tipo']

    def __init__(self, *args, **kwargs):
        '''
        Se establece por defecto que el campo nivel vendrá cargado con la información de NIVELES_COMPTETENCI
        '''
        super(CompetenciaForm, self).__init__(*args, **kwargs)
        self.fields["nivel"] = forms.ChoiceField(choices=NIVELES_COMPTETENCIA)

class ConocimientoForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de Conocimientos
    '''
    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario 
        model = Conocimiento

class CertificacionForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de personas
    '''
    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario 
        model = Certificacion
    def clean(self):
        '''
        Función para validaciones generales del modelo Curriculum
        '''
        fecha_inicio = self.data['fecha_inicio'] 
        fecha_fin = self.data['fecha_fin'] 
        # La fecha viene dada en string, por lo tanto se transforma a tipo fecha
        fecha_inicio = datetime.datetime.strptime(fecha_inicio, '%d/%m/%Y')
        fecha_fin = datetime.datetime.strptime(fecha_fin, '%d/%m/%Y')
        # La fecha inicial no puede ser mayor a la final:
        if fecha_inicio > fecha_fin:
            raise forms.ValidationError(u'La fecha final no puede ser mayor ni igual al día de hoy')
        return self.cleaned_data

    def clean_fecha_inicio(self):
        '''
        Función para validar el campo de fecha inicio
        '''
        # Fecha actual
        fecha_actual = datetime.date.today()
        # Si fecha_actual es futura (función en lib/funciones.py)
        if fecha_futura(self.cleaned_data['fecha_inicio']):
            raise forms.ValidationError(u'La fecha de inicio no puede ser mayor ni igual al día de hoy')
        return self.cleaned_data['fecha_inicio']

class EducacionForm(forms.ModelForm):
    '''
    Formulario general para el ingreso de Conocimientos
    '''
    class Meta:
        # Se determina cuál es el modelo al que va a referirse el formulario 
        model = Educacion

class CurriculumWizard(SessionWizardView):
    def get_template_names(self):
        '''
        Definiendo cuál va a ser el formulario que se utilizará
        '''
        return 'curriculum/postulacion.html'

    def done(self, form_list, **kwargs):
        return render_to_response('done.html', {
                'form': [form.cleaned_data for form in form_list],
            })
