# -*- coding: utf-8 -*-
from django.contrib import admin
from personas.models import *
from personas.forms import *


class PersonaAdmin(admin.ModelAdmin):
    search_fields = ['cedula',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_nombre',
            'email',
            'tlf_reside',
            'tlf_movil',
            'tlf_oficina']

    list_display = ['cedula',
            'primer_nombre',
            'segundo_nombre',
            'primer_apellido',
            'segundo_apellido',
            'genero',
            'email',
            'tlf_reside']

admin.site.register(Persona, PersonaAdmin)


class AuditorAdmin(admin.ModelAdmin):
    list_display = ('persona',
            'fecha_acreditacion',
            'fecha_desacreditacion',
            'estatus')

    list_filter = ('estatus',
            'fecha_acreditacion',
            'fecha_desacreditacion')
admin.site.register(Auditor, AuditorAdmin)


class EstatusAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dependencia')
    
    ordering = ('dependencia',)
admin.site.register(Estatus, EstatusAdmin)

admin.site.register(CertificadoElectronico)
