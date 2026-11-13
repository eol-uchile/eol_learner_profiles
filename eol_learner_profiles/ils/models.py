# -*- coding: utf-8 -*-
"""
Modelos del instrumento ILS.

  - ILSDefinition: definición/versión de una encuesta ILS en Markdown/DSL.
  - CourseILSConfig: instrumento y política de reutilización por curso.
  - ILSUserResponse: respuestas crudas de un estudiante en un curso (fuente
    de verdad de las respuestas).

Las respuestas se guardan crudas y no se procesan: todavía no está definido
cómo se usan (escalas, patrones, etc.).

Django descubre estos modelos vía ``eol_learner_profiles/models.py``.
"""

import json

from django.conf import settings
from django.db import models
from django.utils import timezone

from opaque_keys.edx.django.models import CourseKeyField


class ILSDefinition(models.Model):
    """Definición y versionado de una encuesta ILS (Markdown/DSL)."""
    name = models.CharField(
        max_length=255,
        default='Encuesta ILS',
        help_text='Nombre descriptivo de la versión de la encuesta',
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text='Número de versión del objeto ILS',
    )
    markdown_content = models.TextField(
        help_text='Contenido de la encuesta en formato Markdown/DSL',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si esta versión está activa para ser seleccionada',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'eol_learner_profiles'
        ordering = ['-version']
        verbose_name = 'Definición de Encuesta ILS'
        verbose_name_plural = 'Definiciones de Encuestas ILS'

    def __str__(self):
        return "{} (v{})".format(self.name, self.version)

    @classmethod
    def get_active(cls):
        """Retorna la definición ILS marcada como activa globalmente."""
        return cls.objects.filter(is_active=True).order_by('-version').first()


class CourseILSConfig(models.Model):
    """
    Configuración por curso de la encuesta ILS: qué instrumento se aplica,
    la política de reutilización de respuestas entre cursos y la solicitud
    de re-toma del equipo docente.
    """

    POLICY_ASK = 'ask'
    POLICY_REQUIRE_NEW = 'require_new'
    POLICY_AUTO_REUSE = 'auto_reuse'
    REUSE_POLICY_CHOICES = [
        (
            POLICY_ASK,
            'Importar automáticamente la última respuesta del estudiante '
            '(si existe en otro curso); si no, pedir que responda',
        ),
        (
            POLICY_REQUIRE_NEW,
            'Exigir una nueva respuesta en este curso (no reutilizar)',
        ),
        (
            POLICY_AUTO_REUSE,
            'Reutilizar siempre la última respuesta conocida del estudiante',
        ),
    ]

    course_id = CourseKeyField(max_length=255, db_index=True, unique=True)
    ils_definition = models.ForeignKey(
        ILSDefinition,
        on_delete=models.PROTECT,
        related_name='course_configs',
        null=True,
        blank=True,
        help_text='Versión del instrumento ILS para este curso. '
                  'Si está vacío se usa la versión activa global.',
    )
    reuse_policy = models.CharField(
        max_length=20,
        choices=REUSE_POLICY_CHOICES,
        default=POLICY_ASK,
    )
    retake_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Si se define, las respuestas anteriores a esta fecha se '
                  'consideran vencidas y el estudiante debe responder de nuevo.',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'eol_learner_profiles'
        verbose_name = 'Configuración ILS de curso'
        verbose_name_plural = 'Configuraciones ILS de curso'

    def __str__(self):
        return "CourseILSConfig(course={}, policy={})".format(
            self.course_id, self.reuse_policy
        )

    @classmethod
    def get_for_course(cls, course_key):
        """Devuelve (creando si es necesario) la configuración del curso."""
        obj, _ = cls.objects.get_or_create(course_id=course_key)
        return obj

    def get_effective_definition(self):
        """Instrumento ILS efectivo: el del curso o, si no hay, el activo global."""
        return self.ils_definition or ILSDefinition.get_active()

    def is_response_stale(self, response):
        """True si ``response`` quedó vencida por una solicitud de re-toma."""
        if response is None:
            return True
        if self.retake_requested_at is None:
            return False
        return response.completed_at < self.retake_requested_at


class ILSUserResponse(models.Model):
    """Respuesta de un estudiante en un curso a una versión ILS específica."""

    SOURCE_DIRECT = 'direct'
    SOURCE_IMPORTED = 'imported'
    SOURCE_CHOICES = [
        (SOURCE_DIRECT, 'Respondida en este curso'),
        (SOURCE_IMPORTED, 'Importada desde otro curso'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ils_responses',
    )
    course_id = CourseKeyField(max_length=255, db_index=True)
    ils_definition = models.ForeignKey(
        ILSDefinition,
        on_delete=models.PROTECT,
        related_name='user_responses',
    )
    raw_responses = models.TextField(
        default='{}',
        blank=True,
        help_text='Respuestas del usuario en formato JSON {question_id: answer}',
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_DIRECT,
    )
    imported_from_course = CourseKeyField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Curso de origen cuando la respuesta fue importada.',
    )
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'eol_learner_profiles'
        unique_together = ('user', 'course_id', 'ils_definition')
        ordering = ['-completed_at']
        verbose_name = 'Respuesta de Encuesta ILS'
        verbose_name_plural = 'Respuestas de Encuestas ILS'

    def __str__(self):
        return "ILSResponse(user={}, course={}, version=v{})".format(
            self.user_id, self.course_id, self.ils_definition.version
        )

    def get_raw_responses(self):
        try:
            return json.loads(self.raw_responses) if self.raw_responses else {}
        except (json.JSONDecodeError, ValueError):
            return {}

    def set_raw_responses(self, data):
        self.raw_responses = json.dumps(data)

    @classmethod
    def latest_for_user(cls, user, exclude_course=None):
        """Respuesta ILS más reciente del usuario en cualquier curso (salvo ``exclude_course``)."""
        qs = cls.objects.filter(user=user)
        if exclude_course is not None:
            qs = qs.exclude(course_id=exclude_course)
        return qs.order_by('-completed_at').first()

    @classmethod
    def for_course(cls, user, course_key):
        """Respuesta más reciente del usuario en un curso específico."""
        return cls.objects.filter(
            user=user, course_id=course_key
        ).order_by('-completed_at').first()

