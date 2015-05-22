from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from curriculum.views import (CitasView, EducacionView, LaboralView,
    ConocimientoView, EvaluacionView, CompetenciaView, HabilidadView,
    IdiomaView, CursoView, CertificacionView)
from .views import PerfilView, CrearPerfilView, EditarPerfilView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^perfil/citas/$',
        login_required(CitasView.as_view()),
        name='citas'),

    url(r'^perfil/educacion/(?P<palabra>\w+)/(?P<educacion_id>[\d]+)*$',
        login_required(EducacionView.as_view()),
        name='educacion'),

    url(r'^perfil/laboral/(?P<palabra>\w+)/(?P<laboral_id>[\d]+)*$',
        login_required(LaboralView.as_view()),
        name='laboral'),

    url(r'^perfil/conocimiento/(?P<palabra>\w+)/(?P<conocimiento_id>[\d]+)*$',
        login_required(ConocimientoView.as_view()),
        name='conocimiento'),

    url(r'^perfil/evaluacion/(?P<evaluacion_id>[\d]+)/(?P<aspirante_id>[\d]+)/',
        login_required(EvaluacionView.as_view()),
        name='evaluacion'),

    url(r'^perfil/competencia/(?P<aspirante_id>[\d]+)/',
        login_required(CompetenciaView.as_view()),
        name='competencia'),

    url(r'^perfil/habilidad/(?P<palabra>\w+)/(?P<habilidad_id>[\d]+)*$',
        login_required(HabilidadView.as_view()),
        name='habilidad'),

    url(r'^perfil/idioma/(?P<palabra>\w+)/(?P<idioma_id>[\d]+)*$',
        login_required(IdiomaView.as_view()),
        name='idioma'),

    url(r'^perfil/curso/(?P<palabra>\w+)/(?P<curso_id>[\d]+)*$',
        login_required(CursoView.as_view()),
        name='curso'),

    url(r'^perfil/certificacion/(?P<palabra>\w+)/(?P<certificacion_id>[\d]+)*$',
        login_required(CertificacionView.as_view()),
        name='certificacion'),

    url(r'^crear/',
        login_required(CrearPerfilView.as_view()),
        name='crear_perfil'),

    url(r'^editar/*$',
        login_required(EditarPerfilView.as_view()),
        name='editar_perfil'),

    url(r'^$',
        login_required(PerfilView.as_view()),
        name='perfil'),

)
