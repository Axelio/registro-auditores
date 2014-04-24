from django.conf.urls import patterns, include, url
from django.contrib import admin
from curriculum.views import *
from curriculum.forms import * 
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'auditores_suscerte.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^postulacion/$', login_required(
        staff_member_required(
            CurriculumView.as_view())), name='curriculum'),
)
