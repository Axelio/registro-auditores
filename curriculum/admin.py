from django.contrib import admin
from curriculum.models import *
from curriculum.forms import CertificacionForm, ConocimientoForm, CompetenciaForm, Educacion

class CertificacionAdmin(admin.ModelAdmin):
    form = CertificacionForm
admin.site.register(Certificacion, CertificacionAdmin)

class CompetenciaInline(admin.TabularInline):
    model=Competencia
    form = CompetenciaForm
    extra=1

class IdiomaInline(admin.TabularInline):
    model=Idioma
    extra=1

class ConocimientoAdmin(admin.ModelAdmin):
    inlines = (CompetenciaInline, IdiomaInline, )
    form = ConocimientoForm
admin.site.register(Conocimiento, ConocimientoAdmin)

class IdiomaAdmin(admin.ModelAdmin):
    search_fields = ('idioma',)
admin.site.register(Idioma, IdiomaAdmin)

class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('competencia', 'tipo', 'puntaje')
    list_filter = ('tipo',)
    ordering = ('tipo',)
admin.site.register(Competencia, CompetenciaAdmin)
admin.site.register(ListaIdiomas)
admin.site.register(ListaCompetencia)
admin.site.register(Educacion)
admin.site.register(TipoEducacion)
admin.site.register(Laboral)
