from django.contrib import admin
from curriculum.models import *
from curriculum.forms import (
        CertificacionForm, ConocimientoForm,
        CompetenciaForm, Educacion, 
        ConocimientoAdminForm)

admin.site.register(Certificacion)

class ConocimientoAdmin(admin.ModelAdmin):
    form = ConocimientoAdminForm
admin.site.register(Conocimiento, ConocimientoAdmin)

class IdiomaAdmin(admin.ModelAdmin):
    search_fields = ('idioma',)
    list_display = ('persona','idioma','nivel_leido','nivel_escrito','nivel_hablado')
    list_filter = ('idioma',)
admin.site.register(Idioma, IdiomaAdmin)

class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('competencia', 'nivel')
    list_filter = ('nivel',)
admin.site.register(Competencia, CompetenciaAdmin)

class ListaCompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre','tipo',)
    list_filter = ('tipo',)
    ordering = ('tipo','id')

class CitaAdmin(admin.ModelAdmin):
    list_display = (
            'usuario',
            'primera_fecha',
            'segunda_fecha',
            'tercera_fecha',
            'cita_fijada')
admin.site.register(Cita, CitaAdmin)
admin.site.register(ListaCompetencia, ListaCompetenciaAdmin)
admin.site.register(Educacion)
admin.site.register(TipoEducacion)
admin.site.register(Laboral)
admin.site.register(ListaIdiomas)
