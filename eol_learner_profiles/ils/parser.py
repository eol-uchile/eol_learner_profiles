# -*- coding: utf-8 -*-
"""
Parser para encuestas ILS definidas en formato Markdown / DSL.

Soporta:
  - Selección Única: `( ) Opción`
  - Selección Múltiple: `[ ] Opción`
  - Opción Otro con texto libre: `[has_other_text:true]`
  - Grilla Likert: Tablas Markdown `| Enunciado | 1 | 2 | ... |`
  - Tags de contexto: `[tag:nombre]` (preguntas demográficas, no puntúan)
  - Tags de escala en filas Likert: `[dim:<subescala>, item:<n>]`
  - Salto de página: una línea que sólo contiene `[[page]]` (sin distinción de
    mayúsculas). Divide la encuesta en páginas para el estudiante.
"""

import re

_PAGE_BREAK_RE = re.compile(r'^\[\[\s*page\s*\]\]$', re.IGNORECASE)


def parse_ils_markdown(markdown_text):
    """
    Convierte el contenido Markdown/DSL de una encuesta ILS a una estructura
    de datos.

    Returns:
        dict: {
            'sections': [
                {'title': str, 'page': int, 'questions': [
                    {'id', 'type', 'text', 'tags', 'options', 'rows', 'scale',
                     'page': int}
                ]}
            ],
            'page_count': int,
            'pages': [
                {'number': int, 'blocks': [
                    {'kind': 'section', 'title': str, 'continued': bool} |
                    {'kind': 'question', 'q': <question dict>}
                ]}
            ],
        }
    """
    sections = []
    current_page = 1
    current_section = {'title': 'General', 'questions': [], 'page': current_page}
    lines = markdown_text.splitlines()

    q_counter = 1
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # Salto de página explícito
        if _PAGE_BREAK_RE.match(line):
            current_page += 1
            i += 1
            continue

        # Encabezado sección
        if line.startswith('## '):
            if current_section['questions']:
                sections.append(current_section)
            current_section = {
                'title': line[3:].strip(),
                'questions': [],
                'page': current_page,
            }
            i += 1
            continue

        # Detección de Tabla Likert
        if line.startswith('|') and '---|' in (lines[i + 1] if i + 1 < len(lines) else ''):
            headers = [h.strip() for h in line.split('|')[1:-1]]
            scale = [h for h in headers if h not in ('Enunciado', 'Tag / Dimensión', 'Dimensión')]

            matrix_rows = []
            i += 2  # Saltar header y separator
            while i < len(lines) and lines[i].strip().startswith('|'):
                row_cols = [c.strip() for c in lines[i].strip().split('|')[1:-1]]
                if row_cols:
                    statement = row_cols[0]
                    tag_str = row_cols[-1] if len(row_cols) > 2 else ''
                    # La celda de dimensión puede venir con o sin corchetes:
                    #   [dim:construccion_conocimiento, item:1]  ->  dim:..., item:1
                    _, row_tags = _extract_text_and_tags(tag_str)
                    if not row_tags:
                        row_tags = _parse_tags(tag_str)
                    matrix_rows.append({
                        'id': 'q_likert_{}'.format(q_counter),
                        'statement': statement,
                        'tags': row_tags
                    })
                    q_counter += 1
                i += 1

            current_section['questions'].append({
                'id': 'matrix_{}'.format(len(current_section['questions']) + 1),
                'type': 'likert_matrix',
                'scale': scale,
                'rows': matrix_rows,
                'page': current_page,
            })
            continue

        # Detección de Pregunta Normal (Radio / Checkbox)
        if not line.startswith('(') and not line.startswith('[') and not line.startswith('|'):
            q_text, tags = _extract_text_and_tags(line)
            options = []
            q_type = 'radio'

            i += 1
            while i < len(lines):
                opt_line = lines[i].strip()
                if opt_line.startswith('( )') or opt_line.startswith('(x)'):
                    opt_text, opt_tags = _extract_text_and_tags(opt_line[3:].strip())
                    options.append({'text': opt_text, 'has_other_text': opt_tags.get('has_other_text', False)})
                    q_type = 'radio'
                    i += 1
                elif opt_line.startswith('[ ]') or opt_line.startswith('[x]'):
                    opt_text, opt_tags = _extract_text_and_tags(opt_line[3:].strip())
                    options.append({'text': opt_text, 'has_other_text': opt_tags.get('has_other_text', False)})
                    q_type = 'checkbox'
                    i += 1
                else:
                    break

            if options:
                current_section['questions'].append({
                    'id': 'q_{}'.format(q_counter),
                    'type': q_type,
                    'text': q_text,
                    'tags': tags,
                    'options': options,
                    'page': current_page,
                })
                q_counter += 1
            continue

        i += 1

    if current_section['questions']:
        sections.append(current_section)

    pages = _paginate(sections)
    return {
        'sections': sections,
        'page_count': len(pages),
        'pages': pages,
    }


def _paginate(sections):
    """
    Agrupa los bloques renderizables (encabezados de sección + preguntas) por
    página, en orden de documento. Si una sección se reparte en varias páginas,
    su encabezado se repite marcado como ``continued``.
    """
    buckets = {}
    order = []

    def _bucket(page):
        if page not in buckets:
            buckets[page] = []
            order.append(page)
        return buckets[page]

    for section in sections:
        header_pages = set()
        for q in section['questions']:
            page = q.get('page', 1)
            if page not in header_pages:
                _bucket(page).append({
                    'kind': 'section',
                    'title': section['title'],
                    'continued': bool(header_pages),
                })
                header_pages.add(page)
            _bucket(page).append({'kind': 'question', 'q': q})

    pages = [
        {'number': idx, 'blocks': buckets[p]}
        for idx, p in enumerate(sorted(order), start=1)
    ]
    if not pages:
        pages = [{'number': 1, 'blocks': []}]
    return pages


def _extract_text_and_tags(text):
    tags = {}
    tag_matches = re.findall(r'\[(.*?)\]', text)
    clean_text = re.sub(r'\[.*?\]', '', text).strip()
    for match in tag_matches:
        tags.update(_parse_tags(match))
    return clean_text, tags


def _parse_tags(tag_str):
    tags = {}
    parts = tag_str.split(',')
    for part in parts:
        if ':' in part:
            k, v = part.split(':', 1)
            k = k.strip()
            v = v.strip()
            if v.lower() == 'true':
                v = True
            elif v.lower() == 'false':
                v = False
            tags[k] = v
    return tags
