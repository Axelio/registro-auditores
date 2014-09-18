from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from views import (CrearPersonaView, EditarPersonaView)

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^crear/',
        login_required(CrearPersonaView.as_view()),
        name='crear_persona'),

    url(r'^editar/*$',
        login_required(EditarPersonaView.as_view()),
        name='editar_persona'),

)
