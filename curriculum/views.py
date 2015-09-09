# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.views.generic.base import View
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.context_processors import csrf
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.db.models import Q
from django.core.paginator import (
        Paginator, EmptyPage, PageNotAnInteger)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.humanize.templatetags.humanize import intcomma
from django.forms.models import modelformset_factory
from django.utils import formats

from curriculum.models import *
from curriculum.forms import *
from personas.models import *
from personas.forms import *
from authentication.models import *
from perfil.forms import AcreditacionForm

import datetime
import time


def notificar_entrevista_evaluacion(usuario):
    evaluacion = Evaluacion.objects.filter(usuario=usuario)
    competencias = Competencia.objects.filter(usuario=usuario)

    if evaluacion.exists() and competencias.exists():
        # Se llama una función de revisión de aprobación tanto de evaluación
        # como de entrevista por separado (mejor manejo a nivel general e
        # independiente y se llama una función de notificación
        # según los puntajes
        evaluacion = evaluacion.latest('fecha')
        asunto = u'%sNotificación de inscripción' % (
               settings.EMAIL_SUBJECT_PREFIX)
        destinatarios = (usuario.profile.persona.email,)
        emisor = settings.EMAIL_HOST_USER
        if revisar_entrevista(usuario) and revisar_evaluacion(usuario):
            mensaje = Mensaje.objects.get(caso=u'Aprobación como auditor')
        else:
            mensaje = Mensaje.objects.get(caso=u'No aprobación como auditor')

        # Sustitución de variables clave y usuario
        mensaje = mensaje.mensaje.replace(
                '<PRIMER_NOMBRE>', '%s' % (usuario.persona.primer_nombre))
        mensaje = mensaje.replace(
                '<PRIMER_APELLIDO>', '%s' % (usuario.persona.primer_apellido))
        mensaje = mensaje.replace(
                '<CEDULA>', '%s' % (intcomma(usuario.persona.cedula)))
        mensaje = mensaje.replace(
                '<FECHA>', '%s' % (formats.date_format(evaluacion.fecha,
                                   "DATE_FORMAT")))

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

    lista_auditores = Auditor.objects.filter(
            fecha_desacreditacion__lte=fecha_limite)
    auditores = ''
    for auditor in lista_auditores:
        auditores += u'%s (%s) se vence el: %s\n' % (
                auditor.persona, auditor.persona.email,
                formats.date_format(auditor.fecha_desacreditacion,
                                    "DATE_FORMAT"))

    destinatarios = []

    for operador in get_operadores():
        destinatarios.append(operador.profile.persona.email)

    if lista_auditores.exists():
        asunto = u'%sEstado de auditores' % (settings.EMAIL_SUBJECT_PREFIX)
        mensaje = u'A continuación, el listado de \
                  los auditores prontos a vencer su \
                  acreditación:\n \n %s' % (auditores)
        emisor = settings.EMAIL_HOST_USER

        send_mail(subject=asunto,
                  message=mensaje,
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=destinatarios)

    url = reverse('inicio')
    return HttpResponseRedirect(url)


def listaAspirantes():
    # En teoría, todos los usuarios que no esten en modelo Auditor
    # son aspirantes, así que filtramos a los usuarios
    # que no esten en el modelo Auditor
    aspirantes = User.objects.filter(userprofile__persona__auditor=None)
    aspirantes = aspirantes.exclude(groups__name__iexact='operador')
    lista_aspirantes = []

    for aspirante in aspirantes:
        if revisar_requisitos(aptitudes(aspirante)):
            lista_aspirantes.append(aspirante)
    return lista_aspirantes


def aptitudes(usuario):
    '''
    Revisión de cada una de las aptitudes de la persona
    '''
    listado = []

    laborales = Laboral.objects.filter(
            usuario=usuario.profile).order_by('-fecha_fin')
    educaciones = Educacion.objects.filter(
            persona=usuario.profile.persona).order_by('-fecha_fin')
    conocimientos = Conocimiento.objects.filter(
            usuario=usuario.profile)
    habilidades = Habilidad.objects.filter(
            usuario=usuario.profile)
    idiomas = Idioma.objects.filter(
            persona=usuario.profile.persona)
    certificaciones = Certificacion.objects.filter(
            persona=usuario.profile.persona).order_by('-fecha_fin')
    cursos = Curso.objects.filter(
            usuario=usuario.profile).order_by('-fecha_fin')

    listado.append(laborales)
    listado.append(educaciones)
    listado.append(conocimientos)
    listado.append(habilidades)
    listado.append(idiomas)
    listado.append(certificaciones)
    listado.append(cursos)

    return listado


def lista_filtros(usuario):
    '''
    Envío de variables con las aptitudes ya filtradas
    '''
    listado = aptitudes(usuario)
    requisitos = revisar_requisitos(listado)
    cita = Cita.objects.filter(
            usuario=usuario.profile, dia__gte=datetime.datetime.today())

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
        fijada = cita.filter(cita_fijada=True)
        if fijada.exists():
            listado.update({'cita': fijada[0]})
        else:
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

    if puntajes >= float(aprobaciones.puntaje_aprobatorio):
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
    Clase para la renderizacion de las citas
    '''
    template = 'formulario.html'
    form = modelformset_factory(Cita,
                                extra=3,
                                fields=('dia', 'hora'),
                                form=CitasForm)
    titulo = 'citas'

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        listado = aptitudes(request.user)
        requisitos = revisar_requisitos(listado)
        self.diccionario.update(csrf(request))
        if requisitos:
            if Cita.objects.filter(usuario=request.user.profile).exists():
                return redirect('perfil')
            else:
                self.tipo_mensaje = 'info'
                self.mensaje = 'Debe seleccionar tres fechas/horas tentativas en las \
                                que desearía tener una cita con nosotros.'

        else:
            messages.add_message(request, messages.WARNING, u'Debe tener\
                    toda la información curricular completa.')

            return HttpResponseRedirect(reverse('perfil'))
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        listado = aptitudes(request.user)
        requisitos = revisar_requisitos(listado)
        usuario = request.user
        self.diccionario.update(csrf(request))
        nueva = True
        if not requisitos:
            self.template = 'perfil.html'
            self.tipo_mensaje = 'warning'
            self.mensaje = u'Debe tener toda la información \
                            curricular completa. Por favor, revísela.'
        else:
            self.diccionario.update(csrf(request))
            self.citas_form = self.citas_form(request.POST)

            if self.citas_form.is_valid():
                cita = Cita.objects.filter(usuario=request.user.profile)
                if cita.exists():
                    for i in range(0, self.citas_form.extra):
                        tiempo = request.POST['form-%d-hora' % (i)]
                        fecha = request.POST['form-%d-fecha' % (i)]
                        tiempo_fecha = "%s %s" % (fecha, tiempo)
                        tiempo_fecha = datetime.datetime.strptime(
                                tiempo_fecha, "%d/%m/%Y %H:%M").strftime(
                                        "%Y-%m-%d %H:%M")
                        cita[i].fecha = tiempo_fecha
                        cita[i].save()
                else:
                    hora = ''
                    fecha = ''
                    for i in range(0, self.citas_form.extra):
                        tiempo = request.POST['form-%d-hora' % (i)]
                        fecha = request.POST['form-%d-fecha' % (i)]
                        tiempo_fecha = "%s %s" % (fecha, tiempo)
                        tiempo_fecha = datetime.datetime.strptime(
                                tiempo_fecha, "%d/%m/%Y %H:%M").strftime(
                                        "%Y-%m-%d %H:%M")
                        cita = Cita.objects.create(
                            usuario=request.user.profile,
                            fecha=tiempo_fecha)

                    # Si no hay una fecha fijada aún,
                    # se envía un mail a los admin
                    asunto = u'Nueva propuesta de cita de %s' % (cita.usuario)

                    destinatarios = []

                    for operador in get_operadores():
                        destinatarios.append(
                                operador.get_profile().persona.email)

                    if settings.NOTIFY:
                        emisor = settings.EMAIL_HOST_USER
                        mensaje = Mensaje.objects.get(caso='Propuesta de cita')
                        mensaje = mensaje.mensaje.replace(
                                '<LINK>', '%s/fijar_cita/%s/.' % (
                                    settings.HOST, cita.usuario.id))

                        send_mail(subject=asunto,
                                  message=mensaje,
                                  from_email=settings.DEFAULT_FROM_EMAIL,
                                  recipient_list=destinatarios)

                messages.add_message(
                        request, messages.SUCCESS, 'Las fechas para cita ha \
                                sido cargada con éxito. Se ha enviado su \
                                información a los operadores')

                return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'formulario': self.citas_form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)

        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class EducacionView(View):
    '''
    Clase para la renderización de los datos educativos
    '''

    template = 'formulario.html'
    form = EducacionForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = u'educación'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        nueva = True

        try:
            persona = Persona.objects.get(userprofile=request.user.profile)
        except:
            raise Http404

        self.diccionario.update({'form': self.form()})
        if 'educacion_id' in kwargs and kwargs['educacion_id'] != None:
            nueva = False
            try:
                educacion = Educacion.objects.get(
                        id=int(kwargs['educacion_id']))
            except:
                raise Http404

            if educacion.persona == request.user.profile.persona:
                self.form = self.form(instance=educacion)
            else:
                raise PermissionDenied

        # Si se elimina una Educación
        if kwargs['palabra'] == 'eliminar':
            educacion = Educacion.objects.get(id=int(kwargs['educacion_id']))
            educacion.delete()

            messages.add_message(request, messages.SUCCESS,
                                 u'La información educacional ha sido \
                                 eliminada exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        guardado = False
        nueva = True

        persona = request.user.userprofile.persona
        self.form = self.form(request.POST)

        if self.form.is_valid():
            if 'palabra' in kwargs and not kwargs['palabra'] == None:
                institucion = Institucion.objects.get(
                        id=request.POST['institucion'])
                tipo = TipoEducacion.objects.get(id=request.POST['tipo'])
                fecha_inicio = datetime.datetime.strptime(
                        request.POST['fecha_inicio'], "%d/%m/%Y").strftime(
                                "%Y-%m-%d")
                fecha_fin = datetime.datetime.strptime(
                        request.POST['fecha_fin'], "%d/%m/%Y").strftime(
                                "%Y-%m-%d")
                titulo = request.POST['titulo']

                if kwargs['palabra'] == 'editar':
                    # Si se edita una Educación
                    # Búsqueda de variables con los IDs enviados por POST
                    educacion = Educacion.objects.get(
                            id=int(kwargs['educacion_id']))
                    educacion.institucion = institucion
                    educacion.tipo = tipo
                    educacion.fecha_inicio = fecha_inicio
                    educacion.fecha_fin = fecha_fin
                    educacion.titulo = titulo

                    educacion.save()

                    messages.add_message(request, messages.SUCCESS,
                                         u'Información educacional \
                                                 ha sido editada exitosamente')

                else:
                    # Si se crea una Educación
                    educacion = Educacion.objects.create(
                            persona=persona, institucion=institucion,
                            tipo=tipo, fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin, titulo=titulo)

                    messages.add_message(request, messages.SUCCESS,
                                         u'Información educacional \
                                                 ha sido creada exitosamente')

                return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'persona': persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class CrearAspirante(View):
    '''
    Clase para la creación de un nuevo aspirante
    '''
    template = 'formulario.html'
    form = EmailForm
    titulo = 'nuevo aspirante'

    diccionario = {}
    diccionario.update({'form': form})
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        if not request.user.groups.filter(name__iexact='operador').exists():
            raise PermissionDenied
        self.diccionario.update({'form': self.form()})
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.form = EmailForm(request.POST)

        if self.form.is_valid():
            # Se crea el usuario con el correo electrónico por defecto
            # y se crea una contraseña aleatoria para el usuario
            clave = User.objects.make_random_password()
            usuario = User.objects.create_user(username=request.POST['email'],
                                               email=request.POST['email'],
                                               password=clave,
                                               )

            usuario.is_active = True
            usuario.save()

            # Envío de mail
            asunto = u'{0}Creación de cuenta exitosa'.format(
                    settings.EMAIL_SUBJECT_PREFIX)
            mensaje = Mensaje.objects.get(
                    caso='Creación de usuario (email)')
            emisor = settings.EMAIL_HOST_USER
            destinatarios = [request.POST['email']]

            # Sustitución de variables clave y usuario
            mensaje = mensaje.mensaje.replace(
                    '<clave>', '%s' % (clave)).replace(
                            '<cuenta>', '%s' % (request.POST['email']))

            send_mail(subject=asunto,
                      message=mensaje,
                      from_email=settings.DEFAULT_FROM_EMAIL,
                      recipient_list=destinatarios)

            mensaje = Mensaje.objects.get(caso='Creación de usuario (web)')
            self.mensaje = mensaje.mensaje

            messages.add_message(request, messages.SUCCESS, self.mensaje)

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})

        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class LaboralView(View):
    '''
    Clase para la renderización de los datos laborales
    '''
    template = 'formulario.html'
    form = LaboralForm
    titulo = 'Información laboral'
    mensaje = ''
    tipo_mensaje = ''

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

        self.diccionario.update({'formulario': self.form()})

        # Si se elimina una Educación
        if 'laboral_id' in kwargs and not kwargs['laboral_id'] == None:
            nueva = False
            try:
                laboral = Laboral.objects.get(id=int(kwargs['laboral_id']))
            except:
                raise Http404

            # Si el usuario de laboral no es el mismo al
            # loggeado, retornar permisos denegados
            if laboral.usuario == usuario.profile:
                self.form = self.form(instance=laboral)
            else:
                raise PermissionDenied
        else:
            self.laborales = Laboral.objects.filter(
                    usuario=request.user.profile)

        if kwargs['palabra'] == 'eliminar':
            educacion = Laboral.objects.get(id=int(kwargs['laboral_id']))
            educacion.delete()

            messages.add_message(request, messages.SUCCESS,
                                 u'Información laboral ha \
                                 sido eliminada exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'persona': persona})
        self.diccionario.update({'nueva': nueva})
        self.diccionario.update({'form': self.form})

        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)

        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.form = self.form(request.POST)
        usuario = request.user
        guardado = False

        if self.form.is_valid():

            usuario = usuario.profile
            empresa = request.POST['empresa']
            sector = request.POST['sector']
            estado = Estado.objects.get(id=request.POST['estado'])
            telefono = request.POST['telefono']
            cargo = request.POST['cargo']
            funcion = request.POST['funcion']
            fecha_inicio = datetime.datetime.strptime(
                    request.POST['fecha_inicio'], "%d/%m/%Y").strftime(
                            "%Y-%m-%d")
            fecha_fin = datetime.datetime.strptime(
                    request.POST['fecha_fin'], "%d/%m/%Y").strftime(
                            "%Y-%m-%d")
            retiro = request.POST['retiro']
            direccion_empresa = request.POST['direccion_empresa']
            trabajo_actual = False
            if 'palabra' in kwargs and not kwargs['palabra'] == None:
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

                    self.mensaje = u'Información laboral ha \
                            sido editada exitosamente'

                else:
                    # Si se crea información laboral
                    laboral = Laboral.objects.create(
                            usuario=usuario, empresa=empresa, sector=sector,
                            estado=estado, telefono=telefono, cargo=cargo,
                            funcion=funcion, fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin, retiro=retiro,
                            direccion_empresa=direccion_empresa,
                            trabajo_actual=trabajo_actual)
                    self.mensaje = u'Información laboral ha \
                            sido creada exitosamente'

                messages.add_message(request, messages.SUCCESS, self.mensaje)

            return HttpResponseRedirect(reverse('perfil'))

        else:
            if '__all__' in self.form.errors:
                self.tipo_mensaje = 'error'
                self.mensaje = self.form.errors['__all__'][0]
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
                self.form(instance=laboral)

        persona = request.user.profile.persona
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'persona': persona})
        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)

        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class CompetenciaView(View):
    '''
    Clase para la renderización de los datos de conocimientos generales
    '''
    template = 'carga_evaluacion.html'
    mensaje = ''
    tipo_mensaje = ''
    titulo = u'cargando evaluación'
    lista_filtros = ''
    competencia_form = CompetenciaPruebaForm

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})
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
        self.diccionario.update({'formulario': self.competencia_form})
        self.lista_filtros = lista_filtros(request.user)
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
                puntuacion = float(valor[1].replace(',', '.'))

                lista_competencia = valor[0]
                lista_competencia = lista_competencia.split('_')[1]
                lista_competencia = ListaCompetencia.objects.get(
                        id=lista_competencia)

                usuario = request.path_info.split('/')[3]
                usuario = UserProfile.objects.get(user__id=usuario)

                competencia = Competencia.objects.filter(
                        usuario=usuario, tipo=lista_competencia.tipo)
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
                    puntuacion = float(
                            puntuacion * int(lista_competencia.puntaje_maximo))

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
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'persona': persona})
        self.diccionario.update({'titulo': self.titulo})

        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)

        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class HabilidadView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template = 'formulario.html'
    form = HabilidadForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = 'habilidad'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(id=usuario.profile.persona.id)
        except:
            raise Http404

        self.diccionario.update({'form': self.form()})
        if 'habilidad_id' in kwargs and not kwargs['habilidad_id'] == None:
            nueva = False
            try:
                habilidad = Habilidad.objects.get(
                        id=int(kwargs['habilidad_id']))
            except:
                raise Http404

            if habilidad.usuario == persona.userprofile:
                self.form = self.form(instance=habilidad)
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            habilidad = Habilidad.objects.get(id=int(kwargs['habilidad_id']))
            habilidad.delete()

            messages.add_message(request, messages.SUCCESS,
                                 u'La habilidad ha sido \
                                         eliminada exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.profile.persona
        if 'palabra' in kwargs and not kwargs['palabra'] == None:
            habilidad = request.POST['habilidad']

            if kwargs['palabra'] == 'editar':
                # Si se edita una Habilidad
                # Búsqueda de variables con los IDs enviados por POST
                habilidad_obj = Habilidad.objects.get(
                        id=int(kwargs['habilidad_id']))
                habilidad_obj.habilidad = campo_habilidad

                habilidad_obj.save()

                messages.add_message(request, messages.SUCCESS,
                                     u'La habilidad ha \
                                             sido editada exitosamente')
            else:
                # Si se crea una Habilidad
                habilidad_obj = Habilidad.objects.create(
                    usuario=persona.userprofile, habilidad=habilidad)

                messages.add_message(request, messages.SUCCESS,
                                     u'La habilidad ha \
                                             sido creada exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class ConocimientoView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template = 'formulario.html'
    form = ConocimientoForm
    titulo = 'conocimiento'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        nueva = False

        try:
            persona = Persona.objects.get(userprofile=request.user.profile)
        except:
            raise Http404

        self.diccionario.update({'form': self.form()})

        conocimiento = Conocimiento.objects.filter(
                usuario=request.user.profile)

        if conocimiento.exists():
            if conocimiento[0].usuario == request.user.profile:
                self.form = self.form(instance=conocimiento[0])
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'nueva':
            nueva = True
            if Conocimiento.objects.filter(
                    usuario=request.user.profile).exists():
                messages.add_message(request, messages.ERROR,
                                     u'Usted ya tiene conocimiento \
                                     en base de datos, por \
                                     favor edítela si es necesario')

                return HttpResponseRedirect(reverse('perfil'))

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            conocimiento = Conocimiento.objects.get(
                    id=int(kwargs['conocimiento_id']))
            conocimiento.delete()

            messages.add_message(request, messages.SUCCESS,
                                 u'Conocimiento eliminado exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))

        if 'palabra' in kwargs and not kwargs['palabra'] == None:
            conocimiento = request.POST['otros_conocimientos']

            if kwargs['palabra'] == 'editar':
                conocimiento = Conocimiento.objects.get(
                        usuario=request.user.profile)
                conocimiento.otros_conocimientos = request.POST[
                        'otros_conocimientos']
                conocimiento.save()

                messages.add_message(request, messages.SUCCESS,
                                     u'Conocimiento editado exitosamente')

            else:
                if Conocimiento.objects.filter(
                        usuario=request.user.profile).exists():
                    messages.add_message(request, messages.error,
                                         u'Usted ya tiene conocimientos \
                                         guardados, por favor edítela \
                                         si es necesario')
                else:
                    conocimiento = Conocimiento.objects.create(
                            usuario=request.user.profile,
                            otros_conocimientos=conocimiento)

                    messages.add_message(request, messages.SUCCESS,
                                         u'Otros conocimientos \
                                         editados exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class IdiomaView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template = 'formulario.html'
    form = IdiomaForm
    titulo = 'idioma'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))

        try:
            persona = Persona.objects.get(userprofile=request.user.profile)
        except:
            raise Http404

        self.diccionario.update({'form': self.form()})
        if 'idioma_id' in kwargs and not kwargs['idioma_id'] == None:
            try:
                idioma = Idioma.objects.get(id=int(kwargs['idioma_id']))
            except:
                raise Http404

            if idioma.persona == persona:
                self.form = self.form(instance=idioma)
            else:
                raise PermissionDenied

        # Si se elimina una Habilidad
        if kwargs['palabra'] == 'eliminar':
            idioma = Idioma.objects.get(id=int(kwargs['idioma_id']))
            idioma.delete()

            messages.add_message(request, messages.SUCCESS,
                                 u'El idioma %s ha sido \
                                 eliminada exitosamente' % (idioma.idioma))

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))

        persona = request.user.profile.persona
        if 'palabra' in kwargs and not kwargs['palabra'] == None:
            l_idioma = ListaIdiomas.objects.get(id=request.POST['idioma'])
            nivel_escrito = request.POST['nivel_escrito']
            nivel_leido = request.POST['nivel_leido']
            nivel_hablado = request.POST['nivel_hablado']

            # Buscamos que no se dupliquen idiomas
            idioma = Idioma.objects.filter(
                    persona=persona, idioma=request.POST['idioma'])
            if idioma.exists() and idioma.count() > 1:
                self.mensaje = u'Usted ya tiene %s cargado en base de datos, \
                        por favor edítela si es \
                        necesario' % (request.POST['idioma'])
                self.tipo_mensaje = u'error'
                self.template = 'perfil/editar_formulario.html'
                self.idioma_form = idioma_form(request)
            else:
                if kwargs['palabra'] == 'editar':
                    idioma = Idioma.objects.get(id=kwargs['idioma_id'])
                    idioma.idioma = l_idioma
                    idioma.nivel_escrito = nivel_escrito
                    idioma.nivel_leido = nivel_leido
                    idioma.nivel_hablado = nivel_hablado
                    idioma.save()

                    messages.add_message(request, messages.SUCCESS,
                                         u'El idioma %s ha sido \
                                         eliminada exitosamente' % (
                                             idioma.idioma))
                else:
                    idioma = Idioma.objects.create(
                            persona=persona, idioma=l_idioma,
                            nivel_escrito=nivel_escrito,
                            nivel_leido=nivel_leido,
                            nivel_hablado=nivel_hablado)

                    messages.add_message(request, messages.SUCCESS,
                                         u'El idioma %s ha sido \
                                         creado exitosamente' % (
                                             idioma.idioma))

                return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class CertificacionView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template = 'formulario.html'
    form = CertificacionForm
    titulo = u'certificación'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(id=usuario.profile.persona.id)
        except:
            raise Http404

        self.diccionario.update({'form': self.form()})
        if 'certificacion_id' in kwargs and \
                not kwargs['certificacion_id'] == None:
            nueva = False
            try:
                certificacion = Certificacion.objects.get(
                        id=int(kwargs['certificacion_id']))
            except:
                raise Http404

            if certificacion.persona == persona:
                self.form = self.form(instance=certificacion)
            else:
                raise PermissionDenied

        # Si se elimina una Certificación
        if kwargs['palabra'] == 'eliminar':
            certificacion = Certificacion.objects.get(
                    id=int(kwargs['certificacion_id']))
            certificacion.delete()

            messages.add_message(request, messages.SUCCESS,
                                 u'La certificación ha sido \
                                         eliminada exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        persona = request.user.profile.persona
        if 'palabra' in kwargs and not kwargs['palabra'] == None:
            pais = Pais.objects.get(id=request.POST['pais'])
            institucion = Institucion.objects.get(
                    id=request.POST['institucion'])
            fecha_inicio = datetime.datetime.strptime(
                    request.POST['fecha_inicio'], "%d/%m/%Y").strftime(
                            "%Y-%m-%d")
            fecha_fin = datetime.datetime.strptime(
                    request.POST['fecha_fin'], "%d/%m/%Y").strftime(
                            "%Y-%m-%d")

            if kwargs['palabra'] == 'editar':
                # Si se edita una Certificación
                # Búsqueda de variables con los IDs enviados por POST
                certificacion = Certificacion.objects.get(
                        id=int(kwargs['certificacion_id']))
                certificacion.titulo = request.POST['titulo']
                certificacion.codigo_certificacion = request.POST[
                        'codigo_certificacion']
                certificacion.institucion = institucion
                certificacion.fecha_inicio = fecha_inicio
                certificacion.fecha_fin = fecha_fin
                certificacion.lugar = pais

                certificacion.save()

                messages.add_message(request, messages.SUCCESS,
                                     u'La certificación ha sido \
                                             editada exitosamente')

            else:
                # Si se crea una Certificacion
                certificacion = Certificacion.objects.create(
                        persona=persona, institucion=institucion,
                        pais=pais, codigo_certificacion=request.POST[
                            'codigo_certificacion'],
                        titulo=request.POST['titulo'],
                        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

                messages.add_message(request, messages.SUCCESS,
                                     u'La certificación ha sido \
                                             creada exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class CursoView(View):
    '''
    Clase para la renderización de los datos de habilidad
    '''
    template = 'formulario.html'
    form = CursoForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = u'Cursos'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

    def get(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user
        nueva = True

        try:
            persona = Persona.objects.get(id=usuario.profile.persona.id)
        except:
            raise Http404

        self.diccionario.update({'formulario': self.form()})
        if 'curso_id' in kwargs and not kwargs['curso_id'] == None:
            nueva = False
            try:
                curso = Curso.objects.get(id=int(kwargs['curso_id']))
            except:
                raise Http404

            if curso.usuario == usuario.profile:
                self.form = self.form(instance=curso)
            else:
                raise PermissionDenied

        # Si se elimina un Curso
        if kwargs['palabra'] == 'eliminar':
            certificacion = Curso.objects.get(id=int(kwargs['curso_id']))
            certificacion.delete()

            messages.add_message(request, messages.SUCCESS,
                                 u'Curso eliminado exitosamente')

            return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        usuario = request.user

        self.form = self.form(request.POST)

        persona = request.user.profile.persona
        if self.form.is_valid():
            if 'palabra' in kwargs and not kwargs['palabra'] == None:
                estado = Estado.objects.get(id=request.POST['estado'])
                institucion = Institucion.objects.get(
                        id=request.POST['institucion'])
                fecha_inicio = datetime.datetime.strptime(
                        request.POST['fecha_inicio'], "%d/%m/%Y").strftime(
                                "%Y-%m-%d")
                fecha_fin = datetime.datetime.strptime(
                        request.POST['fecha_fin'], "%d/%m/%Y").strftime(
                                "%Y-%m-%d")

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

                    messages.add_message(request, messages.SUCCESS,
                                         u'Curso editado exitosamente')
                else:
                    # Si se crea un Curso
                    curso = Curso.objects.create(
                            usuario=usuario.profile, institucion=institucion,
                            estado=estado, titulo=request.POST['titulo'],
                            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
                            horas=equest.POST['horas'])

                    messages.add_message(request, messages.SUCCESS,
                                         u'Curso cargado exitosamente')

                return HttpResponseRedirect(reverse('perfil'))

        self.diccionario.update({'form': self.form})
        self.lista_filtros = lista_filtros(request.user)
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
        auditores = Auditor.objects.filter(
                Q(estatus__nombre='Renovado') | Q(
                    estatus__nombre='Inscrito'))

        paginator = Paginator(auditores, settings.LIST_PER_PAGE)

        page = request.GET.get('page')
        try:
            auditores = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            auditores = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999),
            # deliver last page of results.
            auditores = paginator.page(paginator.num_pages)

        self.diccionario.update({'auditores': auditores})
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )


class EvaluacionView(View):
    '''
    Clase para la renderización de la evaluación
    '''
    template = 'perfil/editar_formulario.html'
    evaluacion_form = EvaluacionForm
    mensaje = ''
    tipo_mensaje = ''
    titulo = u'evaluación'
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

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
        self.diccionario.update({'mensaje': self. mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        self.diccionario.update({'formulario': self.evaluacion_form})

        self.lista_filtros = lista_filtros(request.user)
        self.diccionario.update(self.lista_filtros)

        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )

    def post(self, request, *args, **kwargs):
        self.diccionario.update(csrf(request))
        self.evaluacion_form = self.evaluacion_form(request.POST)

        instrumento = kwargs['evaluacion_id']
        instrumento = Instrumento.objects.get(id=instrumento)
        puntaje = float(request.POST['puntaje'])

        # Filtrar las puntaciones del ultimo
        # registro de el instrumento a evaluar
        aprobacion = Aprobacion.objects.filter(
                instrumento=instrumento).latest()

        if puntaje > aprobacion.puntaje_total:
            self.tipo_mensaje = 'error'
            self.mensaje = u'Ha introducido %s puntos. La puntuación máxima \
                             permitida para %s es %s. Por favor, corrija el \
                             puntaje' % (puntaje, instrumento,
                                         aprobacion.puntaje_total)
        else:

            if self.evaluacion_form.is_valid():
                aspirante = kwargs['aspirante_id']
                aspirante = User.objects.get(id=aspirante)
                evaluacion = Evaluacion.objects.filter(usuario=aspirante)
                evaluacion = Evaluacion.objects.create(
                        usuario=aspirante.get_profile(),
                        tipo_prueba=instrumento, puntaje=puntaje)

                self.template = 'curriculum/aprobados.html'
                self.tipo_mensaje = 'success'
                self.mensaje = u'Evaluación cargada exitosamente.'

                notificar_entrevista_evaluacion(aspirante)

            else:
                if self.evaluacion_form.errors:
                    if '__all__' in self.evaluacion_form.errors:
                        self.mensaje = self.evaluacion_form.errors[
                                '__all__'][0]
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
    template = 'auditores/formulario.html'
    acreditacion_form = AcreditacionForm
    titulo = 'acreditar'
    mensaje = ''
    tipo_mensaje = ''
    lista_filtros = ''

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

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

            persona = Persona.objects.get(
                    userprofile__user__id=kwargs['usuario_id'])
            estado = Estatus.objects.get(nombre='Inscrito')
            auditor = Auditor.objects.create(
                    persona=persona, estatus=estado,
                    fecha=fecha_actual,
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
    template = 'formulario.html'
    cita_form = FijarCitaForm
    titulo = 'fijar cita'

    # Envío de variables a la plantilla a través de diccionario
    diccionario = {}
    diccionario.update({'titulo': titulo})

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
        self.diccionario.update({'form': self.cita_form})
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


class DatosView(View):
    '''
    Función para determinar cuáles son los requisitos
    faltantes por la persona segun su ámbito
    '''
    template = 'perfil/datos_usuario.html'
    diccionario = {}
    mensaje = ''
    tipo_mensaje = ''

    def get(self, request, *args, **kwargs):

        # Revisar si la persona ya es auditor (acreditado o no)
        if not request.user.get_profile(
                ).persona.auditor_set.get_query_set().exists():
            # Si no tiene ninguna, es un aspirante a auditor, no renovación

            # Se filtran los requisitos por ámbito...
            pass

        if not request.user.groups.filter(name__iexact='operador').exists():
            raise PermissionDenied

        try:
            persona = Persona.objects.get(userprofile=request.user.profile)
        except:
            raise Http404

        usuario = User.objects.get(id=kwargs['usuario_id'])

        self.diccionario.update({'persona': request.user.profile.persona})
        self.diccionario.update({'usuario': usuario})
        self.diccionario.update({'mensaje': self.mensaje})
        self.diccionario.update({'tipo_mensaje': self.tipo_mensaje})
        return render(request,
                      template_name=self.template,
                      dictionary=self.diccionario,
                      )
