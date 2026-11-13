# -*- coding: utf-8 -*-
"""Django descubre los modelos de la app vía este módulo; viven en cada carpeta."""

from .ils.models import CourseILSConfig, ILSDefinition, ILSUserResponse  # noqa: F401
from .recommendations.models import Recommendation, RecommendationCase  # noqa: F401
