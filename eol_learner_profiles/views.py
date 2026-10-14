# -*- coding: utf-8 -*-

# Python Standard Libraries
import json
import logging
import six
import os

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
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

logger = logging.getLogger(__name__)

# NOTA: Mantenemos la función get_navigation_time por si se necesita a futuro, 
# pero ya no la llamaremos en get_context porque usaremos el JSON.
def get_navigation_time(uid, course_id, group="week", start_date=None, end_date=None):
    base_url = settings.EOL_ANALYTICS_API_URL.rstrip("/")
    api_token = settings.EOL_ANALYTICS_API_TOKEN
    timeout = getattr(settings, "EOL_LEARNER_PROFILES_REQUEST_TIMEOUT", 15)
    encoded_course_id = quote(six.text_type(course_id), safe="")

    url = "{}/metrics/navigation/time/{}/{}".format(base_url, uid, encoded_course_id)
    params = {"group": group}
    if start_date: params["start_date"] = start_date
    if end_date: params["end_date"] = end_date

    headers = {"accept": "application/json", "X-API-KEY": api_token}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        logger.exception("Error al obtener métricas de navegación")
        return {"total_time": 0, "grouped_data": []}


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
        uid = request.user.id
        current_username = request.user.username
        user_name = request.user.profile.name if hasattr(request.user, 'profile') else current_username

        logger.info("EOL Analytics - username=%s uid=%s", current_username, uid)

        # 1. Cargar el JSON desde la carpeta 'data'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'data', 'dashboard_data.json')
        
        dashboard_data = {}
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
        else:
            logger.error("Archivo dashboard_data.json no encontrado en %s", json_path)

        if "estudiantes" in dashboard_data:
            # Es la base de datos completa
            estudiantes = dashboard_data.get("estudiantes", {})
            agregaciones = dashboard_data.get("agregaciones", {})
            
            if current_username in estudiantes:
                estudiante_data = estudiantes[current_username]
            elif estudiantes:
                fallback_user = list(estudiantes.keys())[0]
                estudiante_data = estudiantes[fallback_user]
            else:
                estudiante_data = {}
        else:
            # Es el mockup de un solo estudiante
            estudiante_data = dashboard_data
            agregaciones = {"MEDIAN": {}}

        # 3. Mantenemos CourseGradeFactory si lo necesitas para evaluaciones específicas,
        # pero comentamos las variables mockeadas anteriores.
        course_grade = CourseGradeFactory().read(request.user, course)
        evaluaciones_data = []
        for subsection in course_grade.subsection_grades.values():
            if subsection.format: 
                score_pct = (subsection.percent_graded * 100) if subsection.percent_graded else 0.0
                evaluaciones_data.append({
                    'name': subsection.display_name, 
                    'eval_type': subsection.format,
                    'score_user': round(score_pct, 1)
                })

        # 4. Inyectar todo al contexto
        context = {
            "course": course,
            'page_url': reverse('learner_profile_view', kwargs={'course_id': six.text_type(course_key)}),
            "content": None,
            "max_unit": None,
            
            # Datos inyectados desde el JSON real
            "navigation_week_json": json.dumps(estudiante_data.get("metrics_per_week", [])),
            "navigation_chapter_json": json.dumps(estudiante_data.get("metrics_per_structure", [])),
            "videos_json": json.dumps(estudiante_data.get("metrics_per_video", [])),
            "agregaciones_json": json.dumps(agregaciones),
            
            # Datos locales
            "uid_actual_json": json.dumps(uid),
            "user_name_json": json.dumps(user_name),
            "evaluaciones_json": json.dumps(evaluaciones_data),
        }

        # Renderizado de html
        context['styles_fragment'] = render_to_string('eol_learner_profiles/_styles.html', context)
        context['scripts_fragment'] = render_to_string('eol_learner_profiles/_scripts.html', context)
        context['charts_fragment'] = render_to_string('eol_learner_profiles/_navigation_chart.html', context)
        context['evaluaciones_charts_fragment'] = render_to_string('eol_learner_profiles/_evaluaciones_chart.html', context)
        context['videos_charts_fragment'] = render_to_string('eol_learner_profiles/_videos_chart.html', context)

        return context