# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.utils.decorators import method_decorator
from django.contrib.auth.views import password_change, login
from django.core.urlresolvers import reverse
from axes.decorators import watch_login
from auth.forms import AuthenticationForm
from django.core.context_processors import csrf

# Create your views here.
def auth(request):
    diccionario = {}
    diccionario.update(csrf(request))
    if request.user.groups.get_query_set().filter(name__iexact='operador').exists():
        return HttpResponseRedirect(reverse('perfil'))
    diccionario.update({'user':request.user})
    diccionario.update({'auth':True})
    return login(request, authentication_form=AuthenticationForm, template_name='auth/formulario.html', extra_context=diccionario)
