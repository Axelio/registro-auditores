from django.contrib import admin
from curriculum.models import *
from curriculum.forms import CertificacionForm, ConocimientoForm, CompetenciaForm, Educacion, ConocimientoAdminForm

class CertificacionAdmin(admin.ModelAdmin):
    form = CertificacionForm
admin.site.register(Certificacion, CertificacionAdmin)

class CompetenciaInline(admin.TabularInline):
    model=Competencia
    form = CompetenciaForm
    extra=1

class ConocimientoAdmin(admin.ModelAdmin):
    inlines = (CompetenciaInline,)
    form = ConocimientoAdminForm
admin.site.register(Conocimiento, ConocimientoAdmin)

class IdiomaAdmin(admin.ModelAdmin):
    search_fields = ('idioma',)
admin.site.register(Idioma, IdiomaAdmin)

class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('competencia', 'puntaje')
admin.site.register(Competencia, CompetenciaAdmin)
class ListaCompetenciaAdmin(admin.ModelAdmin):
    list_display = ('nombre','tipo',)
    list_filter = ('tipo',)
    ordering = ('tipo','id')
admin.site.register(ListaCompetencia, ListaCompetenciaAdmin)
admin.site.register(Educacion)
admin.site.register(TipoEducacion)
admin.site.register(Laboral)
admin.site.register(ListaIdiomas)
