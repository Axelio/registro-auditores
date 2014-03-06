# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate

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
