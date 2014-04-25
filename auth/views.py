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

# Create your views here.
def auth(request):
    diccionario = {}
    if request.user.groups.get_query_set().filter(name__iexact='operador').exists():
        return HttpResponseRedirect(reverse('perfil'))
    diccionario.update({'user':request.user})
    diccionario.update({'auth':True})
    return login(request, template_name='auth/formulario.html', extra_context=diccionario)


def cambiar_clave(request):
    diccionario = {}
    titulo = 'cambiar contraseña'
    diccionario.update({'titulo':titulo})
    diccionario.update({'palabra_clave':'cambiar'})
    diccionario.update({'cambiar_clave':True})
    diccionario.update({'formulario':True})
    return password_change(request, template_name='auth/password_reset_form.html',
                post_change_redirect=reverse('inicio'),
                extra_context = diccionario,
                )
