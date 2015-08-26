# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect

from .forms import EditarPerfilForm
from authentication.models import UserProfile
from lugares.models import Estado
from personas.forms import PersonaForm
from personas.models import Persona
from curriculum.views import lista_filtros, aptitudes, revisar_requisitos
from curriculum.models import Cita

import datetime


class PerfilView(View):
    '''
    Clase para la renderización del Perfil
    '''
    template = 'perfil.html'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        if request.user.profile.persona == None:
            return HttpResponseRedirect(reverse('detalles_perfil'))
        '''
        if not request.session.get('ultima_sesion', False):
            persistente = True
            mensaje = 'Recuerde cambiar su contraseña por seguridad...'
            tipo_mensaje = 'warning'
            self.diccionario.update({'tipo_mensaje':tipo_mensaje})
            self.diccionario.update({'mensaje':mensaje})
            request.session['ultima_sesion'] = datetime.datetime.today()

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            return HttpResponseRedirect(reverse('crear_perfil'))
        '''

        # Revisamos si el usuario pertenece al grupo Operador
        # Y si pertenece, le cambiamos la plantilla y los filtros
        if usuario.groups.filter(name__iexact='operador').exists():
            aspirantes = listaAspirantes()
            auditores = Auditor.objects.filter(Q(estatus__nombre='Renovado')|Q(estatus__nombre='Inscrito'))
            self.template = 'perfil/perfil_operador.html'

            self.diccionario.update({'aspirantes': aspirantes})
            self.diccionario.update({'auditores': auditores})

        fijar_cita = False
        if revisar_requisitos(aptitudes(request.user)) == True:
            fijar_cita = True

        if fijar_cita:
            cita = Cita.objects.filter(usuario=request.user.profile, dia__gte=datetime.datetime.today().date())
            if cita.exists():
                self.diccionario.update({'citas': cita})
            if cita.filter(cita_fijada=True).exists():
                cita_fijada = cita.get(cita_fijada=True)
                self.diccionario.update({'cita_fijada': cita_fijada})

        self.diccionario.update({'fijar_cita': fijar_cita})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class DetallesPerfilView(View):
    '''
    Clase para la edición de datos de información de la persona
    '''
    template='formulario.html'
    titulo = 'información personal'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''
    form = PersonaForm

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)

        if not request.user.profile.persona == None:
            # Si hay un perfil creado, se instancia el objeto para su edición
            self.form = self.form(instance=request.user.profile.persona)

        else:
            self.diccionario.update({'form': self.form()})

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


    def post(self, request, *args, **kwargs):
        self.form = self.form(request.POST)

        self.diccionario.update(csrf(request))
        self.diccionario.update({'form': self.form})

        estado = Estado.objects.get(id=request.POST['reside'])
        fecha_nacimiento = datetime.datetime.strptime(request.POST['fecha_nacimiento'], "%d/%m/%Y").strftime("%Y-%m-%d") 

        if request.user.profile.persona == None:
            persona = Persona.objects.create(cedula=request.POST['cedula'],
                                             primer_nombre = request.POST['primer_nombre'],
                                             segundo_nombre = request.POST['segundo_nombre'],
                                             primer_apellido = request.POST['primer_apellido'],
                                             segundo_apellido = request.POST['segundo_apellido'],
                                             genero = request.POST['genero'],
                                             reside = estado,
                                             direccion = request.POST['direccion'],
                                             fecha_nacimiento = fecha_nacimiento,
                                             tlf_reside = request.POST['tlf_reside'],
                                             tlf_movil = request.POST['tlf_movil'],
                                             tlf_oficina = request.POST['tlf_oficina'],
                                             tlf_contacto = request.POST['tlf_contacto'],
                                             estado_civil = request.POST['estado_civil'],
                                             email = request.user.email,
                                             )

        else:
            persona = Persona.objects.get(cedula=request.user.profile.persona.cedula)
            persona.cedula = request.POST['cedula']
            persona.primer_nombre = request.POST['primer_nombre']
            persona.segundo_nombre = request.POST['segundo_nombre']
            persona.primer_apellido = request.POST['primer_apellido']
            persona.segundo_apellido = request.POST['segundo_apellido']
            persona.genero = request.POST['genero']
            persona.reside = estado
            persona.direccion = request.POST['direccion']
            persona.fecha_nacimiento = fecha_nacimiento
            persona.tlf_reside = request.POST['tlf_reside']
            persona.tlf_movil = request.POST['tlf_movil']
            persona.tlf_oficina = request.POST['tlf_oficina']
            persona.tlf_contacto = request.POST['tlf_contacto']
            persona.estado_civil = request.POST['estado_civil']

        request.user.is_active = True
        request.user.first_name = request.POST['primer_nombre']
        request.user.last_name = request.POST['primer_apellido']
        request.user.email = persona.email
        request.user.save()

        perfil = UserProfile.objects.get(user=request.user)
        perfil.persona = persona
        perfil.save()

        messages.add_message(request, messages.SUCCESS,
             'Los datos de su perfil se han guardado exitosamente')


        return redirect(reverse('perfil'))
