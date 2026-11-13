# -*- coding: utf-8 -*-
"""
Máquina de estados de la encuesta ILS dentro de la pestaña.

Responde a la pregunta: cuando un estudiante abre la pestaña, ¿debe ver la
encuesta o su resultado?  Y encapsula las escrituras posibles:

  * :func:`save_direct_response`  -> el estudiante respondió en este curso.
  * :func:`import_latest_response` -> se reutiliza su última respuesta de otro curso.
  * (lectura) :func:`resolve_state` -> qué panel corresponde mostrar.
"""

import json

from django.db import transaction
from django.utils import timezone

from .models import CourseILSConfig, ILSUserResponse
from .parser import parse_ils_markdown

# Estados posibles
STATE_DASHBOARD = 'dashboard'
STATE_SURVEY = 'survey'
STATE_NO_INSTRUMENT = 'no_instrument'

# Motivos por los que se pide responder (para el texto del panel)
REASON_FIRST_TIME = 'first_time'
REASON_RETAKE_REQUESTED = 'retake_requested'
REASON_REQUIRE_NEW = 'require_new'


class ILSState(object):
    """Resultado de :func:`resolve_state`."""

    def __init__(self, name, config, ils_def=None, response=None,
                 reason=None, parsed_survey=None):
        self.name = name
        self.config = config
        self.ils_def = ils_def
        self.response = response
        self.reason = reason
        self.parsed_survey = parsed_survey

    @property
    def show_survey(self):
        return self.name == STATE_SURVEY


def _parsed(ils_def):
    if not ils_def:
        return None
    return parse_ils_markdown(ils_def.markdown_content)


@transaction.atomic
def save_direct_response(user, course_key, ils_def, raw_responses):
    """El estudiante envió la encuesta en este curso."""
    response, _ = ILSUserResponse.objects.get_or_create(
        user=user, course_id=course_key, ils_definition=ils_def,
    )
    response.set_raw_responses(raw_responses)
    response.source = ILSUserResponse.SOURCE_DIRECT
    response.imported_from_course = None
    response.completed_at = timezone.now()
    response.save()
    return response


@transaction.atomic
def import_latest_response(user, course_key, ils_def, source_response):
    """Copia ``source_response`` (ILSUserResponse de otro curso) al curso actual."""
    raw = source_response.get_raw_responses()
    response, _ = ILSUserResponse.objects.get_or_create(
        user=user, course_id=course_key, ils_definition=ils_def,
    )
    response.set_raw_responses(raw)
    response.source = ILSUserResponse.SOURCE_IMPORTED
    response.imported_from_course = source_response.course_id
    response.completed_at = timezone.now()
    response.save()
    return response


def resolve_state(user, course_key, config=None):
    """
    Decide qué debe ver ``user`` en el curso ``course_key``.

    Aplica la política de reutilización, importando en silencio cuando
    corresponde (``ask`` con respuesta previa en otro curso, o ``auto_reuse``).
    """
    config = config or CourseILSConfig.get_for_course(course_key)
    ils_def = config.get_effective_definition()

    if ils_def is None:
        return ILSState(STATE_NO_INSTRUMENT, config)

    local = ILSUserResponse.for_course(user, course_key)
    stale = config.is_response_stale(local)
    policy = config.reuse_policy

    # 1. Respuesta local vigente -> resultado
    if local is not None and not stale:
        return ILSState(STATE_DASHBOARD, config, ils_def=ils_def, response=local)

    # 2. Se necesita una respuesta. ¿Se puede reutilizar de otro curso?
    can_reuse = policy in (CourseILSConfig.POLICY_ASK, CourseILSConfig.POLICY_AUTO_REUSE)
    # Con ``ask`` una re-toma explícita del equipo docente obliga a responder
    # de nuevo (no se re-importa); con ``auto_reuse`` sí se re-importa.
    if policy == CourseILSConfig.POLICY_ASK and stale and local is not None:
        can_reuse = False

    if can_reuse:
        external = ILSUserResponse.latest_for_user(user, exclude_course=course_key)
        if external is not None:
            response = import_latest_response(user, course_key, ils_def, external)
            return ILSState(STATE_DASHBOARD, config, ils_def=ils_def, response=response)

    # 3. No hay nada que reutilizar -> encuesta en blanco
    if policy == CourseILSConfig.POLICY_REQUIRE_NEW:
        reason = REASON_REQUIRE_NEW
    elif stale and local is not None:
        reason = REASON_RETAKE_REQUESTED
    else:
        reason = REASON_FIRST_TIME
    return ILSState(
        STATE_SURVEY, config, ils_def=ils_def, reason=reason,
        parsed_survey=_parsed(ils_def),
    )


def clean_answers(parsed_survey, answers):
    """Deja en ``answers`` sólo las claves que corresponden a preguntas de ``parsed_survey``."""
    if isinstance(answers, str):
        try:
            answers = json.loads(answers)
        except (ValueError, TypeError):
            answers = {}
    answers = answers or {}

    valid_ids = set()
    for section in (parsed_survey or {}).get('sections', []):
        for question in section.get('questions', []):
            if question.get('type') == 'likert_matrix':
                for row in question.get('rows', []):
                    valid_ids.add(row.get('id'))
            else:
                valid_ids.add(question.get('id'))
                valid_ids.add('{}_other'.format(question.get('id')))

    return {k: v for k, v in answers.items() if k in valid_ids}
