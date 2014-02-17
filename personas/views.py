# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.core.context_processors import csrf
from personas.forms import PersonaForm

# Create your views here.
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
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )
