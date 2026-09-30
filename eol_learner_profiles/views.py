# -*- coding: utf-8 -*-

# Python Standard Libraries
import json
import logging
import six

# Installed packages (via pip)
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic.base import View

# Edx dependencies
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.instructor import permissions
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from web_fragments.fragment import Fragment


logger = logging.getLogger(__name__)



class EolLearnerProfileFragmentView(EdxFragmentView):
    def render_to_fragment(self, request, course_id, **kwargs):
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, "load", course_key)

        staff_access = bool(has_access(request.user, 'staff', course))
        data_researcher_access = request.user.has_perm(permissions.CAN_RESEARCH, course_key)
        if not (staff_access or data_researcher_access):
            raise Http404()

        context = self.get_context(request, course_id, course, course_key)
        html = render_to_string('eol_learner_profiles/learner_profile_fragment.html', context)
        fragment = Fragment(html)
        return fragment

    def get_context(self, request, course_id, course, course_key):
        context = {
            "course": course,
            'page_url': reverse(
                'learner_profile_view',
                kwargs={'course_id': six.text_type(course_key)}
            ),
            "content": None,
            "max_unit": None
        }
        return context
