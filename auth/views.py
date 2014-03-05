# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponseRedirect
from auth.forms import AuthenticacionForm

# Create your views here.
class Auth(View):
    tipo_mensaje = ''
    mensaje = ''
    form = AuthenticacionForm
    template = 'index.html'
    diccionario = {}
    
    def get(self, request, *args, **kwargs):
        self.form = self.form()
        if request.user.is_authenticated():
            if request.GET.has_key('next'):
                return HttpResponseRedirect(request.GET['next'])
            
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.form})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        self.diccionario.update({'form':self.form})
        usuario = User.objects.filter(Q(username=request.POST['username'])|Q(email=request.POST['username']))
        self.diccionario.update({'request':request})
        if usuario.exists(): 
            usuario = usuario[0]
            user = authenticate(username=usuario, password=request.POST['password'])

            if user is not None:
                login(request, usuario)
                #"User is not valid, active and authenticated"
                if not user.is_active:
                    self.mensaje = u"La contraseña es válida pero la cuenta ha sido desactivada"
                    (self.tipo_mensaje, self.expresion) = msj_expresion('error')
                    return renderizar_plantilla(request, 
                                        plantilla = self.template, 
                                        tipo_mensaje = self.tipo_mensaje, 
                                        expresion = self.expresion, 
                                        mensaje = self.mensaje, 
                                        form = form
                                    )
                else:
                    # El usuario se loggea correctamente
                    return HttpResponseRedirect('/preguntas_secretas/')
            else:
                # El usuario o contraseña eran incorrectos
                self.mensaje = u"Contraseña incorrecta. Por favor, inténtelo nuevamente"
                (self.tipo_mensaje, self.expresion) = msj_expresion('error')
                return renderizar_plantilla(request, 
                                    plantilla = self.template, 
                                    tipo_mensaje = self.tipo_mensaje, 
                                    expresion = self.expresion, 
                                    mensaje = self.mensaje, 
                                    form = form
                                )
        else:
            # El usuario no existe
            self.mensaje = u"No existe el usuario %s. Por favor, confirme sus datos" %(request.POST['username'])
            (self.tipo_mensaje, self.expresion) = msj_expresion('error')
            form = self.form(request.POST)
            return renderizar_plantilla(request, 
                                plantilla = self.template, 
                                tipo_mensaje = self.tipo_mensaje, 
                                expresion = self.expresion, 
                                mensaje = self.mensaje, 
                                form = form
                            )
