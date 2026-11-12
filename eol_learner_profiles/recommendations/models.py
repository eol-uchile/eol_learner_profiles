# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ValidationError
from jsonfield.fields import JSONField
from .constants import GRAPH_CHOICES, LEVEL_CHOICES


class RecommendationCase(models.Model):
    """
    Caso ILS (nivel 1, lo elige ``case.select_case``): agrupa un juego de textos. El código lo
    busca por ``key``; ``name`` se puede cambiar libremente.
    """
    key = models.SlugField(max_length=64, unique=True, help_text='Identificador estable, p.ej. "generic".')
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        app_label = 'eol_learner_profiles'
        ordering = ['key']
        verbose_name = 'Caso de recomendación'
        verbose_name_plural = 'Casos de recomendación'

    def __str__(self):
        return self.name


class Recommendation(models.Model):
    """
    Texto bajo un gráfico para un caso y una combinación de niveles de las
    dos métricas del gráfico (p.ej. Videos: V1 bajo, V2 medio).

    Si ``data`` tiene contenido se usa en vez de ``text``. Estructura::

        {"introduccion": "...", "subtitulo": "...", "pasos": ["...", "..."], "cierre": "..."}

    Todas las claves son opcionales; cualquier string puede usar {name}.
    """
    case = models.ForeignKey(RecommendationCase, on_delete=models.PROTECT, related_name='recommendations')
    graph = models.CharField(max_length=32, choices=GRAPH_CHOICES, help_text='Gráfico del dashboard.')
    first_level = models.CharField(max_length=8, choices=LEVEL_CHOICES, help_text='Nivel de la 1ª métrica del gráfico.')
    second_level = models.CharField(max_length=8, choices=LEVEL_CHOICES, help_text='Nivel de la 2ª métrica del gráfico.')
    text = models.TextField(blank=True, help_text='Puede usar {name}; lo rellena el dashboard. Se usa si "data" está vacío.')
    data = JSONField(
        null=True, blank=True,
        help_text='Opcional; si se completa reemplaza a "text". '
                  'Ej: {"introduccion": "Hola {name}", "subtitulo": "...", "pasos": ["...", "..."], "cierre": "..."}',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'eol_learner_profiles'
        unique_together = ('case', 'graph', 'first_level', 'second_level')
        ordering = ['case', 'graph', 'first_level', 'second_level']
        verbose_name = 'Recomendación'
        verbose_name_plural = 'Recomendaciones'

    def __str__(self):
        return '{} / {} / {}-{}'.format(self.case, self.graph, self.first_level, self.second_level)

    def clean(self):
        if self.data:
            if not isinstance(self.data, dict):
                raise ValidationError({'data': 'Debe ser un objeto JSON ({...}).'})
            if 'pasos' in self.data and not isinstance(self.data['pasos'], list):
                raise ValidationError({'data': '"pasos" debe ser una lista.'})
        elif not (self.text or '').strip():
            raise ValidationError('Complete "text" o "data".')

    @property
    def content(self):
        """``data`` si tiene contenido; si no, ``text``."""
        return self.data or self.text or None
