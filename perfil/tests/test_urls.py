from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from authentication.models import UserProfile
from lugares.models import Estado, Pais, Institucion
from personas.models import Persona
from curriculum.models import Educacion, TipoEducacion, Laboral

import datetime


class PerfilTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('batman',
                                             'batman@ligadelajusticia.com',
                                             'robin')
        self.pais = Pais.objects.create(nombre='Venezuela')
        self.estado = Estado.objects.create(nombre='Aragua', pais=self.pais)
        self.nacimiento = datetime.datetime(1990, 8, 20)
        self.persona = Persona.objects.create(cedula='1234567',
                                              primer_nombre='Nombre1',
                                              segundo_nombre='Nombre2',
                                              primer_apellido='Apellido1',
                                              segundo_apellido='Apellido2',
                                              genero='0',
                                              reside=self.estado,
                                              fecha_nacimiento=self.nacimiento,
                                              tlf_reside='01231234567',
                                              tlf_movil='01231234567',
                                              tlf_oficina='01231234567',
                                              tlf_contacto='tlf_reside',
                                              estado_civil='s',
                                              email='correo@example.com')
        self.userprofile = UserProfile.objects.create(user=self.user,
                                                      persona=self.persona)

    def test_perfil(self):
        resolver = self.client.get('/perfil/')
        self.assertEqual(resolver.status_code, 302)

    def test_detalles_perfil(self):
        self.client.logout()
        resolver = self.client.get('/perfil/{0}/'.format(self.persona.id))
        self.assertEqual(resolver.status_code, 302)

        self.client.login(username='batman', password='robin')
        resolver = self.client.get('/perfil/{0}/'.format(self.persona.id))
        self.assertEqual(resolver.status_code, 200)


class EducacionTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user('batman',
                                             'batman@ligadelajusticia.com',
                                             'robin')

        self.pais = Pais.objects.create(nombre='Venezuela')

        self.estado = Estado.objects.create(nombre='Aragua', pais=self.pais)

        self.nacimiento = datetime.datetime(1990, 8, 20)

        self.persona = Persona.objects.create(cedula='1234567',
                                              primer_nombre='Nombre1',
                                              segundo_nombre='Nombre2',
                                              primer_apellido='Apellido1',
                                              segundo_apellido='Apellido2',
                                              genero='0',
                                              reside=self.estado,
                                              fecha_nacimiento=self.nacimiento,
                                              tlf_reside='01231234567',
                                              tlf_movil='01231234567',
                                              tlf_oficina='01231234567',
                                              tlf_contacto='tlf_reside',
                                              estado_civil='s',
                                              email='correo@example.com')

        self.userprofile = UserProfile.objects.create(user=self.user,
                                                      persona=self.persona)

    def test_add(self):
        '''
        Se prueba el enlace para agregar nueva educacion
        '''
        # Se deslogea todo usuario
        self.client.logout()

        # Se almacenan los datos de la URL de Educacion
        resolver = self.client.get(
                reverse('educacion', kwargs={'palabra': 'nueva'}))

        # Se comprueban los codigos de estado del intento de ingreso
        self.assertEqual(resolver.status_code, 302)

        # Batman se logea
        self.client.login(username='batman', password='robin')

        # Se almacenan los datos de la URL de Educacion
        resolver = self.client.get(
                reverse('educacion', kwargs={'palabra': 'nueva'}))

        # Se comprueban los codigos de estado del intento de ingreso
        self.assertEqual(resolver.status_code, 200)

    def test_edit(self):
        '''
        Se prueba el enlace para agregar nueva educacion
        '''
        # Se deslogea todo usuario
        self.client.logout()

        # Se almacenan los datos de la URL de Educacion
        resolver = self.client.get(
                reverse('educacion', kwargs={'palabra': 'editar'}))

        # Se comprueban los codigos de estado del intento de ingreso
        self.assertEqual(resolver.status_code, 302)

        # Batman se logea
        self.client.login(username='batman', password='robin')

        # Se almacenan los datos de la URL de Educacion
        resolver = self.client.get(
                reverse('educacion', kwargs={'palabra': 'editar'}))

        # Se comprueban los codigos de estado del intento de ingreso
        self.assertEqual(resolver.status_code, 200)


class LaboralTest(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user('batman',
                                             'batman@ligadelajusticia.com',
                                             'robin')

        self.pais = Pais.objects.create(nombre='Venezuela')

        self.estado = Estado.objects.create(nombre='Aragua', pais=self.pais)

        self.nacimiento = datetime.datetime(1990, 8, 20)

        self.persona = Persona.objects.create(
                cedula='1234567', primer_nombre='Nombre1',
                segundo_nombre='Nombre2', primer_apellido='Apellido1',
                segundo_apellido='Apellido2', genero='0', reside=self.estado,
                fecha_nacimiento=self.nacimiento, tlf_reside='01231234567',
                tlf_movil='01231234567', tlf_oficina='01231234567',
                tlf_contacto='tlf_reside', estado_civil='s',
                email='correo@example.com')

        self.userprofile = UserProfile.objects.create(user=self.user,
                                                      persona=self.persona)
        self.f_inicio = datetime.datetime(1994, 8, 20)

        self.f_fin = datetime.datetime(2000, 8, 20)

        self.laboral = Laboral.objects.create(
                usuario=self.userprofile, empresa='Liga de la Justicia',
                sector='Social', estado=self.estado, telefono='5555555',
                cargo='Superheroe', funcion='Salvar al mundo',
                fecha_inicio=self.f_inicio, fecha_fin=self.f_fin,
                trabajo_actual=True, retiro='',
                direccion_empresa='Ciudad Gotica')

    def test_add(self):
        '''
        Se prueba el enlace para agregar nueva informacion laboral
        '''
        # Se deslogea todo usuario
        self.client.logout()

        # Se almacenan los datos de la URL de Educacion
        resolver = self.client.get(
                reverse('laboral', kwargs={'palabra': 'nueva'}))

        # Se comprueban los codigos de estado del intento de ingreso
        self.assertEqual(resolver.status_code, 302)

        # Batman se logea
        self.client.login(username='batman', password='robin')

        # Se almacenan los datos de la URL de Educacion
        resolver = self.client.get(
                reverse('educacion', kwargs={'palabra': 'nueva'}))

        # Se comprueban los codigos de estado del intento de ingreso
        self.assertEqual(resolver.status_code, 200)

    def test_edit(self):
        '''
        Se prueba el enlace para agregar nueva educacion
        '''
        # Se deslogea todo usuario
        self.client.logout()

        # Se almacenan los datos de la URL de Educacion
        resolver = self.client.get(
                reverse('laboral', kwargs={'palabra': 'editar'}))

        # Se comprueban los codigos de estado del intento de ingreso
        self.assertEqual(resolver.status_code, 302)

        # Batman se logea
        self.client.login(username='batman', password='robin')

        # Se almacenan los datos de la URL de Educacion
        resolver = self.client.get(
                reverse('laboral', kwargs={'palabra': 'editar'}))

        # Se comprueban los codigos de estado del intento de ingreso
        self.assertEqual(resolver.status_code, 200)
