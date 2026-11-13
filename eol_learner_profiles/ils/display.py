# -*- coding: utf-8 -*-
"""
Partes ILS para mostrar en una página: encuesta para el estudiante y, para el
equipo docente, la configuración ILS del curso.

Para mostrar el ILS en una página (la pestaña o el dashboard), en la vista::

    context['ils_fragment'] = render_ils_fragment(request, course, course_key, is_staff)

y en el template ``${ ils_fragment | n }``. Si se necesitan las partes por
separado: ``render_ils(ils_context(...))`` -> ``{'assets', 'config_button',
'survey', 'config_modal'}``.
"""

import six
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.urls import reverse

from . import state
from .models import CourseILSConfig, ILSDefinition, ILSUserResponse
from .parser import parse_ils_markdown


def _staff_context(course_key, config):
    enrolled = User.objects.filter(
        courseenrollment__course_id=course_key,
        courseenrollment__is_active=1,
    ).count()
    current = ILSUserResponse.objects.filter(course_id=course_key)
    if config.retake_requested_at:
        current = current.filter(completed_at__gte=config.retake_requested_at)
    return {
        'staff_config': config,
        'staff_definitions': ILSDefinition.objects.all().order_by('-version'),
        'staff_policy_choices': CourseILSConfig.REUSE_POLICY_CHOICES,
        'staff_enrolled_count': enrolled,
        'staff_responded_count': current.values('user').distinct().count(),
        'ils_editor_url': reverse('ils_editor_list'),
    }


def ils_context(request, course, course_key, is_staff, page_url=None):
    """
    Contexto que necesitan las partes ILS (ver ``render_ils``).

    Pensado para cualquier página que muestre el ILS (esta pestaña o el
    dashboard): ``context.update(ils_context(...))``. ``page_url`` es la página
    que contiene la encuesta: allí vuelven "Responder de nuevo", "Cancelar" y
    los formularios tras enviarse. Por defecto, esta pestaña.
    """
    course_id_str = six.text_type(course_key)
    config = CourseILSConfig.get_for_course(course_key)
    ils_state = state.resolve_state(request.user, course_key, config)

    # Encuesta a renderizar (formulario o revisión de sólo lectura)
    parsed_survey = ils_state.parsed_survey
    if parsed_survey is None and ils_state.ils_def is not None:
        parsed_survey = parse_ils_markdown(ils_state.ils_def.markdown_content)

    existing_response = ILSUserResponse.for_course(request.user, course_key)
    survey_completed = existing_response is not None
    no_instrument = ils_state.name == state.STATE_NO_INSTRUMENT
    # Formulario editable: cuando el estado lo exige o se pidió responder de nuevo (?retake=1).
    render_survey_form = ils_state.show_survey or request.GET.get('retake') == '1'

    context = {
        'course': course,
        'csrf_token': get_token(request),
        'page_url': page_url or reverse('learner_profile_view', kwargs={'course_id': course_id_str}),
        'submit_url': reverse('learner_profile_submit', kwargs={'course_id': course_id_str}),
        'staff_url': reverse('learner_profile_staff', kwargs={'course_id': course_id_str}),

        'is_staff': is_staff,
        'config_open': is_staff and request.GET.get('config') == '1',
        'survey_reason': ils_state.reason,

        'ils_def': ils_state.ils_def,
        'parsed_survey': parsed_survey,
        'no_instrument': no_instrument,

        'survey_completed': survey_completed,
        'existing_answers': existing_response.get_raw_responses() if existing_response else {},
        'render_survey_form': render_survey_form,
        # La tarjeta arranca colapsada si ya fue respondida y no se pide re-tomar.
        'survey_collapsed': survey_completed and not render_survey_form and not no_instrument,
        'response_source': getattr(existing_response, 'source', None),
    }
    if is_staff:
        context.update(_staff_context(course_key, config))
    return context


# Templates en ``templates/eol_learner_profiles/ils/<parte>.html``.
ILS_PARTS = ('assets', 'config_button', 'survey', 'config_modal')


def render_ils(context):
    """
    ``{parte: html}`` con cada parte ILS ya renderizada, para insertarla en
    cualquier template como ``${ils['survey']}``. Cada parte se renderiza
    como template propio (no con ``<%namespace>``/``<%include>`` entre
    templates, que el lookup Mako de Open edX no resuelve para esta app).
    """
    return {
        part: render_to_string('eol_learner_profiles/ils/{}.html'.format(part), context)
        for part in ILS_PARTS
    }


def render_ils_fragment(request, course, course_key, is_staff, page_url=None):
    """HTML de la sección ILS completa (``ils/section.html``), para ``${ ils_fragment | n }``."""
    context = ils_context(request, course, course_key, is_staff, page_url)
    return render_to_string('eol_learner_profiles/ils/section.html', {'ils': render_ils(context)})
