from django.db import models
from personas.models import Persona


class Ubicacion(models.Model):
    '''
    Modelo para almacenar la geolocalizacion de una persona
    '''
    persona = models.ForeignKey(Persona)
    lat = models.CharField(max_length=20)
    lng = models.CharField(max_length=20)

    def __unicode__(self):
        return u'%s' % (self.persona)
