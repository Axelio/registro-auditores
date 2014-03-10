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
    diccionario.update({'user':request.user})
    diccionario.update({'auth':True})
    return login(request, template_name='auth/formulario.html', extra_context=diccionario)

class Auth2(View):
    tipo_mensaje = ''
    mensaje = ''
    form = AuthenticationForm
    template = 'auth/formulario.html'
    diccionario = {}
    
    def get(self, request, *args, **kwargs):
        self.form = self.form()
        if request.user.is_authenticated():
            if request.GET.has_key('next'):
                return HttpResponseRedirect(request.GET['next'])

        self.diccionario.update({'user':request.user})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'form':self.form})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    @method_decorator(watch_login)
    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        self.diccionario.update({'user':request.user})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':form})
        if form.is_valid():
            usuario = request.user
            login(request, form.get_user())
            if request.POST['next'] == '':
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect(request.POST['next'])
        else:
            error = ''
            error = form.errors[form.errors.keys()[0]]

            self.diccionario.update({'tipo_mensaje':'error'})
            self.diccionario.update({'error':error[0]})

            return render(request, 
                           template_name=self.template,
                           dictionary=self.diccionario,
                         )

def cambiar_clave(request):
    diccionario = {}
    titulo = 'cambiar contraseña'
    diccionario.update({'titulo':titulo})
    return password_change(request, template_name='auth/formulario.html',
                #email_template_name='',
                #subject_template_name='reset_subject.txt',
                post_change_redirect=reverse('inicio'),
                extra_context = diccionario,
                )

