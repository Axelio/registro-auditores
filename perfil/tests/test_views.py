from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import urlencode
from django.test.client import Client
from django.contrib.auth.models import User

from authentication.models import UserProfile
from personas.models import Persona, Estado
from lugares.models import Estado, Pais, Institucion
from curriculum.models import Educacion, TipoEducacion, Laboral

import datetime


class PerfilTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.get_or_create(nombre='Aragua',
                                                   pais='Venezuela')
        self.nacimiento = datetime.datetime(1990, 8, 20)
        self.persona = \
            Persona.objects.get_or_create(cedula='1234567',
                                          primer_nombre='Nombre1',
                                          segundo_nombre='Nombre2',
                                          primer_apellido='Apellido1',
                                          segundo_apellido='Apellido2',
                                          genero='0',
                                          direccion=self.estado,
                                          fecha_nacimiento=self.nacimiento,
                                          tlf_reside='01231234567',
                                          tlf_movil='01231234567',
                                          tlf_oficina='01231234567',
                                          tlf_contacto='tlf_reside',
                                          estado_civil='s',
                                          email='correo@example.com')

        self.read_update_delete_url = \
            reverse("detalles_perfil", kwargs={"pk": "1"})


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

        self.institucion = Institucion.objects.create(
                nombre='{0}'.format('1'), estado=self.estado)

        self.tipo_educacion = TipoEducacion.objects.create(
                tipo='{0}'.format('1'))

        self.f_inicio = datetime.datetime(1994, 8, 20)

        self.f_fin = datetime.datetime(2000, 8, 20)

        self.educacion = Educacion.objects.create(persona=self.persona,
                                                  titulo='Superheroe',
                                                  institucion=self.institucion,
                                                  tipo=self.tipo_educacion,
                                                  fecha_inicio=self.f_inicio,
                                                  fecha_fin=self.f_fin)

        # Se preparan los datos para enviarlos a la vista
        self.f_inicio = self.f_inicio.strftime('%d/%m/%Y')
        self.f_fin = self.f_fin.strftime('%d/%m/%Y')

    def test_create(self):
        # Se logea al usuario
        self.client.login(username='batman', password='robin')

        # Se imprimen las educaciones antes del test
        self.assertEquals(Educacion.objects.count(), 1)

        # Se almacenan los datos necesarios en el diccionario "post"
        post = {'persona': self.persona, 'titulo': 'Superheroe',
                'institucion': self.institucion, 'tipo': self.tipo_educacion,
                'fecha_inicio': self.f_inicio, 'fecha_fin': self.f_fin}

        # Se envian los datos a la vista para crear una nueva Educacion
        resolve = self.client.post(
                reverse('educacion', kwargs={'palabra': 'nueva'}), post)

        # Se comprueba que haya una nueva Educacion
        self.assertEquals(Educacion.objects.count(), 2)

    def test_edit(self):
        # Se logea al usuario
        self.client.login(username='batman', password='robin')

        # Se imprimen las educaciones antes del test
        self.assertEquals(self.educacion.titulo, 'Superheroe')

        # Se almacenan los datos necesarios en el diccionario "post"
        post = {'persona': self.persona, 'titulo': 'Guardian de Ciudad Gotica',
                'institucion': self.institucion, 'tipo': self.tipo_educacion,
                'fecha_inicio': self.f_inicio, 'fecha_fin': self.f_fin}

        # Se envian los datos a la vista para crear una nueva Educacion
        resolve = self.client.post(
                reverse('educacion', kwargs={
                    'palabra': 'editar', 'educacion_id': self.educacion.id}),
                post)

        self.educacion = Educacion.objects.first()

        # Se comprueba que haya una nueva Educacion
        self.assertEquals(self.educacion.titulo, 'Guardian de Ciudad Gotica')

    def test_delete(self):
        # Se logea al usuario
        self.client.login(username='batman', password='robin')

        # Se imprimen las educaciones antes del test
        self.assertEquals(Educacion.objects.count(), 1)

        # Se busca el primer object Educacion
        self.educacion = Educacion.objects.first()

        # Se envian los datos a la vista para eliminar la Educacion
        resolve = self.client.get(
                reverse('educacion',
                        kwargs={
                            'palabra': 'eliminar',
                            'educacion_id': self.educacion.id}))

        # Se comprueba que no haya ninguna  Educacion
        self.assertEquals(Educacion.objects.count(), 0)


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
                trabajo_actual=True, retiro='Ninguna',
                direccion_empresa='Ciudad Gotica')

        # Se preparan los datos para enviarlos a la vista
        self.f_inicio = self.f_inicio.strftime('%d/%m/%Y')
        self.f_fin = self.f_fin.strftime('%d/%m/%Y')

    def test_create(self):
        # Se logea al usuario
        self.client.login(username='batman', password='robin')

        # Se imprimen las informaciones laborales antes del test
        self.assertEquals(Laboral.objects.count(), 1)

        # Se almacenan los datos necesarios en el diccionario "post"
        post = {'usuario': self.userprofile, 'empresa': 'Liga de la Justicia',
                'sector': 'Social', 'estado': self.estado.id,
                'telefono': '5555555', 'cargo': 'Superheroe',
                'funcion': 'Salvar al mundo', 'fecha_inicio': self.f_inicio,
                'fecha_fin': self.f_fin, 'trabajo_actual': True, 'retiro': 'Ninguna',
                'direccion_empresa': 'Ciudad Gotica'}

        # Se envian los datos a la vista para crear una nueva
        # informacion Laboral
        resolve = self.client.post(
                reverse('laboral', kwargs={'palabra': 'nueva'}), post)

        # Se comprueba que haya una nueva informacion Laboral
        self.assertEquals(Laboral.objects.count(), 2)

    def test_edit(self):
        # Se logea al usuario
        self.client.login(username='batman', password='robin')

        # Se imprimen las informaciones laborales antes del test
        self.assertEquals(self.laboral.cargo, 'Superheroe')

        # Se almacenan los datos necesarios en el diccionario "post"
        post = {'usuario': self.userprofile, 'empresa': 'Liga de la Justicia',
                'sector': 'Social', 'estado': self.estado.id,
                'telefono': '5555555', 'cargo': 'Guardian de Ciudad Gotica',
                'funcion': 'Salvar al mundo', 'fecha_inicio': self.f_inicio,
                'fecha_fin': self.f_fin, 'trabajo_actual': True, 'retiro': 'Ninguna',
                'direccion_empresa': 'Ciudad Gotica'}

        # Se envian los datos a la vista para crear una nueva
        # informacion Laboral
        resolve = self.client.post(
                reverse('laboral', kwargs={
                    'palabra': 'editar', 'laboral_id': self.laboral.id}),
                post)

        self.laboral= Laboral.objects.first()

        # Se comprueba que se haya editado el cargo laboral
        self.assertEquals(self.laboral.cargo, 'Guardian de Ciudad Gotica')

    def test_delete(self):
        # Se logea al usuario
        self.client.login(username='batman', password='robin')

        # Se comparan los Laborales antes del test
        self.assertEquals(Laboral.objects.count(), 1)

        # Se busca el primer object Educacion
        self.laboral = laboral.objects.first()

        # Se envian los datos a la vista para eliminar la info laboral
        resolve = self.client.get(
                reverse('laboral',
                        kwargs={
                            'palabra': 'eliminar',
                            'laboral_id': self.laboral.id}))

        # Se comprueba que no haya ninguna info laboral
        self.assertEquals(Laboral.objects.count(), 0)
