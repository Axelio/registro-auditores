# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lugares', '__first__'),
        ('authentication', '__first__'),
        ('personas', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ambito',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.CharField(help_text='Ej: Inscripci\xf3n, renovaci\xf3n, etc.', max_length=30)),
            ],
            options={
                'db_table': 'ambito',
                'verbose_name': '\xe1mbito',
            },
        ),
        migrations.CreateModel(
            name='Aprobacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('puntaje_aprobatorio', models.FloatField()),
                ('puntaje_total', models.FloatField(verbose_name='puntaje m\xe1ximo')),
                ('fecha', models.DateField(auto_now_add=True, verbose_name=b'fijada')),
            ],
            options={
                'get_latest_by': 'fecha',
                'verbose_name': 'aprobaci\xf3n',
                'verbose_name_plural': 'aprobaciones',
                'db_table': 'aprobacion',
            },
        ),
        migrations.CreateModel(
            name='Certificacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=500, verbose_name='t\xedtulo')),
                ('codigo_certificacion', models.CharField(max_length=30, verbose_name='c\xf3digo de certificaci\xf3n', blank=True)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True)),
                ('institucion', models.ForeignKey(verbose_name='instituci\xf3n', to='lugares.Institucion')),
                ('pais', models.ForeignKey(to='lugares.Pais')),
                ('persona', models.ForeignKey(to='personas.Persona')),
            ],
            options={
                'db_table': 'certificacion',
                'verbose_name': 'certificaci\xf3n',
                'verbose_name_plural': 'certificaciones',
            },
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dia', models.DateField(default=1)),
                ('hora', models.TimeField(default=1)),
                ('cita_fijada', models.BooleanField(default=False)),
                ('usuario', models.ForeignKey(to='authentication.UserProfile')),
            ],
            options={
                'db_table': 'cita',
            },
        ),
        migrations.CreateModel(
            name='Competencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('puntaje', models.FloatField()),
                ('fecha', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'competencia',
            },
        ),
        migrations.CreateModel(
            name='Conocimiento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('otros_conocimientos', models.TextField(help_text='Escriba aqu\xed los conocimientos extras')),
                ('usuario', models.ForeignKey(to='authentication.UserProfile')),
            ],
            options={
                'db_table': 'conocimiento',
            },
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=150, verbose_name='t\xedtulo')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('horas', models.PositiveIntegerField()),
                ('estado', models.ForeignKey(to='lugares.Estado')),
                ('institucion', models.ForeignKey(verbose_name='instituci\xf3n', to='lugares.Institucion')),
                ('usuario', models.ForeignKey(to='authentication.UserProfile')),
            ],
            options={
                'db_table': 'curso',
            },
        ),
        migrations.CreateModel(
            name='Educacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(help_text='t\xedtulo acad\xe9mico que obtuvo', max_length=50, verbose_name='t\xedtulo acad\xe9mico')),
                ('fecha_inicio', models.DateField(help_text='fecha en la que inici\xf3')),
                ('fecha_fin', models.DateField(help_text='fecha en la que termin\xf3')),
                ('institucion', models.ForeignKey(verbose_name='instituci\xf3n', to='lugares.Institucion', help_text='indique la instituci\xf3n en la cual particip\xf3')),
                ('persona', models.ForeignKey(to='personas.Persona')),
            ],
            options={
                'db_table': 'educacion',
                'verbose_name': 'educaci\xf3n',
                'verbose_name_plural': 'educaciones',
            },
        ),
        migrations.CreateModel(
            name='Evaluacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('puntaje', models.FloatField()),
                ('fecha', models.DateField(auto_now_add=True)),
            ],
            options={
                'db_table': 'evaluacion',
                'verbose_name': 'evaluaci\xf3n',
                'verbose_name_plural': 'evaluaciones',
            },
        ),
        migrations.CreateModel(
            name='Habilidad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('habilidad', models.CharField(max_length=50)),
                ('usuario', models.ForeignKey(to='authentication.UserProfile')),
            ],
            options={
                'db_table': 'habilidad',
                'verbose_name_plural': 'habilidades',
            },
        ),
        migrations.CreateModel(
            name='Idioma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nivel_leido', models.CharField(max_length=10, verbose_name='nivel de lectura', choices=[(b'4', b'Fluido'), (b'3', b'Alto'), (b'2', b'Medio'), (b'1', b'Bajo')])),
                ('nivel_escrito', models.CharField(max_length=10, verbose_name='nivel de escritura', choices=[(b'4', b'Fluido'), (b'3', b'Alto'), (b'2', b'Medio'), (b'1', b'Bajo')])),
                ('nivel_hablado', models.CharField(max_length=10, verbose_name='nivel de conversaci\xf3n', choices=[(b'4', b'Fluido'), (b'3', b'Alto'), (b'2', b'Medio'), (b'1', b'Bajo')])),
            ],
            options={
                'ordering': ('-idioma',),
                'db_table': 'idioma',
            },
        ),
        migrations.CreateModel(
            name='Instrumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(help_text='Ej: Inscripci\xf3n, renovaci\xf3n, etc.', max_length=30)),
                ('ambito', models.ForeignKey(verbose_name='\xe1mbito', to='curriculum.Ambito')),
            ],
            options={
                'db_table': 'instrumento',
            },
        ),
        migrations.CreateModel(
            name='Laboral',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('empresa', models.CharField(max_length=100)),
                ('sector', models.CharField(help_text='Financiero, Industrial, Tecnol\xf3gico, entre otros.', max_length=60)),
                ('telefono', models.CharField(max_length=15, verbose_name='tel\xe9fono')),
                ('cargo', models.CharField(max_length=60)),
                ('funcion', models.TextField(help_text='indique la funci\xf3n o funciones que desempe\xf1aba', verbose_name='funci\xf3n')),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(null=True)),
                ('trabajo_actual', models.BooleanField(default=False)),
                ('retiro', models.CharField(max_length=60, verbose_name='raz\xf3n de retiro')),
                ('direccion_empresa', models.TextField(verbose_name='direcci\xf3n de empresa')),
                ('estado', models.ForeignKey(to='lugares.Estado')),
                ('usuario', models.ForeignKey(to='authentication.UserProfile')),
            ],
            options={
                'db_table': 'laboral',
                'verbose_name_plural': 'laborales',
            },
        ),
        migrations.CreateModel(
            name='ListaCompetencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=200)),
                ('puntaje_maximo', models.FloatField(verbose_name='puntaje m\xe1ximo')),
                ('puntaje_minimo', models.FloatField(default=0.0, verbose_name='puntaje m\xednimo')),
                ('tipo_puntaje', models.CharField(max_length=10, choices=[(b'int', b'Cantidades'), (b'float', b'Puntos')])),
            ],
            options={
                'db_table': 'lista_competencia',
                'verbose_name': 'lista de competancia',
                'verbose_name_plural': 'lista de competancias',
            },
        ),
        migrations.CreateModel(
            name='ListaIdiomas',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'lista_idiomas',
                'verbose_name': 'lista de idiomas',
                'verbose_name_plural': 'lista de idiomas',
            },
        ),
        migrations.CreateModel(
            name='TipoCompetencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=50)),
                ('puntaje_maximo', models.FloatField(verbose_name='puntaje m\xe1ximo')),
            ],
            options={
                'db_table': 'tipo_competencia',
                'verbose_name': 'tipo de competencia',
                'verbose_name_plural': 'tipos de competencias',
            },
        ),
        migrations.CreateModel(
            name='TipoEducacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.CharField(help_text='Ej: Pregrado, Doctorado, Maestr\xeda, entre otros.', max_length=30)),
            ],
            options={
                'db_table': 'tipo_educacion',
                'verbose_name': 'tipos de educaci\xf3n',
                'verbose_name_plural': 'tipos de educaciones',
            },
        ),
        migrations.AddField(
            model_name='listacompetencia',
            name='tipo',
            field=models.ForeignKey(to='curriculum.TipoCompetencia'),
        ),
        migrations.AddField(
            model_name='idioma',
            name='idioma',
            field=models.ForeignKey(to='curriculum.ListaIdiomas'),
        ),
        migrations.AddField(
            model_name='idioma',
            name='persona',
            field=models.ForeignKey(to='personas.Persona'),
        ),
        migrations.AddField(
            model_name='evaluacion',
            name='tipo_prueba',
            field=models.ForeignKey(to='curriculum.Instrumento'),
        ),
        migrations.AddField(
            model_name='evaluacion',
            name='usuario',
            field=models.ForeignKey(to='authentication.UserProfile'),
        ),
        migrations.AddField(
            model_name='educacion',
            name='tipo',
            field=models.ForeignKey(verbose_name='nivel acad\xe9mico', to='curriculum.TipoEducacion'),
        ),
        migrations.AddField(
            model_name='competencia',
            name='tipo',
            field=models.ForeignKey(to='curriculum.TipoCompetencia'),
        ),
        migrations.AddField(
            model_name='competencia',
            name='usuario',
            field=models.ForeignKey(to='authentication.UserProfile'),
        ),
        migrations.AddField(
            model_name='aprobacion',
            name='instrumento',
            field=models.ForeignKey(to='curriculum.Instrumento'),
        ),
    ]
