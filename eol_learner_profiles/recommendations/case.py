# -*- coding: utf-8 -*-
"""
Nivel 1 de la selección: estudiante en un curso -> caso de recomendaciones.

``select_case(user, course_key)`` busca la respuesta ILS del estudiante y
``case_from_ils`` decide el caso. Esa es la única pieza que decidirá cómo se
usa el ILS: devuelve la ``key`` de un ``RecommendationCase`` (el conjunto de
textos a usar) y no guarda nada intermedio. Cuando se defina la regla, se
cambia ``case_from_ils`` (y se crean los casos/textos nuevos en el admin), sin
tocar modelos ni migraciones.
"""

from ..ils.models import ILSUserResponse
from .constants import GENERIC


def case_from_ils(ils_response):
    """
    ``RecommendationCase.key`` para la respuesta ILS ``ils_response``
    (``ILSUserResponse`` o ``None`` si no respondió).

    Por ahora no lee la respuesta: todos van al caso ``"generic"``.
    """
    return GENERIC


def select_case(user, course_key):
    """``RecommendationCase.key`` del estudiante ``user`` en ``course_key``, según su respuesta ILS."""
    return case_from_ils(ILSUserResponse.for_course(user, course_key))
