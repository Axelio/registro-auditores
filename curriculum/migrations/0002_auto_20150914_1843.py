# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='dia',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='cita',
            name='hora',
            field=models.TimeField(),
        ),
    ]
