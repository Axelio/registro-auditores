# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.utils.decorators import method_decorator
from django.contrib.auth.views import password_change, login
from django.core.urlresolvers import reverse
from auth.forms import AuthenticationForm
from django.core.context_processors import csrf
import datetime # Importar funciones para cálculo del tiempo
from auditores_suscerte import settings # Importar configuraciones del proyecto

# Create your views here.
def auth(request):
    diccionario = {}
    diccionario.update(csrf(request))
    if request.user.groups.get_query_set().filter(name__iexact='operador').exists():
        return HttpResponseRedirect(reverse('perfil'))
    diccionario.update({'user':request.user})
    diccionario.update({'auth':True})
    return login(request, authentication_form=AuthenticationForm, template_name='auth/formulario.html', extra_context=diccionario)


class AutoLogout: 
    def process_request(self, request): 
        if not request.user.is_authenticated() : 
            #No se puede desloggear un usuario no loggeado
            return 

        try: 
            # AUTO_LOGOUT_DELAY es una variable en minutos para desloguear al usuario
            # request.session['last_touch'] Es una variable tipo time que guarda el momento del último movimiento del usuario

            # Si ha pasado más tiempo inactivo que la cantitudad de tiempo especificado en el settings, entonces se desloggea al usuario
            if datetime.datetime.today() - request.session['last_touch'] > datetime.timedelta(0, settings.AUTO_LOGOUT_DELAY * 60, 0): 
                logout(request) # Se desloggea al usuario
                return 
        except KeyError: 
            pass 

        request.session['last_touch'] = datetime.datetime.today() # Si no se intenta el desloggeo, se guarda en la variable 'last_touch' con el momento actual del usuario
