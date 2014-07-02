from django.conf.urls import patterns, include, url
from django.contrib import admin
from curriculum.views import *
from curriculum.forms import * 
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^nuevo_aspirante/$', login_required(
            CrearAspirante.as_view()), name='nuevo_aspirante'),
)
