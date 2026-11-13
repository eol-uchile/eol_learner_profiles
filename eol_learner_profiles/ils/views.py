# -*- coding: utf-8 -*-
"""
Vistas ILS: editor global de instrumentos (+ preview) y los POST de la
pestaña (envío de la encuesta y configuración ILS del curso).
"""

import json

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import View

from ..courseware import load_course
from . import state
from .models import CourseILSConfig, ILSDefinition
from .parser import parse_ils_markdown

_DEFAULT_MARKDOWN = (
    "# Encuesta ILS v1\n\n## Sección 1: Datos\n\n"
    "¿Pregunta de prueba?\n( ) Opción A\n( ) Opción B\n"
)


# ---------------------------------------------------------------------------
# Editor global de instrumentos ILS
# ---------------------------------------------------------------------------

def check_ils_editor_permission(user):
    """Staff global o permiso de modelo sobre ILSDefinition."""
    if not user.is_authenticated:
        return False
    return user.is_staff or user.has_perm('eol_learner_profiles.change_ilsdefinition')


def _render_mako_page(template_name, context):
    """
    Página completa con cabecera/pie de Open edX: los templates heredan de
    ``/main.html`` y el ``MakoMiddleware`` aporta el contexto de request.
    """
    return HttpResponse(render_to_string(template_name, context))


def _next_version():
    latest = ILSDefinition.objects.order_by('-version').first()
    return (latest.version + 1) if latest else 1


class ILSEditorListView(View):
    """Lista todas las versiones de instrumentos ILS."""

    def get(self, request):
        if not check_ils_editor_permission(request.user):
            raise PermissionDenied("No tiene permisos para acceder al editor de ILS.")

        return _render_mako_page('eol_learner_profiles/ils/editor_list.html', {
            'definitions': ILSDefinition.objects.all().order_by('-version'),
            'create_url': reverse('ils_editor_create'),
        })


class ILSEditorDetailView(View):
    """Editor split-screen (Markdown / DSL + Live Preview)."""

    def get(self, request, pk=None):
        if not check_ils_editor_permission(request.user):
            raise PermissionDenied("No tiene permisos para acceder al editor de ILS.")

        ils_def = get_object_or_404(ILSDefinition, pk=pk) if pk else None
        return self._render(
            request, ils_def,
            markdown=ils_def.markdown_content if ils_def else _DEFAULT_MARKDOWN,
            error=request.GET.get('error'),
        )

    def post(self, request, pk=None):
        if not check_ils_editor_permission(request.user):
            raise PermissionDenied("No tiene permisos para guardar instrumentos ILS.")

        name = request.POST.get('name', 'Encuesta ILS').strip()
        markdown_content = request.POST.get('markdown_content', '').strip()
        is_active = request.POST.get('is_active') == 'true'

        if pk and request.POST.get('action', 'update') != 'new_version':
            ils_def = get_object_or_404(ILSDefinition, pk=pk)
            ils_def.name = name
            ils_def.markdown_content = markdown_content
            ils_def.is_active = is_active
            ils_def.save()
        else:
            ils_def = ILSDefinition.objects.create(
                name=name, version=_next_version(),
                markdown_content=markdown_content, is_active=is_active,
            )

        if is_active:
            ILSDefinition.objects.exclude(pk=ils_def.pk).update(is_active=False)

        return HttpResponseRedirect(reverse('ils_editor_list'))

    @staticmethod
    def _render(request, ils_def, markdown, error):
        return _render_mako_page('eol_learner_profiles/ils/editor_detail.html', {
            'ils_def': ils_def,
            'default_markdown': markdown,
            'error': error,
            'list_url': reverse('ils_editor_list'),
            'preview_url': reverse('ils_preview_api'),
            'csrf_token': get_token(request),
        })


class ILSPreviewApiView(View):
    """API AJAX: recibe Markdown y retorna la estructura parseada."""

    def post(self, request):
        if not check_ils_editor_permission(request.user):
            return JsonResponse({'error': 'Permission denied'}, status=403)

        parsed_data = parse_ils_markdown(request.POST.get('markdown_content', ''))
        return JsonResponse({'success': True, 'parsed': parsed_data})


# ---------------------------------------------------------------------------
# POST desde la pestaña del curso
# ---------------------------------------------------------------------------

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ILSSubmitView(View):
    """El estudiante envía sus respuestas de la encuesta ILS."""

    def post(self, request, course_id):
        try:
            course_key, _, _ = load_course(request, course_id)
        except Exception:
            raise Http404()

        ils_def = CourseILSConfig.get_for_course(course_key).get_effective_definition()
        if ils_def is None:
            return _json_or_redirect(request, course_id, ok=False,
                                     message='No hay instrumento ILS configurado.')

        parsed = parse_ils_markdown(ils_def.markdown_content)
        answers = state.clean_answers(parsed, _read_answers(request))
        state.save_direct_response(request.user, course_key, ils_def, answers)
        return _json_or_redirect(request, course_id, ok=True)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ILSStaffConfigView(View):
    """El equipo docente ajusta la configuración ILS del curso."""

    def post(self, request, course_id):
        try:
            course_key, _, is_staff = load_course(request, course_id)
        except Exception:
            raise Http404()
        if not is_staff:
            raise PermissionDenied()

        config = CourseILSConfig.get_for_course(course_key)
        action = request.POST.get('action', 'save')

        if action == 'request_retake':
            config.retake_requested_at = timezone.now()
        elif action == 'clear_retake':
            config.retake_requested_at = None
        else:  # save
            def_id = request.POST.get('ils_definition') or ''
            config.ils_definition = (
                ILSDefinition.objects.filter(pk=int(def_id)).first() if def_id.isdigit() else None
            )
            policy = request.POST.get('reuse_policy')
            if policy in {c[0] for c in CourseILSConfig.REUSE_POLICY_CHOICES}:
                config.reuse_policy = policy

        config.updated_by = request.user
        config.save()
        return _json_or_redirect(request, course_id, ok=True, query='config=1')


def _read_answers(request):
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body.decode('utf-8')).get('answers', {})
        except (ValueError, TypeError):
            return {}
    raw = request.POST.get('answers')
    if raw:
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return {}
    # form-encoded: cada campo es una respuesta
    answers = {}
    for key in request.POST:
        if key in ('csrfmiddlewaretoken', 'action', 'next'):
            continue
        values = request.POST.getlist(key)
        answers[key] = values if len(values) > 1 else values[0]
    return answers


def _json_or_redirect(request, course_id, ok=True, message='', query=None):
    wants_json = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in (request.content_type or '')
        or request.GET.get('format') == 'json'
    )
    if wants_json:
        return JsonResponse(
            {'result': 'success' if ok else 'error', 'message': message},
            status=200 if ok else 400,
        )
    # Vuelve a la página que contiene la encuesta (pestaña o dashboard). Sólo
    # rutas del mismo sitio, para que ``next`` no sirva de redirección abierta.
    url = request.POST.get('next') or ''
    if not url.startswith('/') or url.startswith('//') or '\\' in url:
        url = reverse('learner_profile_view', kwargs={'course_id': course_id})
    if query:
        url = '{}{}{}'.format(url, '&' if '?' in url else '?', query)
    return HttpResponseRedirect(url)
