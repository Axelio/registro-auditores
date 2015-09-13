# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('lugares', '__first__'),
        ('authentication', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Auditor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateField()),
                ('observacion', models.TextField(help_text=b'Razones por la cual se acredita o desacredita al auditor', verbose_name='observaci\xf3n')),
            ],
            options={
                'db_table': 'auditor',
                'verbose_name': 'auditor',
                'verbose_name_plural': 'auditores',
            },
        ),
        migrations.CreateModel(
            name='CertificadoElectronico',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('certificado', models.CharField(max_length=5000)),
                ('usuario', models.ForeignKey(to='authentication.UserProfile')),
            ],
            options={
                'db_table': 'certificado_electonico',
                'verbose_name': 'certificado electr\xf3nico',
                'verbose_name_plural': 'certificados electr\xf3nicos',
            },
        ),
        migrations.CreateModel(
            name='Estatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=50)),
                ('dependencia', models.ForeignKey(blank=True, to='personas.Estatus', null=True)),
            ],
            options={
                'db_table': 'estatus',
                'verbose_name_plural': 'estatus',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cedula', models.CharField(help_text='Los datos deben ser \xfanicamente n\xfameros', unique=True, max_length=50, verbose_name='C\xe9dula')),
                ('primer_nombre', models.CharField(help_text=b'Indique su primer nombre', max_length=50)),
                ('segundo_nombre', models.CharField(help_text=b'Indique su segundo nombre, si posee', max_length=50, blank=True)),
                ('primer_apellido', models.CharField(help_text=b'Indique su primer apellido', max_length=50)),
                ('segundo_apellido', models.CharField(help_text=b'Indique su segundo apellido', max_length=50, blank=True)),
                ('genero', models.IntegerField(default=0, help_text=b'Seleccione su g\xc3\xa9nero', verbose_name='g\xe9nero', choices=[(0, b'Masculino'), (1, b'Femenino')])),
                ('direccion', models.TextField(help_text='Indique direcci\xf3n donde reside', verbose_name='direcci\xf3n', blank=True)),
                ('fecha_nacimiento', models.DateField(help_text=b'Indique su fecha de nacimiento', null=True, blank=True)),
                ('tlf_reside', models.CharField(help_text='N\xfamero telef\xf3nico de residencia', max_length=15, verbose_name='tel\xe9fono de residencia')),
                ('tlf_movil', models.CharField(help_text='N\xfamero telef\xf3nico celular', max_length=15, verbose_name='tel\xe9fono m\xf3vil', blank=True)),
                ('tlf_oficina', models.CharField(help_text='N\xfamero telef\xf3nico de oficina', max_length=15, verbose_name='tel\xe9fono de oficina', blank=True)),
                ('tlf_contacto', models.CharField(default=b'fijo', help_text='tome en cuenta que                     esta informaci\xf3n ser\xe1 p\xfablica', max_length=10, verbose_name='tel\xe9fono de contacto', choices=[(b'movil', 'Tel\xe9fono m\xf3vil'), (b'fijo', 'Tel\xe9fono de residencia'), (b'oficina', 'Tel\xe9fono de oficina')])),
                ('estado_civil', models.CharField(default=b's', help_text=b'Se\xc3\xb1ale su estado civil', max_length=15, blank=True, choices=[(b's', b'Soltero(a)'), (b'c', b'Casado(a)'), (b'd', b'Divorciado(a)'), (b'v', b'Viudo(a)')])),
                ('email', models.EmailField(help_text=b'tome en cuenta que                     esta informaci\xc3\xb3n ser\xc3\xa1 p\xc3\xbablica', unique=True, max_length=254, verbose_name='Email', validators=[django.core.validators.MaxLengthValidator(2000)])),
                ('reside', models.ForeignKey(help_text='Estado de residencia', to='lugares.Estado')),
            ],
            options={
                'db_table': 'personas',
                'verbose_name': 'persona',
            },
        ),
        migrations.AddField(
            model_name='auditor',
            name='estatus',
            field=models.ForeignKey(to='personas.Estatus'),
        ),
        migrations.AddField(
            model_name='auditor',
            name='persona',
            field=models.ForeignKey(to='personas.Persona'),
        ),
    ]
