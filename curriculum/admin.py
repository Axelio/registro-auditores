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
    list_display = ('persona', 'idioma',
            'nivel_leido', 'nivel_escrito', 'nivel_hablado')
    list_filter = ('idioma',)
admin.site.register(Idioma, IdiomaAdmin)


class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'puntaje', 'fecha')
    list_filter = ('usuario', 'tipo', 'fecha')
    ordering = ('usuario','tipo__listacompetencia__tipo', 'id')
admin.site.register(Competencia, CompetenciaAdmin)


class TipoCompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puntaje_maximo')
    ordering = ('id',)
admin.site.register(TipoCompetencia, TipoCompetenciaAdmin)


class ListaCompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'puntaje_maximo', 'tipo_puntaje')
    list_filter = ('tipo',)
    ordering = ('tipo', 'id')
admin.site.register(ListaCompetencia, ListaCompetenciaAdmin)


class CitaAdmin(admin.ModelAdmin):
    list_display = (
            'usuario',
            'primera_fecha',
            'segunda_fecha',
            'tercera_fecha',
            'cita_fijada')
admin.site.register(Cita, CitaAdmin)


class CursoAdmin(admin.ModelAdmin):
    list_display = (
            'usuario',
            'titulo',
            'estado',
            'fecha_inicio',
            'fecha_fin',
            'horas')

    list_filter = (
            'fecha_inicio',
            'fecha_fin')
admin.site.register(Curso, CursoAdmin)
class AprobacionAdmin(admin.ModelAdmin):
    list_display = (
        'instrumento', 'ambito', 'puntaje_aprobatorio',
        'puntaje_total', 'fecha'
            )

    search_fields = (
        'instrumento', 'ambito'
            )

    list_filter = (
        'ambito', 'fecha'
            )


class EvaluacionAdmin(admin.ModelAdmin):
    list_display = (
            'usuario',
            'puntaje',
            'fecha')
    list_filter = (
            'fecha',)
admin.site.register(Evaluacion, EvaluacionAdmin)
admin.site.register(Aprobacion, AprobacionAdmin)
admin.site.register(Educacion)
admin.site.register(TipoEducacion)
admin.site.register(Laboral)
admin.site.register(ListaIdiomas)
admin.site.register(Ambito)
admin.site.register(Instrumento)
admin.site.register(Estado)
