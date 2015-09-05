from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import resolve
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from authentication.tests import LoginTest
from authentication.models import UserProfile
from lugares.models import Estado, Pais, Institucion
from personas.models import Persona
from curriculum.models import Educacion, TipoEducacion

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

    def test_citas(self):
        self.client.logout()
        resolver = self.client.get(reverse('citas'))
        self.assertEqual(resolver.status_code, 302)

        self.client.login(username='batman', password='robin')
        resolver = self.client.get(reverse('citas'))
        # self.assertEqual(resolver.status_code, 200)

'''

    def test_laboral(self):
        resolver = self.client.get(reverse('laboral'))
        # self.assertEqual(resolver.status_code, 302)

    def test_conocimiento(self):
        resolver = self.client.get(reverse('conocimiento'))
        self.assertEqual(resolver.status_code, 302)

    def test_evaluacion(self):
        resolver = self.client.get(reverse('evaluacion'))
        self.assertEqual(resolver.status_code, 302)

    def test_competencia(self):
        resolver = self.client.get(reverse('competencia'))
        self.assertEqual(resolver.status_code, 302)

    def test_habilidad(self):
        resolver = self.client.get(reverse('habilidad'))
        self.assertEqual(resolver.status_code, 302)

    def test_idioma(self):
        resolver = self.client.get(reverse('idioma'))
        self.assertEqual(resolver.status_code, 302)

    def test_curso(self):
        resolver = self.client.get(reverse('curso'))
        self.assertEqual(resolver.status_code, 302)

    def test_certificacion(self):
        resolver = self.client.get(reverse('certificacion'))
        self.assertEqual(resolver.status_code, 302)
'''
