# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.conf import settings
from .views import (
    EolLearnerProfileFragmentView,
)

urlpatterns = (
    # Recomendation Dashboard Tab for student
    url(
        r'courses/{}/learner_profile$'.format(
            settings.COURSE_ID_PATTERN,
        ),
        EolLearnerProfileFragmentView.as_view(),
        name='learner_profile_view',
    ),
)
