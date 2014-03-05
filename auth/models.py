# -*- coding: UTF8 -*-
from django.conf import settings
from django.db import models
from personas.models import Persona
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user=models.ForeignKey(User)
    persona=models.OneToOneField(Persona,null=False,help_text=u'Por favor, ingrese nombre, apellido o cédula de la persona')

    class Meta:
        verbose_name='Usuario'
        unique_together=('user','persona')

    def __unicode__(self):
        return u'%s %s' %(self.persona.primer_nombre, self.persona.primer_apellido)

def funcion(u):
    if not hasattr(u, '_cached_profile'):
        u._cached_profile = UserProfile.objects.get_or_create(user=u)[0]
    return u._cached_profile 
User.profile = property(funcion)

class Mensaje(models.Model):
    caso = models.CharField(max_length=100)
    mensaje = models.TextField()
    class Meta:
        db_table ='mensaje'
    def __unicode__(self):
        return u'%s' %(self.caso)

