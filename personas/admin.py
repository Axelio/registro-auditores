from django.contrib import admin

# Register your models here.
from personas.models import *

class PersonaAdmin(admin.ModelAdmin):
    search_fields   = ['cedula','primer_nombre','segundo_nombre','primer_apellido','segundo_nombre','email','tlf_fijo','tlf_movil','tlf_oficina']
    list_display    = ['cedula','primer_nombre','segundo_nombre','primer_apellido','segundo_apellido','genero','email','tlf_fijo']
admin.site.register(Persona, PersonaAdmin)

