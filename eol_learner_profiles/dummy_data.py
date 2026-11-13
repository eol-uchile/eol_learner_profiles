# -*- coding: utf-8 -*-
"""Datos de prueba de ``data/`` (compartidos por recomendaciones, dashboard, etc.)."""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


def load_json(filename):
    """Contenido de ``data/<filename>``."""
    with open(os.path.join(DATA_DIR, filename), encoding='utf-8') as fh:
        return json.load(fh)


def load_dummy_metrics():
    """Mock de la respuesta de la API de métricas: ``{'units': {...}, 'students': [...]}``."""
    return load_json('dummy_metrics.json')
