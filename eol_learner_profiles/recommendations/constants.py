# -*- coding: utf-8 -*-

# ``key`` del caso ILS que se usa mientras no se defina cómo usar el ILS (nivel 1).
GENERIC = 'generic'

# Nivel de una métrica respecto de su grupo (fijo: lo define la regla P33/P66).
LOW, MID, HIGH = 'low', 'mid', 'high'
LEVEL_CHOICES = [(LOW, '< P33'), (MID, 'P33 – P66'), (HIGH, '> P66')]

# Gráficos del dashboard y las dos métricas (claves en los datos) que deciden su texto.
GRAPH_METRICS = {
    'videos': ('V1', 'V2'),
    'evaluations': ('E1', 'E2'),
    'consistency': ('C1', 'C2'),
}
GRAPH_CHOICES = [('videos', 'Videos'), ('evaluations', 'Evaluaciones'), ('consistency', 'Constancia')]
