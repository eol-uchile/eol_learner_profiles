# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import opaque_keys.edx.django.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ILSDefinition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Encuesta ILS', help_text='Nombre descriptivo de la versión de la encuesta', max_length=255)),
                ('version', models.PositiveIntegerField(default=1, help_text='Número de versión del objeto ILS')),
                ('markdown_content', models.TextField(help_text='Contenido de la encuesta en formato Markdown/DSL')),
                ('is_active', models.BooleanField(default=True, help_text='Indica si esta versión está activa para ser seleccionada')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Definición de Encuesta ILS',
                'verbose_name_plural': 'Definiciones de Encuestas ILS',
                'ordering': ['-version'],
            },
        ),
        migrations.CreateModel(
            name='RecommendationCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.SlugField(help_text='Identificador estable, p.ej. "generic".', max_length=64, unique=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Caso de recomendación',
                'verbose_name_plural': 'Casos de recomendación',
                'ordering': ['key'],
            },
        ),
        migrations.CreateModel(
            name='CourseILSConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', opaque_keys.edx.django.models.CourseKeyField(db_index=True, max_length=255, unique=True)),
                ('reuse_policy', models.CharField(choices=[('ask', 'Importar automáticamente la última respuesta del estudiante (si existe en otro curso); si no, pedir que responda'), ('require_new', 'Exigir una nueva respuesta en este curso (no reutilizar)'), ('auto_reuse', 'Reutilizar siempre la última respuesta conocida del estudiante')], default='ask', max_length=20)),
                ('retake_requested_at', models.DateTimeField(blank=True, help_text='Si se define, las respuestas anteriores a esta fecha se consideran vencidas y el estudiante debe responder de nuevo.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ils_definition', models.ForeignKey(blank=True, help_text='Versión del instrumento ILS para este curso. Si está vacío se usa la versión activa global.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='course_configs', to='eol_learner_profiles.ilsdefinition')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Configuración ILS de curso',
                'verbose_name_plural': 'Configuraciones ILS de curso',
            },
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graph', models.CharField(choices=[('videos', 'Videos'), ('evaluations', 'Evaluaciones'), ('consistency', 'Constancia')], help_text='Gráfico del dashboard.', max_length=32)),
                ('first_level', models.CharField(choices=[('low', '< P33'), ('mid', 'P33 – P66'), ('high', '> P66')], help_text='Nivel de la 1ª métrica del gráfico.', max_length=8)),
                ('second_level', models.CharField(choices=[('low', '< P33'), ('mid', 'P33 – P66'), ('high', '> P66')], help_text='Nivel de la 2ª métrica del gráfico.', max_length=8)),
                ('text', models.TextField(help_text='Puede usar {name}; lo rellena el dashboard.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recommendations', to='eol_learner_profiles.recommendationcase')),
            ],
            options={
                'verbose_name': 'Recomendación',
                'verbose_name_plural': 'Recomendaciones',
                'ordering': ['case', 'graph', 'first_level', 'second_level'],
                'unique_together': {('case', 'graph', 'first_level', 'second_level')},
            },
        ),
        migrations.CreateModel(
            name='ILSUserResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', opaque_keys.edx.django.models.CourseKeyField(db_index=True, max_length=255)),
                ('raw_responses', models.TextField(blank=True, default='{}', help_text='Respuestas del usuario en formato JSON {question_id: answer}')),
                ('source', models.CharField(choices=[('direct', 'Respondida en este curso'), ('imported', 'Importada desde otro curso')], default='direct', max_length=20)),
                ('imported_from_course', opaque_keys.edx.django.models.CourseKeyField(blank=True, help_text='Curso de origen cuando la respuesta fue importada.', max_length=255, null=True)),
                ('completed_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('ils_definition', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_responses', to='eol_learner_profiles.ilsdefinition')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ils_responses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Respuesta de Encuesta ILS',
                'verbose_name_plural': 'Respuestas de Encuestas ILS',
                'ordering': ['-completed_at'],
                'unique_together': {('user', 'course_id', 'ils_definition')},
            },
        ),
    ]
