# -*- coding: utf-8 -*-
"""Pruebas de las recomendaciones para los gráficos del dashboard."""

import itertools
from unittest import mock

from django.contrib.auth.models import User
from django.http import Http404
from django.test import RequestFactory, TestCase
from opaque_keys.edx.keys import CourseKey

from .constants import GENERIC, GRAPH_METRICS, HIGH, LOW, MID
from .models import Recommendation, RecommendationCase
from ..dummy_data import load_dummy_metrics
from .debug import RecommendationDebugView, debug_context
from .case import case_from_ils, select_case
from .service import get_recommendations, metric_level, percentile, select_by_metrics

COURSE = CourseKey.from_string('course-v1:eol+REC+2024')
LEVELS = (LOW, MID, HIGH)
COHORT = list(range(1, 101))   # P33 = 33.67, P66 = 66.34


def _load_generic():
    """Caso genérico y un texto por gráfico y combinación (idempotente: con o sin migraciones)."""
    case, _ = RecommendationCase.objects.get_or_create(key=GENERIC, defaults={'name': 'Genérico'})
    for graph in GRAPH_METRICS:
        for first, second in itertools.product(LEVELS, LEVELS):
            Recommendation.objects.update_or_create(
                case=case, graph=graph, first_level=first, second_level=second,
                defaults={'text': 'Hola, {name}: %s %s/%s' % (graph, first, second)},
            )


def level(value, cohort):
    return metric_level(value, cohort)['level']


class LevelTests(TestCase):
    def test_percentile_interpolates_like_spreadsheet(self):
        self.assertEqual(percentile([1, 2, 3, 4], 0.5), 2.5)
        self.assertEqual(percentile([7], 0.33), 7)

    def test_level_against_cohort(self):
        self.assertEqual(level(10, COHORT), LOW)
        self.assertEqual(level(50, COHORT), MID)
        self.assertEqual(level(90, COHORT), HIGH)

    def test_boundaries_are_mid(self):
        cohort = [0, 3, 6, 9]          # P33 = 2.97, P66 = 5.94
        self.assertEqual(level(percentile(cohort, 0.33), cohort), MID)
        self.assertEqual(level(percentile(cohort, 0.66), cohort), MID)

    def test_missing_data_has_no_level(self):
        self.assertIsNone(level(None, COHORT))
        self.assertIsNone(level(5, []))
        self.assertEqual(level(5, [None, 1, 9]), MID)


class GetRecommendationsTests(TestCase):
    def setUp(self):
        _load_generic()
        self.user = User.objects.create(username='stu')
        self.cohort = {m: COHORT for pair in GRAPH_METRICS.values() for m in pair}

    def _text(self, graph, first, second, case=GENERIC):
        return Recommendation.objects.get(
            case__key=case, graph=graph, first_level=first, second_level=second,
        ).text

    def test_one_text_per_graph_from_its_two_metrics(self):
        student = {'V1': 10, 'V2': 50, 'E1': 90, 'E2': 10, 'C1': 50, 'C2': 50}
        out = get_recommendations(self.user, COURSE, student, self.cohort)
        self.assertEqual(out, {
            'videos': self._text('videos', LOW, MID),
            'evaluations': self._text('evaluations', HIGH, LOW),
            'consistency': self._text('consistency', MID, MID),
        })

    def test_every_combination_yields_a_text(self):
        values = {LOW: 10, MID: 50, HIGH: 90}
        for first, second in itertools.product(LEVELS, LEVELS):
            student = {}
            for m1, m2 in GRAPH_METRICS.values():
                student.update({m1: values[first], m2: values[second]})
            out = get_recommendations(self.user, COURSE, student, self.cohort)
            for graph in GRAPH_METRICS:
                self.assertEqual(out[graph], self._text(graph, first, second))

    def test_renaming_a_case_does_not_change_the_lookup(self):
        RecommendationCase.objects.filter(key=GENERIC).update(name='Caso base')
        out = get_recommendations(self.user, COURSE, {'V1': 10, 'V2': 50}, self.cohort)
        self.assertEqual(out['videos'], self._text('videos', LOW, MID))

    def test_graph_without_its_metrics_is_none(self):
        out = get_recommendations(self.user, COURSE, {'V1': 10, 'V2': 10}, self.cohort)
        self.assertIsNotNone(out['videos'])
        self.assertIsNone(out['evaluations'])
        self.assertIsNone(out['consistency'])

    def test_ils_picks_the_case_then_metrics_pick_the_text(self):
        self.assertEqual(case_from_ils(None), GENERIC)
        self.assertEqual(select_case(self.user, COURSE), GENERIC)
        other, _ = RecommendationCase.objects.get_or_create(key='otro', defaults={'name': 'Otro'})
        Recommendation.objects.create(case=other, graph='videos',
                                      first_level=LOW, second_level=MID, text='texto de otro caso')
        student = {'V1': 10, 'V2': 50}
        self.assertEqual(select_by_metrics('otro', student, self.cohort)['videos'], 'texto de otro caso')
        self.assertEqual(get_recommendations(self.user, COURSE, student, self.cohort)['videos'], self._text('videos', LOW, MID))


class MetricLevelTests(TestCase):
    def test_reports_value_thresholds_and_level(self):
        out = metric_level(10, COHORT)
        self.assertEqual(out['level'], LOW)
        self.assertAlmostEqual(out['p33'], percentile(COHORT, 0.33))
        self.assertAlmostEqual(out['p66'], percentile(COHORT, 0.66))
        self.assertEqual(metric_level(None, COHORT)['level'], None)


class DebugTests(TestCase):
    def setUp(self):
        _load_generic()
        self.data = load_dummy_metrics()

    def test_dummy_file_has_every_metric_for_every_student(self):
        metrics = {m for pair in GRAPH_METRICS.values() for m in pair}
        self.assertGreater(len(self.data['students']), 3)
        for row in self.data['students']:
            self.assertTrue(row['username'])
            self.assertTrue(metrics <= set(row), row['username'])

    def test_selects_requested_student_then_current_user_then_first(self):
        names = [row['username'] for row in self.data['students']]
        user = User.objects.create(username=names[2])
        self.assertEqual(debug_context(user, COURSE, self.data, names[4])['selected_username'], names[4])
        self.assertEqual(debug_context(user, COURSE, self.data, 'nadie')['selected_username'], names[2])
        other = User.objects.create(username='fuera_del_mock')
        self.assertEqual(debug_context(other, COURSE, self.data)['selected_username'], names[0])

    def test_shows_the_text_chosen_by_get_recommendations(self):
        user = User.objects.create(username='staff')
        ctx = debug_context(user, COURSE, self.data)
        self.assertEqual([g['key'] for g in ctx['graphs']], list(GRAPH_METRICS))
        for graph in ctx['graphs']:
            levels = [m['level'] for m in graph['metrics']]
            self.assertNotIn(None, levels)
            self.assertEqual(graph['text'], self._text_for(graph['key'], *levels))

    def _text_for(self, graph, first, second):
        return Recommendation.objects.get(case__key=GENERIC, graph=graph, first_level=first, second_level=second).text


class DebugViewTests(TestCase):
    """``courses/<course_id>/learner_profile/recomendation_debug``: sólo staff."""

    def setUp(self):
        _load_generic()
        self.request = RequestFactory().get('/', {'debug_student': 'nadie'})
        self.request.user = User.objects.create(username='staff')

    def _get(self, is_staff):
        with mock.patch('eol_learner_profiles.recommendations.debug.load_course',
                        return_value=(COURSE, object(), is_staff)), \
                mock.patch('eol_learner_profiles.recommendations.debug.render_to_string',
                           side_effect=lambda name, ctx: '{}|{}'.format(name, ctx['case'])) as render:
            return RecommendationDebugView.as_view()(self.request, course_id=str(COURSE)), render

    def test_staff_sees_the_page(self):
        response, render = self._get(is_staff=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(render.call_args[0][0], 'eol_learner_profiles/recommendations/debug.html')

    def test_students_get_404(self):
        with self.assertRaises(Http404):
            self._get(is_staff=False)
