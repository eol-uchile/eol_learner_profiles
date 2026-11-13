# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import url

from .ils.views import (
    ILSEditorDetailView,
    ILSEditorListView,
    ILSPreviewApiView,
    ILSStaffConfigView,
    ILSSubmitView,
)
from .recommendations.debug import RecommendationDebugView
from .views import EolLearnerProfileFragmentView

urlpatterns = (
    # Editor y preview de instrumentos (staff global)
    url(r'^eol_learner_profiles/ils_editor/$', ILSEditorListView.as_view(), name='ils_editor_list'),
    url(r'^eol_learner_profiles/ils_editor/new/$', ILSEditorDetailView.as_view(), name='ils_editor_create'),
    url(r'^eol_learner_profiles/ils_editor/(?P<pk>\d+)/$', ILSEditorDetailView.as_view(), name='ils_editor_detail'),
    url(r'^eol_learner_profiles/ils_preview/$', ILSPreviewApiView.as_view(), name='ils_preview_api'),

    # Pestaña del curso
    url(r'courses/{}/learner_profile/submit$'.format(settings.COURSE_ID_PATTERN), ILSSubmitView.as_view(), name='learner_profile_submit'),
    url(r'courses/{}/learner_profile/staff$'.format(settings.COURSE_ID_PATTERN), ILSStaffConfigView.as_view(), name='learner_profile_staff'),
    url(r'courses/{}/learner_profile/recomendation_debug$'.format(settings.COURSE_ID_PATTERN), RecommendationDebugView.as_view(), name='learner_profile_recommendation_debug'),
    url(r'courses/{}/learner_profile$'.format(settings.COURSE_ID_PATTERN), EolLearnerProfileFragmentView.as_view(), name='learner_profile_view'),
)
