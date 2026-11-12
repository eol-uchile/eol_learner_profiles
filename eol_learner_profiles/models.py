# -*- coding: utf-8 -*-
from django.db import models
from .ils.models import CourseILSConfig, ILSDefinition, ILSUserResponse
from .recommendations.models import Recommendation, RecommendationCase

class DataFile(models.Model):
    """Archivos de datos temporales subidos desde el admin. Por cada key se usa el último subido."""
    UID_MAPPING = 'uid_mapping'
    EVALUACIONES = 'evaluaciones'
    METRICAS = 'metricas'
    DASHBOARD = 'dashboard'
    KEY_CHOICES = (
        (UID_MAPPING, 'Mapeo user_id staging -> prod (CSV)'),
        (EVALUACIONES, 'Evaluaciones mock (JSON)'),
        (METRICAS, 'Métricas mock (JSON)'),
        (DASHBOARD, 'Dashboard mock (JSON)'),
    )

    key = models.CharField(max_length=50, choices=KEY_CHOICES)
    file = models.FileField(upload_to='eol_learner_profiles/data_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-uploaded_at',)
        verbose_name = 'archivo de datos'
        verbose_name_plural = 'archivos de datos'

    def __str__(self):
        return '{}: {}'.format(self.key, self.file.name)
