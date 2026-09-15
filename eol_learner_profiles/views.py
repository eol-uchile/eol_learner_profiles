# -*- coding: utf-8 -*-

# Python Standard Libraries
import json
import logging
import six

from urllib.parse import quote
import requests


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

def get_navigation_time(uid, course_id, group="week", start_date=None, end_date=None):

    base_url = settings.EOL_ANALYTICS_API_URL.rstrip("/")
    api_token = settings.EOL_ANALYTICS_API_TOKEN

    timeout = getattr(
        settings,
        "EOL_LEARNER_PROFILES_REQUEST_TIMEOUT",
        15
    )

    encoded_course_id = quote(six.text_type(course_id), safe="")

    url = "{}/metrics/navigation/time/{}/{}".format(
        base_url,
        uid,
        encoded_course_id
    )

    params = {
        "group": group,
    }

    if start_date:
        params["start_date"] = start_date

    if end_date:
        params["end_date"] = end_date

    headers = {
        "accept": "application/json",
        "X-API-KEY": api_token,
    }

    logger.info("=== EOL ANALYTICS REQUEST ===")
    logger.info("URL: %s", url)
    logger.info("PARAMS: %s", params)
    logger.info("UID: %s", uid)
    logger.info("COURSE: %s", course_id)

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException:
        logger.exception(
            "Error al obtener métricas de navegación para "
            "uid=%s, course_id=%s",
            uid,
            course_id,
        )
        return {
            "total_time": 0,
            "grouped_data": []
        }


class EolLearnerProfileFragmentView(EdxFragmentView):
    def render_to_fragment(self, request, course_id, **kwargs):
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, "load", course_key)

        staff_access = bool(has_access(request.user, 'staff', course))
        data_researcher_access = request.user.has_perm(permissions.CAN_RESEARCH, course_key)
        if not (staff_access or data_researcher_access):
            raise Http404()

        context = self.get_context(request, course_id, course, course_key)
        # html = render_to_string('eol_learner_profiles/learner_profile_fragment.html', context)
        html = render_to_string('eol_learner_profiles/learner_profile_fragment_v2.html', context)
        fragment = Fragment(html)
        return fragment

    def get_context(self, request, course_id, course, course_key):
        uid = request.user.id

        logger.info("EOL Analytics - username=%s uid=%s", request.user.username, uid)

        user_name = request.user.profile.name if hasattr(request.user, 'profile') else request.user.username

        # api test
        # navigation_time = get_navigation_time(
        # uid=uid,
        # course_id=course_id,
        # group="week",
        # start_date="2026-03-01",
        # end_date="2026-09-06",
        # )

        navigation_week = get_navigation_time(
            uid=uid,
            course_id=course_id,
            group="week",
            start_date="2026-03-01",
            end_date="2026-09-06",
        )

        navigation_chapter = get_navigation_time(
            uid=uid,
            course_id=course_id,
            group="chapter",
            start_date="2026-03-01",
            end_date="2026-09-06",
        )
        
        context = {
            "course": course,
            'page_url': reverse(
                'learner_profile_view',
                kwargs={'course_id': six.text_type(course_key)}
            ),
            "content": None,
            "max_unit": None,
            "navigation_week_json": json.dumps(navigation_week or {}),
            "navigation_chapter_json": json.dumps(navigation_chapter or {}),
            "uid_actual_json": json.dumps(request.user.id),
            "user_name_json": json.dumps(user_name),
        }
        context['styles_fragment'] = render_to_string('eol_learner_profiles/_styles.html', context)
        context['charts_fragment'] = render_to_string('eol_learner_profiles/_navigation_chart.html', context)
        context['navigation_chart_styles_fragment'] = render_to_string('eol_learner_profiles/_navigation_chart_styles.html', context)
        context['scripts_fragment'] = render_to_string('eol_learner_profiles/_scripts.html', context)

        return context
