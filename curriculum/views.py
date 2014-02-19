# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied

from curriculum.models import *
from curriculum.forms import *
from personas.models import *
from personas.forms import *
from auth.models import *
import datetime

class EducacionView(View):
    '''
    Clase para la renderización de los datos educativos
    '''
    template='perfil/editar_educacion.html'
    educacion_form = EducacionForm
    educaciones = ''
    mensaje = ''
    tipo_mensaje = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(userprofile=request.user.userprofile_set.get_query_set()[0].persona)
        except:
            raise Http404

        self.diccionario.update({'educacion_form':self.educacion_form()})
        if kwargs.has_key('educacion_id') and not kwargs['educacion_id'] == None:
            nueva = False
            try:
                educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
            except:
                raise Http404

            if educacion.persona == usuario.userprofile_set.get_query_set()[0].persona:
                self.educacion_form = self.educacion_form(instance=educacion)
            else:
                raise PermissionDenied
        else:
            self.educaciones = Educacion.objects.filter(persona=persona)

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'educaciones':self.educaciones})
        self.diccionario.update({'educacion_form':self.educacion_form})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        guardado = False

        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            # Si se edita una Educación
            if kwargs['palabra'] == 'editar':
                # Búsqueda de variables con los IDs enviados por POST
                institucion = Institucion.objects.get(id=request.POST['institucion'])
                tipo = TipoEducacion.objects.get(id=request.POST['tipo'])
                fecha_inicio = datetime.datetime.strptime(request.POST['fecha_inicio'], "%d/%m/%Y").strftime("%Y-%m-%d") 
                fecha_fin = datetime.datetime.strptime(request.POST['fecha_fin'], "%d/%m/%Y").strftime("%Y-%m-%d") 

                educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
                educacion.institucion = institucion
                educacion.carrera = request.POST['carrera']
                educacion.tipo = tipo
                educacion.fecha_inicio = fecha_inicio
                educacion.fecha_fin = fecha_fin

                educacion.save()

                self.mensaje = u'Información educacional ha sido guardado exitosamente'
                self.tipo_mensaje = u'success'

            # Si se elimina una Educación
            if kwargs['palabra'] == 'eliminar':
                educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
                educacion.delete()

                self.mensaje = u'Información educacional ha sido eliminada exitosamente'
                self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        persona = request.user.userprofile_set.get_query_set()[0].persona
        self.educaciones = Educacion.objects.filter(persona=persona)

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'educaciones':self.educaciones})
        self.diccionario.update({'educacion_form':self.educacion_form})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class CurriculumView(View):
    '''
    Clase para postulación de currículum
    '''
    template='curriculum/postulacion.html'
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
                                              email = request.POST['email'], 
                                              first_name = request.POST['primer_nombre'],
                                              last_name = request.POST['segundo_nombre'],
                                              password = clave, 
                                             )

            usuario.is_active = True
            usuario.first_name = request.POST['primer_nombre']
            usuario.last_name = request.POST['primer_apellido']
            usuario.save()

            # Se asocia la persona con el usuario
            if not UserProfile.objects.filter(user=usuario, persona=persona).exists():
               usuario_perfil = UserProfile.objects.create(user=usuario, persona=persona)

            # Envío de mail
            asunto = u'[SUSCERTE] Creación de cuenta exitosa'
            mensaje = Mensaje.objects.get(caso='Creación de usuario (email)')
            emisor = settings.EMAIL_HOST_USER
            destinatarios = (request.POST['email'],)

            # Sustitución de variables clave y usuario
            mensaje = mensaje.mensaje.replace('<clave>','%s'%(clave)).replace('<usuario>','%s'%(request.POST['email']))
            send_mail(subject=asunto, message=mensaje, from_email=emisor, recipient_list=destinatarios)

        self.template = 'curriculum/aprobados.html'
        mensaje = Mensaje.objects.get(caso='Creación de usuario (web)')
        mensaje = mensaje.mensaje
        self.diccionario.update({'mensaje':mensaje})
        return HttpResponseRedirect('preguntas_secretas/')
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class PerfilView(View):
    '''
    Clase para la renderización del Perfil
    '''
    template='perfil/perfil.html'

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}

    def get(self, request, *args, **kwargs):
        mensaje = ''
        tipo = ''
        self.diccionario.update(csrf(request))
        usuario = request.user
        try:
            persona = Persona.objects.get(userprofile=request.user.userprofile_set.get_query_set)
        except:
            raise Http404
        else:
            persona = Persona.objects.get(userprofile=request.user.userprofile_set.get_query_set)

        educaciones = Educacion.objects.filter(persona=persona)
        laborales = Laboral.objects.filter(usuario=request.user.userprofile_set.get_query_set)

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'educaciones':educaciones})
        self.diccionario.update({'laborales':laborales})
        self.diccionario.update({'mensaje':mensaje})
        self.diccionario.update({'tipo':tipo})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )
