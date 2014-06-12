# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.context_processors import csrf
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.db.models import Q
from django.core.paginator import (Paginator, EmptyPage,
        PageNotAnInteger)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils import formats

from curriculum.models import *
from curriculum.forms import *
from personas.models import *
from personas.forms import *
from auth.models import *

import datetime

def notificar_entrevista_evaluacion(usuario):
    evaluacion = Evaluacion.objects.filter(usuario=usuario)
    competencias = Competencia.objects.filter(usuario=usuario)

    if evaluacion.exists() and competencias.exists():
        # Se llama una función de revisión de aprobación tanto de evaluación
        # como de entrevista por separado (mejor manejo a nivel general e
        # independiente y se llama una función de notificación según los puntajes
        evaluacion = evaluacion.latest('fecha')
        asunto = u'%sNotificación de inscripción' % (settings.EMAIL_SUBJECT_PREFIX)
        destinatarios = (usuario.persona.email,)
        emisor = settings.EMAIL_HOST_USER
        if revisar_entrevista(usuario) and revisar_evaluacion(usuario):
            mensaje = Mensaje.objects.get(caso=u'Aprobación como auditor')
        else:
            mensaje = Mensaje.objects.get(caso=u'No aprobación como auditor')

        # Sustitución de variables clave y usuario
        mensaje = mensaje.mensaje.replace('<PRIMER_NOMBRE>','%s' % (usuario.persona.primer_nombre))
        mensaje = mensaje.replace('<PRIMER_APELLIDO>','%s' % (usuario.persona.primer_apellido))
        mensaje = mensaje.replace('<CEDULA>','%s' % (intcomma(usuario.persona.cedula)))
        mensaje = mensaje.replace('<FECHA>','%s' % (formats.date_format(evaluacion.fecha, "DATE_FORMAT")))

        send_mail(subject=asunto, message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=destinatarios)


def get_operadores():
    '''
    Función diseñara para retornar el listado de operadores
    '''
    return User.objects.filter(groups__name__iexact='operador')


def revisar_acreditaciones(request):
    '''
    Se revisa si hay alguna acreditación
    pronta a vencer dado a PERIODO_REV_ACREDITACION
    especificada eni el settings. Si hay alguna por
    vencerse, retorna True
    '''
    fecha_actual = datetime.date.today()
    fecha_limite = datetime.datetime(
            fecha_actual.year,
            fecha_actual.month + settings.PERIODO_REV_ACREDITACION,
            fecha_actual.day)

    lista_auditores = Auditor.objects.filter(fecha_desacreditacion__lte=fecha_limite)
    auditores = ''
    for auditor in lista_auditores:
        auditores +=  u'%s (%s) se vence el: %s \n' % (auditor.persona, auditor.persona.email, formats.date_format(auditor.fecha_desacreditacion, "DATE_FORMAT"))

    destinatarios = []

    for operador in get_operadores():
        destinatarios.append(operador.profile.persona.email)

    if lista_auditores.exists():
        asunto = u'%sEstado de auditores' % (settings.EMAIL_SUBJECT_PREFIX)
        mensaje = u'A continuación, el listado de los auditores prontos a vencer su acreditación:\n \n %s' % (auditores)
        emisor = settings.EMAIL_HOST_USER

        send_mail(subject=asunto, message=mensaje, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=destinatarios)
    url = reverse('inicio')
    return HttpResponseRedirect(url)


def listaAspirantes():
    # En teoría, todos los usuarios que no esten en grupo operadores
    # son aspirantes, así que filtramos a los usuarios
    # que no esten en el grupo Operadores
    personas = Persona.objects.filter()
    auditores = Auditor.objects.filter(acreditado=True)
    citas = Cita.objects.all()
    citados = []

    for cita in citas:
        citados.append(cita.usuario)

    aspirantes = User.objects.filter(is_active=True, userprofile__in=citados)
    aspirantes = aspirantes.exclude(Q(userprofile__persona__auditor__in=auditores)|Q(groups__name__iexact='operador'))
    return aspirantes


def aptitudes(request):
    '''
    Revisión de cada una de las aptitudes de la persona
    '''
    listado = []

    laborales = Laboral.objects.filter(
            usuario=request.user.profile).order_by('-fecha_fin')
    educaciones = Educacion.objects.filter(
            persona=request.user.profile.persona).order_by('-fecha_fin')
    conocimientos = Conocimiento.objects.filter(
            usuario=request.user.profile)
    habilidades = Habilidad.objects.filter(
            usuario=request.user.profile)
    idiomas = Idioma.objects.filter(
            persona=request.user.profile.persona)
    certifcaciones = Certificacion.objects.filter(
            persona=request.user.profile.persona).order_by('-fecha_fin')
    cursos = Curso.objects.filter(
            usuario=request.user.profile).order_by('-fecha_fin')

    listado.append(laborales)
    listado.append(educaciones)
    listado.append(conocimientos)
    listado.append(habilidades)
    listado.append(idiomas)
    listado.append(certifcaciones)
    listado.append(cursos)

    return listado


def lista_filtros(request):
    '''
    Envío de variables con las aptitudes ya filtradas
    '''
    listado = aptitudes(request)
    requisitos = revisar_requisitos(listado)
    cita = Cita.objects.filter(usuario=request.user.profile)

    listado = {'laborales': listado[0],
                'educaciones': listado[1],
                'conocimientos': listado[2],
                'habilidades': listado[3],
                'idiomas': listado[4],
                'certificaciones': listado[5],
                'cursos': listado[6],
                'requisitos': requisitos,
                }

    if cita.exists():
        listado.update({'cita': cita[0]})

    return listado


def revisar_entrevista(usuario):
    '''
    Validar según los puntajes de aprobación
    de las entrevistas, que el usuario haya aprobado
    '''
    competencias = Competencia.objects.filter(
            usuario=usuario)
    puntajes = 0.0

    aprobaciones = Aprobacion.objects.last()

    for competencia in competencias:
        puntajes += float(competencia.puntaje)

    if puntajes >= float(aprobaciones.entrevista_aprobatoria):
        return True
    else:
        return False


def revisar_evaluacion(usuario):
    '''
    Validar según los puntajes de aprobación
    de las entrevistas, que el usuario haya aprobado
    '''
    evaluacion = Evaluacion.objects.filter(
            usuario=usuario).latest('fecha')

    aprobaciones = Aprobacion.objects.last()

    if evaluacion.puntaje >= float(aprobaciones.evaluacion_aprobatoria):
        return True
    else:
        return False


def revisar_requisitos(listado):
    '''
    Validar si todos los requisitos se satisfacen
    para proceder a la fijación de fecha para la cita.
    Retorna True si la información es suficiente.
    Retorna False si falta información.
    '''
    for lista in listado:
        if not lista.exists():
            return False
    return True


class CitasView(View):
    '''
    Clase para la renderización de las citas
    '''
    template = 'perfil/editar_formulario.html'
    citas_form = CitasForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = 'citas'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        listado = aptitudes(request)
        requisitos = revisar_requisitos(listado)
        usuario = request.user
        self.diccionario.update(csrf(request))
        nueva = True
        if requisitos:
            self.tipo_mensaje = 'info'
            self.mensaje = 'Debe seleccionar tres fechas tentativas en las '
            self.mensaje += 'que desearía tener una cita con nosotros.'
            cita = Cita.objects.filter(usuario=usuario.profile)
            if cita.exists():
                if cita[0].cita_fijada == '':
                    # Si la fecha fijada está en blanco (no ha sido fijada)
                    # Se le permite al usuario la edición de la misma
                    self.citas_form = self.citas_form(instance=cita[0])
                else:
                    # Sino, debe redireccionarle al perfil de nuevo
                    return redirect('perfil')
        else:
            self.template = 'perfil/perfil.html'
            self.tipo_mensaje = 'warning'
            self.mensaje = u'Debe tener toda la información '
            self.mensaje += u'curricular completa. Por favor, revísela.'
        self.diccionario.update({'persona': usuario.profile.persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'formulario': self.citas_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        listado = aptitudes(request)
        requisitos = revisar_requisitos(listado)
        usuario = request.user
        self.diccionario.update(csrf(request))
        nueva = True
        if not requisitos:
            self.template = 'perfil/perfil.html'
            self.tipo_mensaje = 'warning'
            self.mensaje = u'Debe tener toda la información '
            self.mensaje += u'curricular completa. Por favor, revísela.'
        else:
            self.diccionario.update(csrf(request))
            self.citas_form = self.citas_form(request.POST)
            usuario = request.user
            nueva = True
            fecha_1 = datetime.datetime.strptime(
                    request.POST['primera_fecha'],
                    "%d/%m/%Y").strftime("%Y-%m-%d")
            fecha_2 = datetime.datetime.strptime(
                    request.POST['segunda_fecha'],
                    "%d/%m/%Y").strftime("%Y-%m-%d")
            fecha_3 = datetime.datetime.strptime(
                    request.POST['tercera_fecha'],
                    "%d/%m/%Y").strftime("%Y-%m-%d")

            if self.citas_form.is_valid():
                if nueva:
                    cita = Cita.objects.filter(usuario=usuario.profile)
                    if cita.exists():
                        cita = cita[0]
                        cita.primera_fecha = primera_fecha = fecha_1
                        cita.segunda_fecha = segunda_fecha = fecha_2
                        cita.tercera_fecha = tercera_fecha = fecha_3
                        cita.save()
                    else:
                        cita = Cita.objects.create(usuario=usuario.profile,
                                primera_fecha=fecha_1,
                                segunda_fecha=fecha_2,
                                tercera_fecha=fecha_3)

                    self.mensaje = "Las fechas para cita ha sido cargada con "
                    self.mensaje += "éxito. Se ha enviado su información a "
                    self.mensaje += "los administradores"
                    self.tipo_mensaje = 'success'
                    self.template = 'perfil/perfil.html'
            else:
                if self.citas_form.errors:
                    self.mensaje = self.citas_form.errors['__all__'][0]
                    self.tipo_mensaje = 'error'

        self.diccionario.update({'persona': usuario.profile.persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'formulario': self.citas_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)

        return render(request,
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class EducacionView(View):
    '''
    Clase para la renderización de los datos educativos
    '''

    template = 'perfil/editar_formulario.html'
    educacion_form = EducacionForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = u'educación'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'formulario': self.educacion_form()})
        if kwargs.has_key('educacion_id') and kwargs['educacion_id'] != None:
            nueva = False
            try:
                educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
            except:
                raise Http404

            if educacion.persona == usuario.userprofile_set.get_query_set()[0].persona:
                self.educacion_form = self.educacion_form(instance=educacion)
            else:
                raise PermissionDenied

        # Si se elimina una Educación
        if kwargs['palabra'] == 'eliminar':
            educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
            educacion.delete()

            self.mensaje = u'Información educacional ha sido eliminada exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.educacion_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        guardado = False
        nueva = True

        persona = request.user.userprofile_set.get_query_set()[0].persona
        self.educacion_form = self.educacion_form(request.POST)
        if self.educacion_form.is_valid():
            if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
                institucion = Institucion.objects.get(id=request.POST['institucion'])
                tipo = TipoEducacion.objects.get(id=request.POST['tipo'])
                fecha_inicio = datetime.datetime.strptime(request.POST['fecha_inicio'], "%d/%m/%Y").strftime("%Y-%m-%d") 
                fecha_fin = datetime.datetime.strptime(request.POST['fecha_fin'], "%d/%m/%Y").strftime("%Y-%m-%d") 
                titulo = request.POST['titulo']

                if kwargs['palabra'] == 'editar':
                    # Si se edita una Educación
                    # Búsqueda de variables con los IDs enviados por POST
                    educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
                    educacion.institucion = institucion
                    educacion.tipo = tipo
                    educacion.fecha_inicio = fecha_inicio
                    educacion.fecha_fin = fecha_fin
                    educacion.titulo = titulo

                    educacion.save()

                    self.mensaje = u'Información educacional ha sido editada exitosamente'
                    self.tipo_mensaje = u'success'
                else:
                    # Si se crea una Educación
                    educacion = Educacion.objects.create(persona=persona, institucion=institucion, tipo=tipo, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, titulo=titulo)
                    self.mensaje = u'Información educacional ha sido creada exitosamente'
                    self.tipo_mensaje = u'success'

                self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.educacion_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class CurriculumView(View):
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
        if not request.user.groups.filter(name__iexact='operador').exists():
            raise PermissionDenied
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

            usuario_perfil = UserProfile.objects.create(persona=persona, user=usuario)

            # Envío de mail
            asunto = u'%sCreación de cuenta exitosa' % (settings.EMAIL_SUBJECT_PREFIX)
            mensaje = Mensaje.objects.get(caso='Creación de usuario (email)')
            emisor = settings.EMAIL_HOST_USER
            destinatarios = (request.POST['email'],)

            # Sustitución de variables clave y usuario
            mensaje = mensaje.mensaje.replace('<clave>','%s'%(clave)).replace('<cuenta>','%s'%(request.POST['email']))
            send_mail(subject=asunto, message=mensaje, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=destinatarios)

        self.template = 'curriculum/aprobados.html'
        mensaje = Mensaje.objects.get(caso='Creación de usuario (web)')
        mensaje = mensaje.mensaje
        self.diccionario.update({'mensaje':mensaje})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class PerfilView(View):
    '''
    Clase para la renderización del Perfil
    '''
    template = 'perfil/perfil.html'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PerfilView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        mensaje = ''
        tipo = ''
        self.diccionario.update(csrf(request))
        usuario = request.user
        if usuario.last_login == usuario.date_joined:
            mensaje = 'Recuerde cambiar su contraseña por seguridad...'
            tipo_mensaje = 'warning'
            self.diccionario.update({'tipo_mensaje':tipo_mensaje})
            self.diccionario.update({'mensaje':mensaje})

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'mensaje':mensaje})
        self.diccionario.update({'tipo':tipo})

        # Revisamos si el usuario pertenece al grupo Operador
        # Y si pertenece, le cambiamos la plantilla y los filtros
        if usuario.groups.filter(name__iexact='operador').exists():
            aspirantes = listaAspirantes()
            auditores = Auditor.objects.filter(acreditado=True)
            self.template = 'perfil/perfil_operador.html'

            paginator = Paginator(auditores, settings.LIST_PER_PAGE)
            page = request.GET.get('page')
            try:
                auditores = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                auditores = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                auditores = paginator.page(paginator.num_pages)

            paginator = Paginator(aspirantes, settings.LIST_PER_PAGE)
            page = request.GET.get('page')
            try:
                aspirantes = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                aspirantes = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                aspirantes = paginator.page(paginator.num_pages)

            self.diccionario.update({'aspirantes':aspirantes})
            self.diccionario.update({'auditores':auditores})

        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

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
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = False

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.persona_form = self.persona_form(instance=persona)

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.persona_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        self.persona_form = self.persona_form(request.POST)

        persona = Persona.objects.get(id=usuario.profile.persona.id)
        if self.persona_form.is_valid():
            estado = Estado.objects.get(id=request.POST['reside'])
            fecha_nacimiento = datetime.datetime.strptime(request.POST['fecha_nacimiento'], "%d/%m/%Y").strftime("%Y-%m-%d") 

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
            persona.save()

            usuario.first_name = persona.primer_nombre
            usuario.last_name = persona.primer_apellido
            usuario.email = persona.email
            usuario.save()

            self.mensaje = u'Información personal editada exitosamente'
            self.tipo_mensaje = u'success'

            if usuario.groups.filter(name__iexact='operador').exists():
                aspirantes = listaAspirantes()
                auditores = Auditor.objects.filter(acreditado=True)
                self.template = 'perfil/perfil_operador.html'

                paginator = Paginator(auditores, settings.LIST_PER_PAGE)
                page = request.GET.get('page')
                try:
                    auditores = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    auditores = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    auditores = paginator.page(paginator.num_pages)

                paginator = Paginator(aspirantes, settings.LIST_PER_PAGE)
                page = request.GET.get('page')
                try:
                    aspirantes = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    aspirantes = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    aspirantes = paginator.page(paginator.num_pages)

                self.diccionario.update({'aspirantes':aspirantes})
                self.diccionario.update({'auditores':auditores})

            else:

                self.template = 'perfil/perfil.html'

                self.lista_filtros = lista_filtros(request)
                self.diccionario.update(self.lista_filtros)

        else:
            if self.persona_form.errors.has_key('__all__'):
                self.tipo_mensaje = 'error'
                self.mensaje = self.persona_form.errors['__all__'][0]

        persona = Persona.objects.get(id=usuario.profile.persona.id)
        self.diccionario.update({'formulario':self.persona_form})
        self.diccionario.update({'persona':persona})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class LaboralView(View):
    '''
    Clase para la renderización de los datos laborales
    '''
    template='perfil/editar_formulario.html'
    laboral_form = LaboralForm 
    titulo = 'laboral'
    mensaje = ''
    tipo_mensaje = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})
    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.laboral_form()})

        # Si se elimina una Educación
        if kwargs.has_key('laboral_id') and not kwargs['laboral_id'] == None:
            nueva = False
            try:
                laboral = Laboral.objects.get(id=int(kwargs['laboral_id']))
            except:
                raise Http404

            # Si el usuario de laboral no es el mismo al loggeado, retornar permisos denegados
            if laboral.usuario == usuario.profile:
                self.laboral_form = self.laboral_form(instance=laboral)
            else:
                raise PermissionDenied
        else:
            self.laborales = Laboral.objects.filter(usuario=request.user.profile)

        if kwargs['palabra'] == 'eliminar':
            educacion = Laboral.objects.get(id=int(kwargs['laboral_id']))
            educacion.delete()

            self.mensaje = u'Información laboral ha sido eliminada exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'formulario':self.laboral_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.laboral_form = self.laboral_form(request.POST)
        usuario = request.user
        guardado = False

        if self.laboral_form.is_valid():

            usuario = usuario.profile
            empresa = request.POST['empresa']
            sector = request.POST['sector']
            estado = Estado.objects.get(id=request.POST['estado'])
            telefono = request.POST['telefono']
            cargo = request.POST['cargo']
            funcion = request.POST['funcion']
            fecha_inicio = datetime.datetime.strptime(request.POST['fecha_inicio'], "%d/%m/%Y").strftime("%Y-%m-%d") 
            fecha_fin = datetime.datetime.strptime(request.POST['fecha_fin'], "%d/%m/%Y").strftime("%Y-%m-%d") 
            retiro = request.POST['retiro']
            direccion_empresa = request.POST['direccion_empresa']
            trabajo_actual = False
            if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
                if kwargs['palabra'] == 'editar':
                    # Si se edita información laboral 
                    # Búsqueda de variables con los IDs enviados por POST
                    
                    laboral = Laboral.objects.get(id=kwargs['laboral_id'])
                    laboral.empresa = empresa
                    laboral.sector = sector
                    laboral.estado = estado
                    laboral.telefono = telefono
                    laboral.cargo = cargo
                    laboral.funcion = funcion
                    laboral.fecha_inicio = fecha_inicio
                    laboral.fecha_fin = fecha_fin
                    laboral.retiro = retiro
                    laboral.direccion_empresa = direccion_empresa
                    laboral.trabajo_actual = trabajo_actual

                    laboral.save()

                    self.mensaje = u'Información laboral ha sido editada exitosamente'
                    self.tipo_mensaje = u'success'

                else:
                    # Si se crea información laboral 
                    laboral = Laboral.objects.create(usuario = usuario, empresa=empresa, sector=sector, estado=estado, telefono=telefono, cargo=cargo, funcion=funcion, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, retiro=retiro, direccion_empresa=direccion_empresa, trabajo_actual=trabajo_actual)
                    self.mensaje = u'Información laboral ha sido creada exitosamente'
                    self.tipo_mensaje = u'success'



            self.template = 'perfil/perfil.html'

        else:
            if self.laboral_form.errors.has_key('__all__'):
                self.tipo_mensaje = 'error'
                self.mensaje = self.laboral_form.errors['__all__'][0]
                laboral = laboral.objects.get(id=kwargs['laboral_id'])
                laboral.empresa = empresa
                laboral.sector = sector
                laboral.estado = estado
                laboral.telefono = telefono
                laboral.cargo = cargo
                laboral.funcion = funcion
                laboral.fecha_inicio = fecha_inicio
                laboral.fecha_fin = fecha_fin
                laboral.retiro = retiro
                laboral.direccion_empresa = direccion_empresa
                laboral.trabajo_actual = trabajo_actual

                laboral.save(commit=False)
                self.laboral_form(instance=laboral)

        persona = request.user.profile.persona
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'persona':persona})
        self.diccionario.update({'formulario':self.laboral_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class CompetenciaView(View):
    '''
    Clase para la renderización de los datos de conocimientos generales
    '''
    template='carga_evaluacion.html' # Plantilla que utilizará por defecto para renderizar
    mensaje = '' # Mensaje que se le mostrará al usuario
    tipo_mensaje = '' # Si el mensaje es de éxito o de error
    titulo = u'cargando evaluación' # Título a ser renderizado en la plantilla
    lista_filtros = '' # Listado filtrado de objetos que llegarán a la plantilla
    competencia_form = CompetenciaPruebaForm

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})
    competencias = ListaCompetencia.objects.all().order_by('tipo')

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True
        error = False 

        # Obtener la persona para renderizarla en la plantilla
        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        aspirante = User.objects.get(id=kwargs['aspirante_id'])

        self.diccionario.update({'competencias': self.competencias})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'persona': persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'error': error})
        self.diccionario.update({'formulario':self.competencia_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))

        persona = request.user.profile.persona

        listado_tipo_competencia = []

        for valor in request.POST.items():
            if not valor[0].__contains__('csrf'):
                puntuacion = float(valor[1].replace(',','.'))

                lista_competencia = valor[0]
                lista_competencia = lista_competencia.split('_')[1]
                lista_competencia = ListaCompetencia.objects.get(id=lista_competencia)

                usuario = request.path_info.split('/')[3]
                usuario = UserProfile.objects.get(user__id=usuario)
                
                competencia = Competencia.objects.filter(usuario=usuario, tipo=lista_competencia.tipo)
                if competencia.exists():
                    competencia = competencia[0]
                    competencia.puntaje = competencia.puntaje + puntuacion
                    competencia.save()
                else:
                    competencia = Competencia.objects.create(
                            tipo=lista_competencia.tipo,
                            usuario=usuario,
                            puntaje=puntuacion)

                if lista_competencia.tipo_puntaje == 'int':
                    puntuacion = float(puntuacion * int(lista_competencia.puntaje_maximo))

        # Revisión de puntuación máxima
        competencia = Competencia.objects.all()
        for comp in competencia:
            if comp.puntaje > comp.tipo.puntaje_maximo:
                comp.puntaje = comp.tipo.puntaje_maximo
                comp.save()


        self.template = 'curriculum/aprobados.html'
        self.tipo_mensaje = 'success'
        self.mensaje = u'Entrevista cargada exitosamente.'

        notificar_entrevista_evaluacion(usuario)

        self.diccionario.update({'competencias': self.competencias})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'persona':persona})
        self.diccionario.update({'titulo':self.titulo})

        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class HabilidadView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template='perfil/editar_formulario.html'
    habilidad_form = HabilidadForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = 'habilidad'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(id=usuario.profile.persona.id)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.habilidad_form()})
        if kwargs.has_key('habilidad_id') and not kwargs['habilidad_id'] == None:
            nueva = False
            try:
                habilidad = Habilidad.objects.get(id=int(kwargs['habilidad_id']))
            except:
                raise Http404

            if habilidad.usuario == persona.userprofile:
                self.habilidad_form = self.habilidad_form(instance=habilidad)
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            habilidad = Habilidad.objects.get(id=int(kwargs['habilidad_id']))
            habilidad.delete()

            self.mensaje = u'Habilidad eliminada exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.habilidad_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.profile.persona
        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            habilidad = request.POST['habilidad']

            if kwargs['palabra'] == 'editar':
                # Si se edita una Educación
                # Búsqueda de variables con los IDs enviados por POST
                habilidad_obj = Habilidad.objects.get(id=int(kwargs['habilidad_id']))
                habilidad_obj.habilidad = campo_habilidad

                habilidad_obj.save()

                self.mensaje = u'Habilidad editada exitosamente'
                self.tipo_mensaje = u'success'
            else:
                # Si se crea una Educación
                habilidad_obj = Habilidad.objects.create(usuario=persona.userprofile, habilidad=habilidad)
                self.mensaje = u'Habilidad creada exitosamente'
                self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.habilidad_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class ConocimientoView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template='perfil/editar_formulario.html'
    conocimiento_form = ConocimientoForm 
    titulo = 'conocimiento'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = False

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.conocimiento_form()})
        if kwargs.has_key('conocimiento_id') and not kwargs['conocimiento_id'] == None:
            try:
                conocimiento = Conocimiento.objects.get(id=int(kwargs['conocimiento_id']))
            except:
                raise Http404

            if conocimiento.usuario == persona.userprofile:
                self.conocimiento_form = self.conocimiento_form(instance=conocimiento)
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'nueva':
            nueva = True
            if Conocimiento.objects.filter(usuario=persona.userprofile).exists():
                self.mensaje = u'Usted ya tiene conocimiento en base de datos, por favor edítela si es necesario'
                self.tipo_mensaje = u'error'
                self.template = 'perfil/perfil.html'

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            conocimiento = Conocimiento.objects.get(id=int(kwargs['conocimiento_id']))
            conocimiento.delete()

            self.mensaje = u'Conocimiento eliminado exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.conocimiento_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.profile.persona
        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            conocimiento = request.POST['otros_conocimientos']

            if kwargs['palabra'] == 'editar':
                conocimiento = Conocimiento.objects.get(id=kwargs['conocimiento_id'])
                conocimiento.otros_conocimientos = request.POST['otros_conocimientos']
                conocimiento.save()

                self.mensaje = u'Conocimientos editados exitosamente'
                self.tipo_mensaje = u'success'
            else:
                if Conocimiento.objects.filter(usuario=persona.userprofile).exists():
                    self.mensaje = u'Usted ya tiene conocimientos guardados, por favor edítela si es necesario'
                    self.tipo_mensaje = u'error'
                else:
                    conocimiento = Conocimiento.objects.create(usuario=persona.userprofile, otros_conocimientos=conocimiento)
                    self.mensaje = u'Otros conocimientos creados exitosamente'
                    self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.conocimiento_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class IdiomaView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template='perfil/editar_formulario.html'
    idioma_form = IdiomaForm 
    titulo = 'idioma'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(userprofile=usuario.profile)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.idioma_form()})
        if kwargs.has_key('idioma_id') and not kwargs['idioma_id'] == None:
            try:
                idioma = Idioma.objects.get(id=int(kwargs['idioma_id']))
            except:
                raise Http404

            if idioma.persona == persona:
                self.idioma_form = self.idioma_form(instance=idioma)
            else:
                raise PermissionDenied

        if kwargs['palabra'] == 'nueva':
            nueva = True
        else:
            idioma = Idioma.objects.get(id=int(kwargs['idioma_id']))

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            idioma.delete()

            self.mensaje = u'Idioma eliminado exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona':persona})
        self.diccionario.update({'nueva':nueva})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'formulario':self.idioma_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.userprofile_set.get_query_set()[0].persona
        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:
            l_idioma = ListaIdiomas.objects.get(id=request.POST['idioma'])
            nivel_escrito = request.POST['nivel_escrito']
            nivel_leido = request.POST['nivel_leido']
            nivel_hablado = request.POST['nivel_hablado']

            # Buscamos que no se dupliquen idiomas
            idioma = Idioma.objects.filter(persona=persona, idioma=request.POST['idioma'])
            if idioma.exists() and idioma.count() > 1:
                self.mensaje = u'Usted ya tiene %s cargado en base de datos, por favor edítela si es necesario' %(request.POST['idioma'])
                self.tipo_mensaje = u'error'
                self.template = 'perfil/editar_formulario.html'
                self.idioma_form=idioma_form(request)
            else:
                if kwargs['palabra'] == 'editar':
                    idioma = Idioma.objects.get(id=kwargs['idioma_id'])
                    idioma.idioma = l_idioma
                    idioma.nivel_escrito = nivel_escrito
                    idioma.nivel_leido = nivel_leido
                    idioma.nivel_hablado = nivel_hablado
                    idioma.save()

                    self.mensaje = u'Idioma editado exitosamente'
                    self.tipo_mensaje = u'success'
                else:
                    idioma = Idioma.objects.create(persona=persona, idioma=l_idioma, nivel_escrito=nivel_escrito, nivel_leido=nivel_leido, nivel_hablado=nivel_hablado)
                    self.mensaje = u'Idioma creado exitosamente'
                    self.tipo_mensaje = u'success'

                self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje':self.tipo_mensaje})
        self.diccionario.update({'mensaje':self.mensaje})
        self.diccionario.update({'formulario':self.idioma_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class CertificacionView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template='perfil/editar_formulario.html'
    certificacion_form = CertificacionForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = u'certificación'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(id=usuario.profile.persona.id)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.certificacion_form()})
        if kwargs.has_key('certificacion_id') and not kwargs['certificacion_id'] == None:
            nueva = False
            try:
                certificacion = Certificacion.objects.get(id=int(kwargs['certificacion_id']))
            except:
                raise Http404

            if certificacion.persona == persona:
                self.certificacion_form = self.certificacion_form(instance=certificacion)
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            certificacion = Certificacion.objects.get(id=int(kwargs['certificacion_id']))
            certificacion.delete()

            self.mensaje = u'Certificación eliminada exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona': persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje':self. mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'formulario': self.certificacion_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.profile.persona
        if kwargs.has_key('palabra') and not kwargs['palabra'] == None:

            pais = Pais.objects.get(id=request.POST['pais'])
            institucion = Institucion.objects.get(id=request.POST['institucion'])
            fecha_inicio = datetime.datetime.strptime(request.POST['fecha_inicio'], "%d/%m/%Y").strftime("%Y-%m-%d") 
            fecha_fin = datetime.datetime.strptime(request.POST['fecha_fin'], "%d/%m/%Y").strftime("%Y-%m-%d") 

            if kwargs['palabra'] == 'editar':
                # Si se edita una Certificación
                # Búsqueda de variables con los IDs enviados por POST
                certificacion = Certificacion.objects.get(id=int(kwargs['certificacion_id']))
                certificacion.titulo = request.POST['titulo']
                certificacion.codigo_certificacion = request.POST['codigo_certificacion']
                certificacion.institucion = institucion
                certificacion.fecha_inicio = fecha_inicio
                certificacion.fecha_fin = fecha_fin
                certificacion.lugar = pais 

                certificacion.save()

                self.mensaje = u'Habilidad editada exitosamente'
                self.tipo_mensaje = u'success'
            else:
                # Si se crea una Certificacion
                certificacion = Certificacion.objects.create(persona = persona,
                        institucion = institucion,
                        pais = pais,
                        codigo_certificacion = request.POST['codigo_certificacion'],
                        titulo = request.POST['titulo'],
                        fecha_inicio = fecha_inicio,
                        fecha_fin = fecha_fin)
                self.mensaje = u'Certificación creada exitosamente'
                self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'formulario': self.certificacion_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )



class CursoView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template='perfil/editar_formulario.html'
    curso_form = CursoForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = u'curso'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(id=usuario.profile.persona.id)
        except:
            raise Http404

        self.diccionario.update({'formulario':self.curso_form()})
        if kwargs.has_key('curso_id') and not kwargs['curso_id'] == None:
            nueva = False
            try:
                curso = Curso.objects.get(id=int(kwargs['curso_id']))
            except:
                raise Http404

            if curso.usuario == usuario.profile:
                self.curso_form = self.curso_form(instance=curso)
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            certificacion = Curso.objects.get(id=int(kwargs['curso_id']))
            certificacion.delete()

            self.mensaje = u'Curso eliminado exitosamente'
            self.tipo_mensaje = u'success'

            self.template = 'perfil/perfil.html'

        self.diccionario.update({'persona': persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje':self. mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'formulario': self.curso_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        self.curso_form = self.curso_form(request.POST)

        persona = request.user.profile.persona
        if self.curso_form.is_valid():
            if kwargs.has_key('palabra') and not kwargs['palabra'] == None:

                estado = Estado.objects.get(id=request.POST['estado'])
                institucion = Institucion.objects.get(id=request.POST['institucion'])
                fecha_inicio = datetime.datetime.strptime(request.POST['fecha_inicio'], "%d/%m/%Y").strftime("%Y-%m-%d") 
                fecha_fin = datetime.datetime.strptime(request.POST['fecha_fin'], "%d/%m/%Y").strftime("%Y-%m-%d") 

                if kwargs['palabra'] == 'editar':
                    # Si se edita un Curso
                    # Búsqueda de variables con los IDs enviados por POST
                    curso = Curso.objects.get(id=int(kwargs['curso_id']))
                    curso.titulo = request.POST['titulo']
                    curso.institucion = institucion
                    curso.fecha_inicio = fecha_inicio
                    curso.fecha_fin = fecha_fin
                    curso.horas = request.POST['horas']
                    curso.estado = estado

                    curso.save()

                    self.mensaje = u'Curso editado exitosamente'
                    self.tipo_mensaje = u'success'
                else:
                    # Si se crea un Curso
                    curso = Curso.objects.create(usuario = usuario.profile,
                            institucion = institucion,
                            estado = estado,
                            titulo = request.POST['titulo'],
                            fecha_inicio = fecha_inicio,
                            fecha_fin = fecha_fin,
                            horas = request.POST['horas'])
                    self.mensaje = u'Curso cargado exitosamente'
                    self.tipo_mensaje = u'success'

                self.template = 'perfil/perfil.html'
        else:
            if self.curso_form.errors.has_key('__all__'):
                self.mensaje = self.evaluacion_form.errors['__all__'][0]
                self.tipo_mensaje = 'error'

        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'formulario': self.curso_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class VerAuditores(View):
    '''
    Clase para las consultas de los auditores
    '''
    template = 'auditores/auditores.html'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}

    def get(self, request, *args, **kwargs):
        fecha_actual = datetime.date.today()
        auditores = Auditor.objects.filter(
                fecha_desacreditacion__gte=fecha_actual,
                acreditado = True)

        paginator = Paginator(auditores,  settings.LIST_PER_PAGE) # Show 25 contacts per page

        page = request.GET.get('page')
        try:
            auditores = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            auditores = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            auditores = paginator.page(paginator.num_pages)

        self.diccionario.update({'auditores':auditores})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )
        

class CargaEvaluacion(View):
    '''
    Clase para las consultas de los auditores
    '''
    template = 'auditores.html'
    lista_filtros = ''
    formulario = EvaluacionForm

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}

    def get(self, request, *args, **kwargs):

        diccionario.update()
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )
class EvaluacionView(View):
    '''
    Clase para la renderización de la evaluación
    '''
    template='perfil/editar_formulario.html'
    evaluacion_form = EvaluacionForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = u'evaluación'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(id=usuario.profile.persona.id)
        except:
            raise Http404


        self.diccionario.update({'persona': persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje':self. mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'formulario': self.evaluacion_form})
        self.lista_filtros = lista_filtros(request)
        self.diccionario.update(self.lista_filtros)
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.evaluacion_form = self.evaluacion_form(request.POST)
        request.POST
        usuario = request.user
        persona = request.user.profile.persona

        if self.evaluacion_form.is_valid():
            usuario = request.path_info.split('/')[3]
            usuario = UserProfile.objects.get(user__id=usuario)
            evaluacion = Evaluacion.objects.filter(usuario=usuario)
            if evaluacion.exists():
                evaluacion = evaluacion[0]
                evaluacion.puntaje = request.POST['puntaje']
                evaluacion.save()
            else:
                evaluacion = Evaluacion.objects.create(
                        usuario=usuario,
                        puntaje = request.POST['puntaje'])

            self.template = 'curriculum/aprobados.html'
            self.tipo_mensaje = 'success'
            self.mensaje = u'Evaluación cargada exitosamente.'

            notificar_entrevista_evaluacion(usuario)

        else:
            if self.evaluacion_form.errors:
                if self.evaluacion_form.errors.has_key('__all__'):
                    self.mensaje = self.evaluacion_form.errors['__all__'][0]
                    self.tipo_mensaje = 'error'

        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'formulario': self.evaluacion_form})

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class AcreditarView(View):
    '''
    Clase para la edición de datos de información de la persona
    '''
    template='auditores/formulario.html'
    acreditacion_form = AcreditacionForm
    titulo = 'acreditar'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        nueva = False

        if not request.user.groups.filter(name__iexact='operador').exists():
            raise PermissionDenied

        try:
            persona = Persona.objects.get(userprofile=request.user.profile)
        except:
            raise Http404

        usuario = User.objects.get(id=kwargs['usuario_id'])

        self.diccionario.update({'usuario': usuario})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'form': self.acreditacion_form})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        self.acreditacion_form = self.acreditacion_form(request.POST)

        if self.acreditacion_form.is_valid():
            fecha_actual = datetime.date.today()
            fecha_limite = datetime.datetime(
                    fecha_actual.year + settings.PERIODO_VENC_ACREDITACION,
                    fecha_actual.month,
                    fecha_actual.day)
            
            persona = Persona.objects.get(userprofile__user__id=kwargs['usuario_id'])
            auditor = Auditor.objects.create(persona=persona,
                    acreditado=True,
                    fecha_acreditacion=fecha_actual,
                    fecha_desacreditacion=fecha_limite,
                    observacion=request.POST['observacion'])
            return HttpResponseRedirect(reverse('inicio'))
        else:
            self.diccionario.update({'usuario': usuario})
            self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
            self.diccionario.update({'mensaje': self.mensaje})
            self.diccionario.update({'form': self.acreditacion_form})

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )


class FijarCitaView(View):
    '''
    Clase para la edición de datos de información de la persona
    '''
    template='auditores/fijar_cita.html'
    cita_form = FijarCitaForm
    titulo = 'fijar cita'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo':titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        nueva = False

        if not request.user.groups.filter(name__iexact='operador').exists():
            raise PermissionDenied

        try:
            persona = Persona.objects.get(userprofile=request.user.profile)
        except:
            raise Http404

        usuario = User.objects.get(id=kwargs['usuario_id'])
        cita = Cita.objects.get(usuario__user=usuario)

        self.diccionario.update({'usuario': usuario})
        self.diccionario.update({'cita': cita})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'form': self.cita_form })
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        self.cita_form = self.cita_form(request.POST)

        if self.cita_form.is_valid():
            cita = Cita.objects.get(usuario__user__id=kwargs['usuario_id'])
            cita.cita_fijada = request.POST['cita_fijada']
            cita.save()
            
            return HttpResponseRedirect(reverse('inicio'))
        else:
            self.diccionario.update({'usuario': usuario})
            self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
            self.diccionario.update({'mensaje': self.mensaje})
            self.diccionario.update({'form': self.cita_form})

        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )

class RequisitosView(View):
    '''
    Función para determinar cuáles son los requisitos
    faltantes por la persona segun su ámbito
    '''
    template = 'perfil/evaluar_requisitos.html'
    diccionario = {}
    mensaje = ''
    tipo_mensaje = ''

    def get(self, request, *args, **kwargs):
        usuario = User.objects.get(id=kwargs['usuario_id'])

        # Revisar si la persona ya es auditor (acreditado o no)
        if not usuario.get_profile().persona.auditor_set.get_query_set().exists():
            # Si no tiene ninguna, es un aspirante a auditor, no renovación

            # Se filtran los requisitos por ámbito...
            pass


        self.diccionario.update({'usuario': usuario})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        return render(request, 
                       template_name=self.template,
                       dictionary=self.diccionario,
                     )
