# -*- coding: utf-8 -*-
"""Pruebas del instrumento ILS: parser, limpieza de respuestas y máquina de estados."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from opaque_keys.edx.keys import CourseKey

from . import state
from .models import CourseILSConfig, ILSDefinition, ILSUserResponse
from .parser import parse_ils_markdown

SURVEY_MD = """# Encuesta Test

## Sección 1: Datos

Indique su género [tag:gender]
( ) Femenino
( ) Masculino
( ) Otro (especifique): [has_other_text:true]

## Parte A

| Enunciado | 1 | 2 | 3 | 4 | 5 | Dimensión |
|---|:-:|:-:|:-:|:-:|:-:|---|
| It1 | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:construccion_conocimiento, item:1] |
| It6 | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:construccion_conocimiento, item:6] |
| It11 | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:construccion_conocimiento, item:11] |
| It31 | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_critico, item:31] |
| It35 | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_relacionar_estructurar, item:35] |
"""

COURSE_A = CourseKey.from_string("course-v1:eol+ILS+2024")
COURSE_B = CourseKey.from_string("course-v1:eol+OTRO+2024")


def _row_ids(parsed):
    return [
        r['id'] for s in parsed['sections'] for q in s['questions']
        if q['type'] == 'likert_matrix' for r in q['rows']
    ]


def _gender_qid(parsed):
    for section in parsed['sections']:
        for q in section['questions']:
            if (q.get('tags') or {}).get('tag') == 'gender':
                return q['id']
    return None


class ParserTests(TestCase):
    def test_bracketed_dimension_tag_is_parsed(self):
        parsed = parse_ils_markdown(SURVEY_MD)
        rows = [
            r for s in parsed['sections'] for q in s['questions']
            if q['type'] == 'likert_matrix' for r in q['rows']
        ]
        self.assertEqual(rows[0]['tags'].get('dim'), 'construccion_conocimiento')
        self.assertEqual(rows[0]['tags'].get('item'), '1')

    def test_demographic_question_keeps_tag(self):
        self.assertIsNotNone(_gender_qid(parse_ils_markdown(SURVEY_MD)))

    def test_no_page_break_is_single_page(self):
        parsed = parse_ils_markdown(SURVEY_MD)
        self.assertEqual(parsed['page_count'], 1)
        self.assertEqual(len(parsed['pages']), 1)

    def test_page_break_splits_into_pages(self):
        md = (
            "## S1\n\nP1? [tag:gender]\n( ) a\n( ) b\n\n"
            "[[page]]\n\n"
            "## S2\n\n"
            "| Enunciado | 1 | 2 | 3 | 4 | 5 | Dimensión |\n"
            "|---|---|---|---|---|---|---|\n"
            "| Af | | | | | | dim:construccion_conocimiento, item:1 |\n"
            "\n[[ Page ]]\n\n"
            "P3?\n( ) sí\n( ) no\n"
        )
        parsed = parse_ils_markdown(md)
        self.assertEqual(parsed['page_count'], 3)
        kinds = [[b['kind'] for b in pg['blocks']] for pg in parsed['pages']]
        self.assertEqual(kinds, [
            ['section', 'question'],
            ['section', 'question'],
            ['section', 'question'],   # S2 continúa -> encabezado repetido
        ])
        self.assertTrue(parsed['pages'][2]['blocks'][0]['continued'])
        # el puntaje recorre todas las preguntas sin importar la página
        self.assertEqual(len([q for s in parsed['sections'] for q in s['questions']]), 3)

    def test_empty_page_between_breaks_is_dropped(self):
        parsed = parse_ils_markdown("## S\n\n[[page]]\n\n[[page]]\n\nQ?\n( ) a\n( ) b\n")
        self.assertEqual(parsed['page_count'], 1)


class CleanAnswersTests(TestCase):
    def test_keeps_only_known_question_ids(self):
        parsed = parse_ils_markdown(SURVEY_MD)
        rows = _row_ids(parsed)
        qid = _gender_qid(parsed)
        cleaned = state.clean_answers(parsed, {
            rows[0]: '4', qid: 'Femenino', '{}_other'.format(qid): 'x', 'bogus': '1',
        })
        self.assertEqual(set(cleaned), {rows[0], qid, '{}_other'.format(qid)})

    def test_accepts_json_string(self):
        parsed = parse_ils_markdown(SURVEY_MD)
        rows = _row_ids(parsed)
        self.assertEqual(state.clean_answers(parsed, '{"%s": "3"}' % rows[0]), {rows[0]: '3'})


class ResolveStateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='stu', email='stu@example.com')
        self.ils = ILSDefinition.objects.create(
            name='Patrones', version=1, markdown_content=SURVEY_MD, is_active=True,
        )
        self.rows = _row_ids(parse_ils_markdown(SURVEY_MD))

    def _answers(self, values):
        return dict(zip(self.rows, [str(v) for v in values]))

    def _config(self, course=COURSE_A, **kw):
        cfg = CourseILSConfig.get_for_course(course)
        for k, v in kw.items():
            setattr(cfg, k, v)
        cfg.save()
        return cfg

    def test_first_visit_shows_survey(self):
        result = state.resolve_state(self.user, COURSE_A, self._config())
        self.assertEqual(result.name, state.STATE_SURVEY)
        self.assertEqual(result.reason, state.REASON_FIRST_TIME)

    def test_after_submit_shows_dashboard_and_keeps_raw_answers(self):
        cfg = self._config()
        answers = self._answers([5, 5, 5, 4, 4])
        state.save_direct_response(self.user, COURSE_A, self.ils, answers)
        result = state.resolve_state(self.user, COURSE_A, cfg)
        self.assertEqual(result.name, state.STATE_DASHBOARD)
        self.assertEqual(result.response.get_raw_responses(), answers)

    def test_no_instrument(self):
        self.ils.is_active = False
        self.ils.save()
        result = state.resolve_state(self.user, COURSE_B, self._config(course=COURSE_B))
        self.assertEqual(result.name, state.STATE_NO_INSTRUMENT)

    def test_retake_request_forces_survey(self):
        cfg = self._config()
        resp = state.save_direct_response(
            self.user, COURSE_A, self.ils, self._answers([3, 3, 3, 3, 3]),
        )
        resp.completed_at = timezone.now() - timedelta(days=2)
        resp.save()
        cfg.retake_requested_at = timezone.now()
        cfg.save()
        result = state.resolve_state(self.user, COURSE_A, cfg)
        self.assertEqual(result.name, state.STATE_SURVEY)
        self.assertEqual(result.reason, state.REASON_RETAKE_REQUESTED)

    def test_ask_policy_imports_from_other_course_silently(self):
        state.save_direct_response(self.user, COURSE_B, self.ils, self._answers([5, 5, 5, 5, 5]))
        cfg = self._config(reuse_policy=CourseILSConfig.POLICY_ASK)
        result = state.resolve_state(self.user, COURSE_A, cfg)
        self.assertEqual(result.name, state.STATE_DASHBOARD)
        self.assertEqual(result.response.source, ILSUserResponse.SOURCE_IMPORTED)
        self.assertEqual(result.response.imported_from_course, COURSE_B)
        self.assertEqual(result.response.get_raw_responses(), self._answers([5, 5, 5, 5, 5]))

    def test_require_new_ignores_other_course(self):
        state.save_direct_response(self.user, COURSE_B, self.ils, self._answers([5, 5, 5, 5, 5]))
        cfg = self._config(reuse_policy=CourseILSConfig.POLICY_REQUIRE_NEW)
        result = state.resolve_state(self.user, COURSE_A, cfg)
        self.assertEqual(result.name, state.STATE_SURVEY)
        self.assertEqual(result.reason, state.REASON_REQUIRE_NEW)

    def test_auto_reuse_reimports_even_after_retake_request(self):
        state.save_direct_response(self.user, COURSE_B, self.ils, self._answers([4, 4, 4, 4, 4]))
        resp = state.save_direct_response(
            self.user, COURSE_A, self.ils, self._answers([1, 1, 1, 1, 1]),
        )
        resp.completed_at = timezone.now() - timedelta(days=2)
        resp.save()
        cfg = self._config(
            reuse_policy=CourseILSConfig.POLICY_AUTO_REUSE,
            retake_requested_at=timezone.now(),
        )
        result = state.resolve_state(self.user, COURSE_A, cfg)
        self.assertEqual(result.name, state.STATE_DASHBOARD)
        self.assertEqual(result.response.source, ILSUserResponse.SOURCE_IMPORTED)


class RedirectAfterPostTests(TestCase):
    """Tras un POST, se vuelve a la página que contiene la encuesta (``next``), sólo si es del mismo sitio."""

    def _redirect(self, next_url=None, query=None):
        from django.test import RequestFactory
        from .views import _json_or_redirect
        data = {} if next_url is None else {'next': next_url}
        return _json_or_redirect(RequestFactory().post('/x', data), str(COURSE_A), query=query)['Location']

    def test_follows_same_site_next(self):
        self.assertEqual(self._redirect('/courses/x/dashboard'), '/courses/x/dashboard')
        self.assertEqual(self._redirect('/courses/x/dashboard?tab=2', query='config=1'),
                         '/courses/x/dashboard?tab=2&config=1')

    def test_unsafe_or_missing_next_falls_back_to_the_tab(self):
        from django.urls import reverse
        tab = reverse('learner_profile_view', kwargs={'course_id': str(COURSE_A)})
        for bad in (None, '', 'https://evil.example', '//evil.example', '/\\evil.example', 'dashboard'):
            self.assertEqual(self._redirect(bad), tab, bad)
        self.assertEqual(self._redirect(query='config=1'), tab + '?config=1')
