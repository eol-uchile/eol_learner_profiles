

import math

from .constants import GRAPH_METRICS, HIGH, LOW, MID
from .models import Recommendation
from .case import select_case

AGG_METRICS = {
    'V1': 'video_visualization_rate',
    'V2': 'video_interaction_time',
    'E1': 'problem_time',
    'E2': 'grades',
    'C1': 'navigation_by_week',
    'C2': 'completion_by_week',
}

def percentile(values, q):
    """Percentil ``q`` (0..1) con interpolación lineal (igual que Excel PERCENTIL.INC)."""
    data = sorted(values)
    pos = (len(data) - 1) * q
    lower, upper = math.floor(pos), math.ceil(pos)
    return data[lower] + (data[upper] - data[lower]) * (pos - lower)


def metric_level(value, cohort_values):
    """
    ``{'value', 'p33', 'p66', 'level'}`` de una métrica frente al grupo.
    ``cohort_values`` es la lista de valores del grupo o un dict
    ``{'p33', 'p66'}`` con los percentiles ya calculados.
    ``level`` es ``low`` (< P33) / ``mid`` (P33..P66) / ``high`` (> P66), o
    ``None`` si falta el valor o el grupo no tiene datos.
    """
    if isinstance(cohort_values, dict):
        p33, p66 = cohort_values.get('p33'), cohort_values.get('p66')
        if value is None or p33 is None or p66 is None:
            return {'value': value, 'p33': p33, 'p66': p66, 'level': None}
    else:
        cohort = [v for v in (cohort_values or []) if v is not None]
        if value is None or not cohort:
            return {'value': value, 'p33': None, 'p66': None, 'level': None}
        p33, p66 = percentile(cohort, 0.33), percentile(cohort, 0.66)
    lvl = LOW if value < p33 else HIGH if value > p66 else MID
    return {'value': value, 'p33': p33, 'p66': p66, 'level': lvl}


def select_by_metrics(case_key, student_metrics, cohort_metrics):
    """
    Nivel 2: ``{gráfico: contenido|None}`` del caso ``case_key`` según los
    niveles de las métricas. El contenido es el dict ``data`` de la
    recomendación si está completo, o su ``text`` (str) si no.
    """
    wanted = {}
    for graph, metrics in GRAPH_METRICS.items():
        levels = tuple(metric_level(student_metrics.get(m), cohort_metrics.get(m))['level'] for m in metrics)
        if None not in levels:
            wanted[graph] = levels

    contents = {
        row.graph: row.content
        for row in Recommendation.objects.filter(case__key=case_key, graph__in=wanted)
        if (row.first_level, row.second_level) == wanted[row.graph]
    }
    return {graph: contents.get(graph) for graph in GRAPH_METRICS}

def get_recommendations(user, course_key, student_metrics, cohort_metrics):
    """
    ``{gráfico: texto|None}`` para ``user`` en ``course_key``, una entrada por
    gráfico de ``GRAPH_METRICS``. El ILS del estudiante se busca internamente.
    """
    return select_by_metrics(select_case(user, course_key), student_metrics, cohort_metrics)

def get_recommendation(user, course_key, agg_data):
    try:
        student_metrics = {
            m: agg_data.get(p + '_user') if p else None
            for m, p in AGG_METRICS.items()
        }
        cohort_metrics = {
            m: {'p33': agg_data.get(p + '_p33'), 'p66': agg_data.get(p + '_p66')} if p else None
            for m, p in AGG_METRICS.items()
        }

        texts = get_recommendations(user, course_key, student_metrics, cohort_metrics)
        name = user.profile.name if hasattr(user, 'profile') else user.username

        def _fill(value):
            """Rellena {name} en strings, también dentro de listas y dicts."""
            if isinstance(value, str):
                try:
                    return value.format(name=name)
                except (KeyError, IndexError, ValueError):
                    return value
            if isinstance(value, list):
                return [_fill(v) for v in value]
            if isinstance(value, dict):
                return {k: _fill(v) for k, v in value.items()}
            return value

        def _wrap(content):
            if not content:
                return {}
            if isinstance(content, dict):
                return _fill(content)
            return {'introduccion': _fill(content)}

        rec_videos = _wrap(texts.get("videos"))
        rec_nav = _wrap(texts.get("consistency"))
        rec_eval = _wrap(texts.get("evaluations"))

        return rec_videos, rec_nav, rec_eval
    except Exception as e:
        logger.error("Error obteniendo recomendaciones: %s", str(e))
        return None
