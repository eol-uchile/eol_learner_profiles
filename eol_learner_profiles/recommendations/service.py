# -*- coding: utf-8 -*-
"""
Recomendaciones para los gráficos del dashboard.

Uso desde la vista del dashboard::

    from eol_learner_profiles.recommendations.service import get_recommendations

    texts = get_recommendations(
        request.user, course_key,
        student_metrics={'V1': 0.42, 'V2': 3.0, 'E1': 18, 'E2': 5.1, 'C1': 2, 'C2': 95},
        cohort_metrics={'V1': [0.1, 0.42, 0.8, ...], 'V2': [...], ...},
    )
    # -> {'videos': '...', 'evaluations': '...', 'consistency': '...'}   (gráfico -> texto)

``student_metrics`` trae cada métrica ya agregada para el estudiante (p.ej. V1
= promedio de % visualizado sobre todos sus videos). ``cohort_metrics`` trae
esa misma métrica para todos los estudiantes del grupo (incluido él/ella); de
ahí salen P33 y P66.

Selección en dos niveles:
  1. ``case.select_case(user, course_key)``: con la respuesta ILS del
     estudiante en el curso elige el caso (``RecommendationCase``, hoy siempre
     ``"generic"``). La decisión vive en código y no guarda nada intermedio:
     cambiarla no requiere migraciones.
  2. ``select_by_metrics``: dentro de los textos del caso, en cada gráfico cada
     métrica se clasifica contra el grupo (``< P33`` low, ``P33..P66`` mid,
     ``> P66`` high) y el par de niveles elige el texto.

Casos (``RecommendationCase``) y textos (``Recommendation``) viven en la base
de datos y se editan en el admin; los gráficos y sus dos métricas están en
``constants.GRAPH_METRICS``. Un gráfico queda en ``None`` si
falta alguna de sus métricas o no hay texto. Los textos son plantillas
``str.format`` (``{name}``): los rellena quien los muestra.
"""

import math

from .constants import GRAPH_METRICS, HIGH, LOW, MID
from .models import Recommendation
from .case import select_case


def percentile(values, q):
    """Percentil ``q`` (0..1) con interpolación lineal (igual que Excel PERCENTIL.INC)."""
    data = sorted(values)
    pos = (len(data) - 1) * q
    lower, upper = math.floor(pos), math.ceil(pos)
    return data[lower] + (data[upper] - data[lower]) * (pos - lower)


def metric_level(value, cohort_values):
    """
    ``{'value', 'p33', 'p66', 'level'}`` de una métrica frente al grupo.
    ``level`` es ``low`` (< P33) / ``mid`` (P33..P66) / ``high`` (> P66), o
    ``None`` si falta el valor o el grupo no tiene datos.
    """
    cohort = [v for v in (cohort_values or []) if v is not None]
    if value is None or not cohort:
        return {'value': value, 'p33': None, 'p66': None, 'level': None}
    p33, p66 = percentile(cohort, 0.33), percentile(cohort, 0.66)
    lvl = LOW if value < p33 else HIGH if value > p66 else MID
    return {'value': value, 'p33': p33, 'p66': p66, 'level': lvl}


def select_by_metrics(case_key, student_metrics, cohort_metrics):
    """Nivel 2: ``{gráfico: texto|None}`` de los textos del caso ``case_key`` según los niveles de las métricas."""
    wanted = {}
    for graph, metrics in GRAPH_METRICS.items():
        levels = tuple(metric_level(student_metrics.get(m), cohort_metrics.get(m))['level'] for m in metrics)
        if None not in levels:
            wanted[graph] = levels

    texts = {
        row.graph: row.text
        for row in Recommendation.objects.filter(case__key=case_key, graph__in=wanted)
        if (row.first_level, row.second_level) == wanted[row.graph]
    }
    return {graph: texts.get(graph) for graph in GRAPH_METRICS}


def get_recommendations(user, course_key, student_metrics, cohort_metrics):
    """
    ``{gráfico: texto|None}`` para ``user`` en ``course_key``, una entrada por
    gráfico de ``GRAPH_METRICS``. El ILS del estudiante se busca internamente.
    """
    return select_by_metrics(select_case(user, course_key), student_metrics, cohort_metrics)
