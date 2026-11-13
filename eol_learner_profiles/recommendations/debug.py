# -*- coding: utf-8 -*-
"""
Página de debug (sólo staff) en ``courses/<course_id>/learner_profile/recomendation_debug``:
qué recomendación eligen los dos niveles de ``get_recommendations`` para un
estudiante, usando métricas de prueba de
``eol_learner_profiles/data/dummy_metrics.json`` en vez de la API.
"""

from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.views.generic.base import View

from ..courseware import load_course
from ..dummy_data import load_dummy_metrics
from .case import select_case
from .constants import GRAPH_CHOICES, GRAPH_METRICS
from .models import RecommendationCase
from .service import metric_level, select_by_metrics


def debug_context(user, course_key, data, username=None):
    """
    Elige un estudiante del mock (``username``, si no el usuario actual, si
    no el primero) y arma, por gráfico, los niveles de sus métricas frente al
    grupo y el texto elegido. El caso (nivel 1) sale de la respuesta ILS del
    usuario actual en el curso.
    """
    students = data['students']
    by_name = {row['username']: row for row in students}
    selected = by_name.get(username) or by_name.get(user.username) or students[0]
    cohort = {m: [row.get(m) for row in students] for metrics in GRAPH_METRICS.values() for m in metrics}

    case_key = select_case(user, course_key)
    texts = select_by_metrics(case_key, selected, cohort)
    graphs = []
    for graph, label in GRAPH_CHOICES:
        graphs.append({
            'key': graph,
            'label': label,
            'metrics': [
                dict(metric_level(selected.get(m), cohort[m]), name=m, unit=data.get('units', {}).get(m, ''))
                for m in GRAPH_METRICS[graph]
            ],
            'text': texts[graph],
        })
    case = RecommendationCase.objects.filter(key=case_key).first()
    return {
        'case': case.name if case else case_key,
        'usernames': [row['username'] for row in students],
        'selected_username': selected['username'],
        'cohort_size': len(students),
        'graphs': graphs,
    }


class RecommendationDebugView(View):
    """Página de debug; ``?debug_student=<username>`` elige el estudiante del mock. Sin staff -> 404."""

    def get(self, request, course_id):
        course_key, course, is_staff = load_course(request, course_id)
        if not is_staff:
            raise Http404()
        context = debug_context(request.user, course_key, load_dummy_metrics(), request.GET.get('debug_student'))
        context['course'] = course
        return HttpResponse(render_to_string('eol_learner_profiles/recommendations/debug.html', context))
