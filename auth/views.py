# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.utils.decorators import method_decorator
#from axes.decorators import watch_login
from auth.forms import AuthenticationForm, CambiarClaveForm
#from django.contrib.auth.forms import PasswordChangeForm


# Create your views here.
class Auth(View):
    tipo_mensaje = ''
    mensaje = ''
    form = AuthenticationForm
    template = 'index.html'
    diccionario = {}
    
    def get(self, request, *args, **kwargs):
        self.form = self.form()
        if request.user.is_authenticated():
            if request.GET.has_key('next'):
                return HttpResponseRedirect(request.GET['next'])

        self.diccionario.update({'user':request.user})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.form})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    #@method_decorator(watch_login)
    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        self.diccionario.update({'user':request.user})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':form})
        if form.is_valid():
            usuario = request.user
            login(request, form.get_user())
            if request.GET.has_key('next'):
                return HttpResponseRedirect(request.GET['next'])
        else:
            error = ''
            error = form.errors[form.errors.keys()[0]]

            self.diccionario.update({'tipo_mensaje':'error'})
            self.diccionario.update({'error':error[0]})

            return render(request, 
                           template_name=self.template,
                           dictionary=self.diccionario,
                         )

# Create your views here.
class CambiarClave(View):
    tipo_mensaje = ''
    mensaje = ''
    #form = PasswordChangeForm
    form = CambiarClaveForm
    template = 'perfil/editar_formulario.html'
    titulo = 'cambiar contraseña'
    diccionario = {}

    diccionario.update({'titulo':titulo})
    
    def get(self, request, *args, **kwargs):
        '''
        Si el usuario está autenticado pasamos formulario CambiarClaveLoged
        '''
        import pdb
        #pdb.set_trace()
        if request.user.is_authenticated():
            self.diccionario.update({'user':request.user})
            self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
            self.diccionario.update({'mensaje':self.mensaje})
            self.diccionario.update({'formulario':self.form})
            return render(request, 
                           template_name=self.template,
                           dictionary=self.diccionario,
                         )

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        self.diccionario.update({'user':request.user})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':form})
        if form.is_valid():
            usuario = request.user
            login(request, form.get_user())
            if request.GET.has_key('next'):
                return HttpResponseRedirect(request.GET['next'])
        else:
            error = ''
            error = form.errors[form.errors.keys()[0]]

            self.diccionario.update({'tipo_mensaje':'error'})
            self.diccionario.update({'error':error[0]})

            return render(request, 
                           template_name=self.template,
                           dictionary=self.diccionario,
                         )
