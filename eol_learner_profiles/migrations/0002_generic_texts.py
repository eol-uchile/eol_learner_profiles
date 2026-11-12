# -*- coding: utf-8 -*-
"""
Contenido inicial: el caso "generic" (RecommendationCase) y sus 27 textos (planilla "Recomendaciones Optimizadas", perfil "5. Genérico", columna
Recomendacion_Optimizada), 3 gráficos x 9 combinaciones de niveles. Se carga una sola vez y desde ahí la fuente de verdad es la base de datos y
los textos se editan en el admin.
"""
from django.db import migrations

LOW, MID, HIGH = 'low', 'mid', 'high'

# (gráfico, nivel de la 1ª métrica, nivel de la 2ª métrica, texto)
INITIAL_TEXTS = [
    # ------------------------------------------------------------------
    # Evaluaciones: E1 = tiempo en la sub-sección de evaluación, E2 = calificación
    # ------------------------------------------------------------------
    ('evaluations', LOW, LOW, "text_ev_low_low"),
    ('evaluations', LOW, MID, "text_ev_low_mid"),
    ('evaluations', LOW, HIGH, "text_ev_low_high"),
    ('evaluations', MID, LOW, "text_ev_mid_low"),
    ('evaluations', MID, MID, "text_ev_mid_mid"),
    ('evaluations', MID, HIGH, "text_ev_mid_high"),
    ('evaluations', HIGH, HIGH, "text_ev_high_high"),
    ('evaluations', HIGH, LOW, "text_ev_mid_high"),
    ('evaluations', HIGH, MID, "text_ev_high_mid"),
    # ------------------------------------------------------------------
    # Constancia: C1 = unidades completadas por semana, C2 = tiempo conectado por semana
    # ------------------------------------------------------------------
    ('consistency', LOW, LOW, "text_con_low_low"),
    ('consistency', LOW, MID, "text_con_low_mid"),
    ('consistency', LOW, HIGH, "text_con_low_high"),
    ('consistency', MID, LOW, "text_con_mid_low"),
    ('consistency', MID, MID, "text_con_mid_mid"),
    ('consistency', MID, HIGH, "text_con_mid_high"),
    ('consistency', HIGH, HIGH, "text_con_high_high"),
    ('consistency', HIGH, LOW, "text_con_mid_high"),
    ('consistency', HIGH, MID, "text_con_high_mid"),
    # ------------------------------------------------------------------
    # Videos: V1 = % del video efectivamente visualizado, V2 = interacciones con el video
    # ------------------------------------------------------------------
    ('videos', LOW, LOW, "text_vid_low_low"),
    ('videos', LOW, MID, "text_vid_low_mid"),
    ('videos', LOW, HIGH, "text_vid_low_high"),
    ('videos', MID, LOW, "text_vid_mid_low"),
    ('videos', MID, MID, "text_vid_mid_mid"),
    ('videos', MID, HIGH, "text_vid_mid_high"),
    ('videos', HIGH, HIGH, "text_vid_high_high"),
    ('videos', HIGH, LOW, "text_vid_mid_high"),
    ('videos', HIGH, MID, "text_vid_high_mid"),
]

def load(apps, schema_editor):
    Case = apps.get_model('eol_learner_profiles', 'RecommendationCase')
    Recommendation = apps.get_model('eol_learner_profiles', 'Recommendation')
    case, _ = Case.objects.get_or_create(key='generic', defaults={'name': 'Genérico'})
    for graph, first_level, second_level, text in INITIAL_TEXTS:
        Recommendation.objects.get_or_create(case=case, graph=graph, first_level=first_level, second_level=second_level, defaults={'text': text})


def unload(apps, schema_editor):
    Case = apps.get_model('eol_learner_profiles', 'RecommendationCase')
    apps.get_model('eol_learner_profiles', 'Recommendation').objects.filter(case__key='generic').delete()
    Case.objects.filter(key='generic').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('eol_learner_profiles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load, unload),
    ]
