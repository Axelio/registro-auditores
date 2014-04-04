from django.conf.urls import patterns, include, url
from django.contrib import admin
from curriculum.views import *
from curriculum.forms import * 

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'auditores_suscerte.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^postulacion/$', CurriculumView.as_view(), name='curriculum'),
)
