# -*- coding: UTF8 -*-
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf

from curriculum.views import lista_filtros
from auth.models import UserProfile
from lugares.models import Estado

from forms import PersonaForm, EditarPersonaForm
from models import Persona

import datetime


class EditarPersonaView(View):
    '''
    Clase para la edición de datos de información de la persona
    '''
    template='perfil/editar_formulario.html'
    persona_form = EditarPersonaForm
    titulo = 'información personal'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        try:
            request.user.get_profile()
        except:
            url = reverse('crear_persona')

        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = False

        persona = Persona.objects.get(userprofile=usuario.profile)
        self.persona_form = self.persona_form(instance=persona)
        self.diccionario.update({'persona':persona})

        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.persona_form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.persona_form = PersonaForm(request.POST)

        self.diccionario.update(csrf(request))
        self.diccionario.update({'persona_form':self.persona_form})
        persona = request.user.get_profile().persona

        estado = Estado.objects.get(id=request.POST['reside'])
        fecha_nacimiento = datetime.datetime.strptime(request.POST['fecha_nacimiento'], "%d/%m/%Y").strftime("%Y-%m-%d") 

        persona = Persona.objects.get(cedula=persona.cedula)
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

        request.user.first_name = request.POST['primer_nombre']
        request.user.last_name = request.POST['primer_apellido']
        request.user.email = persona.email
        request.user.save()

        return redirect(reverse('perfil'))


class CrearPersonaView(View):
    '''
    Clase para postulación de currículum
    '''
    template='curriculum/postulacion.html'
    persona_form = PersonaForm

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'persona_form':persona_form})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.diccionario.update({'curriculum':True})
        self.diccionario.update({'mensaje_error':''})
        self.diccionario.update({'form':self.persona_form()})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.persona_form = PersonaForm(request.POST)

        email2_error = ''
        error_general = ''
        error = False

        if not self.persona_form.is_valid():
            self.diccionario.update(csrf(request))
            self.diccionario.update({'curriculum':True})
            mensaje_error = ''
            if self.persona_form.errors.has_key('__all__'):
                mensaje_error = self.persona_form.errors['__all__'][0]
            self.diccionario.update({'mensaje_error':mensaje_error})
            self.diccionario.update({'form':self.persona_form})
            return render(request, 
                           template_name=self.template,
                           dictionary=self.diccionario,
                         )

        else:
            estado = Estado.objects.get(id=request.POST['reside'])
            fecha_nacimiento = datetime.datetime.strptime(request.POST['fecha_nacimiento'], "%d/%m/%Y").strftime("%Y-%m-%d") 
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

            usuario = request.user

            usuario.is_active = True
            usuario.first_name = request.POST['primer_nombre']
            usuario.last_name = request.POST['primer_apellido']
            usuario.save()

            usuario_perfil = UserProfile.objects.create(persona=persona, user=usuario)

        self.template = 'perfil/perfil.html'
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class PersonalesView(View):
    '''
    Clase para guardado del perfil de la persona
    '''
    template='perfil/personales.html'
    persona_form = PersonaForm() 

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'persona_form':persona_form})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.persona_form = PersonaForm(request.POST)

        email2_error = ''
        error_general = ''
        error = False

        if not request.POST.has_key('email_2'):
            email2_error = u'Este campo es obligatorio.'
            self.persona_form.errors = True
            error = True
        else:
            valor_email2 = request.POST['email_2']

        if not self.persona_form.errors:
            if not request.POST['email'] == request.POST['email_2']:
                error = True
                error_general = u'Ambas direcciones de correo electrónico deben coincidir. Por favor, revise y vuelva a intentarlo.'

        # Revisar si ya hay alguna cédula o email guardada para este usuario
        if Persona.objects.filter(cedula=request.POST['cedula']).exists():
            error = True
            error_general = u'Esta persona ya se encuentra registrada con esa cédula.'
        if Persona.objects.filter(email=request.POST['email']).exists() or User.objects.filter(email=request.POST['email']).exists():
            error = True
            error_general = u'Esta persona ya se encuentra registrada con ese email.'

        self.diccionario.update(csrf(request))
        self.diccionario.update({'persona_form':self.persona_form})
        self.diccionario.update({'valor_email2':valor_email2})
        self.diccionario.update({'email2_error':email2_error})
        self.diccionario.update({'error_general':error_general})

        # Si hay algún error, se renderiza de nuevo la plantilla con los errores encontrados
        if error:
            return render(request, 
                           template_name=self.template,
                           dictionary=self.diccionario,
                         )
        else:
            estado = Estado.objects.get(id=request.POST['reside'])
            fecha_nacimiento = datetime.datetime.strptime(request.POST['fecha_nacimiento'], "%d/%m/%Y").strftime("%Y-%m-%d") 
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
                                             email = request.POST['email'],
                                             )
            # Se crea el usuario con el correo electrónico por defecto y se crea una contraseña aleatoria para el usuario
            clave = User.objects.make_random_password()
            usuario = User.objects.create_user(username = request.POST['email'],
                                              password = clave, 
                                             )

            usuario.is_active = True
            usuario.first_name = request.POST['primer_nombre']
            usuario.last_name = request.POST['primer_apellido']
            usuario.email = request.POST['email']
            usuario.save()

            # Envío de mail
            asunto = u'%sCreación de cuenta exitosa' % (settings.EMAIL_SUBJECT_PREFIX)
            mensaje = Mensaje.objects.get(caso='Creación de usuario (email)')
            emisor = settings.EMAIL_HOST_USER
            destinatarios = (request.POST['email'],)

            # Sustitución de variables clave y usuario
            mensaje = mensaje.mensaje.replace('<clave>','%s'%(clave)).replace('<usuario>','%s'%(request.POST['email']))
            send_mail(subject=asunto, message=mensaje, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=destinatarios)

        self.template = 'curriculum/aprobados.html'
        mensaje = Mensaje.objects.get(caso='Creación de usuario (web)')
        mensaje = mensaje.mensaje
        self.diccionario.update({'mensaje':mensaje})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )
