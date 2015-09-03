from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import urlencode

from personas.models import Persona, Estado

import datetime


class PerfilTest(TestCase):

    fixtures = ('paises.json', 'estados.json')

    def setUp(self):
        self.estado = Estado.objects.get_or_create(nombre='Aragua',
                                                   pais='Venezuela')
        self.nacimiento = datetime.datetime(1990, 8, 20)
        self.persona = \
            Persona.objects.get_or_create(cedula = '1234567',
                                          primer_nombre = 'Nombre1',
                                          segundo_nombre = 'Nombre2',
                                          primer_apellido = 'Apellido1',
                                          segundo_apellido = 'Apellido2',
                                          genero = '0',
                                          direccion = self.estado,
                                          fecha_nacimiento = self.nacimiento,
                                          tlf_reside = '01231234567',
                                          tlf_movil = '01231234567',
                                          tlf_oficina = '01231234567',
                                          tlf_contacto = 'tlf_reside',
                                          estado_civil = 's',
                                          email = 'correo@example.com')

        self.read_update_delete_url = \
            reverse("detalles_perfil", kwargs={"pk": "1"})

