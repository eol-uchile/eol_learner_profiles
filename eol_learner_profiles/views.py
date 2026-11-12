import os
import json
import logging
import math
import six

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
import random

# Internal project dependencies
from .courseware import load_course
from .ils.display import render_ils_fragment

# Edx dependencies
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.instructor import permissions
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from web_fragments.fragment import Fragment
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import UsageKey

from .fetch_metrics import (
    get_api_navigation_time,
    get_api_problem_time,
    get_api_completion_progress,
    get_api_video_metrics,
    get_api_aggregated_metrics,
    get_evaluation_grades,
    aggregate_problem_time,
    check_api_availability,
)
from .recommendations.service import get_recommendation
from .user_mapping import get_api_uid

logger = logging.getLogger(__name__)

class EolLearnerProfileFragmentView(EdxFragmentView):
    def render_to_fragment(self, request, course_id, **kwargs):
        course_key, course, is_staff = load_course(request, course_id)

        context = self.get_context(request, course_id, course, course_key)
        context['ils_fragment'] = render_ils_fragment(request, course, course_key, is_staff)
        html = render_to_string('eol_learner_profiles/learner_profile_fragment.html', context)
        return Fragment(html)

    def render_standalone_response(self, request, fragment, **kwargs):
        """
        El template ya es una página completa (hereda ``/main.html``): se entrega
        tal cual, sin el envoltorio ``fragments/standalone-page-fragment.html``
        de EdxFragmentView, que la anidaba dentro de otra página.
        """
        return HttpResponse(fragment.content)

    def get_context(self, request, course_id, course, course_key):
        uid = request.user.id
        current_username = request.user.username
        user_name = request.user.profile.name if hasattr(request.user, 'profile') else current_username

        logger.info("EOL Analytics - username=%s uid=%s", current_username, uid)

        # Flag uso API
        use_api_setting = getattr(settings, 'EOL_LEARNER_PROFILES_USE_API', True)
        USE_API = str(use_api_setting).lower() == 'true'

        # Flag uso evaluaciones mock
        use_mock_evals_setting = getattr(settings, 'EOL_LEARNER_PROFILES_MOCK_EVALS', True)
        USE_MOCK_EVALS = str(use_mock_evals_setting).lower() == 'true'

        if USE_API:
            check_api_availability()

            # Descomentar para forzar uso de user_id + curso real de la api
            # uid = ...
            # course_id = "..."
            uid = get_api_uid(uid)
            nav_data_week = get_api_navigation_time(uid, course_id, group="week")
            comp_data_week = get_api_completion_progress(uid, course_id, group="week")
            nav_data_chapter = get_api_navigation_time(uid, course_id, group="chapter")
            comp_data_chapter = get_api_completion_progress(uid, course_id, group="chapter")
            vid_data = get_api_video_metrics(uid, course_id)
            prob_data_time = get_api_problem_time(uid, course_id)
            agg_data = get_api_aggregated_metrics(uid, course_id)
            evaluaciones_data = []
            # Fix momentáneo para calculo de p33 y p66 para eval_time
            if 'problem_time_user' not in agg_data:
                pt = aggregate_problem_time(prob_data_time)
                if pt:
                    agg_data.update(problem_time_user=pt['user'], problem_time_p33=pt['p33'], problem_time_p66=pt['p66'])
        else:
            
            mock_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'mock_api_data.json')
            try:
                with open(mock_path, 'r', encoding='utf-8') as f:
                    all_mock_data = json.load(f)
                
                user_mock = all_mock_data.get(str(user_name), {}) # trata de traer datos del usuario

                if not user_mock and all_mock_data:
                    first_user = list(all_mock_data.keys())[0]
                    user_mock = all_mock_data[first_user]
                
                nav_data_week = user_mock.get("navigation_week", {})
                comp_data_week = user_mock.get("completion_week", {})
                nav_data_chapter = user_mock.get("navigation_chapter", {})
                comp_data_chapter = user_mock.get("completion_chapter", {})
                vid_data = user_mock.get("videos", {})
                prob_data_time = user_mock.get("problems_time", {})
                agg_data = user_mock.get("aggregated", {})
                evaluaciones_data = user_mock.get("evaluaciones", [])
                
                logger.warning("Datos json local: %s", user_name)

            except Exception as e:
                logger.error("ERROR - Datos json local: %s", str(e))
                nav_data_week = comp_data_week = nav_data_chapter = comp_data_chapter = vid_data = prob_data_time = agg_data = {}
                evaluaciones_data = []

        # Nombres de evaluaciones (vista tiempo)
        if prob_data_time and "grouped_data" in prob_data_time:
            store = modulestore()
            for item in prob_data_time["grouped_data"]:
                block_id_str = item.get("block_id")
                if block_id_str:
                    try:
                        usage_key = UsageKey.from_string(block_id_str)
                        
                        block_item = store.get_item(usage_key)
                        
                        if block_item:
                            fallback_name = "Evaluación " + str(item["block_id"])[-4:]
                            item["display_name"] = block_item.display_name or fallback_name
                            
                            if hasattr(block_item, 'format') and block_item.format:
                                item["eval_type"] = block_item.format
                            else:
                                item["eval_type"] = "Tipo evaluación"
                        else:
                            item["display_name"] = "Evaluación " + str(item["block_id"])[-4:]
                            item["eval_type"] = "Tipo evaluación"
                    except Exception as e:
                        item["display_name"] = "Evaluación " + str(block_id_str)[-4:]
                        item["eval_type"] = "Tipo evaluación"

        # Evaluaciones
        evaluaciones_data = get_evaluation_grades(request.user, course, uid, USE_MOCK_EVALS)
        
        # Calcula el promedio de las evaluaciones
        promedio_eval = 0
        if evaluaciones_data:
            def _to_float(value):
                """Return a float, or None if the value is missing, non-numeric, or NaN."""
                try:
                    f = float(value)
                except (TypeError, ValueError):
                    return None
                return None if math.isnan(f) else f
            notas_validas = [n for n in (_to_float(item.get('score_user')) for item in evaluaciones_data) if n is not None]
            promedio_eval = round(sum(notas_validas) / len(notas_validas), 1) if notas_validas else None

        # Resumen
        tiempo_minutos = round(float(nav_data_week.get("total_time", 0)) / 60) if nav_data_week.get("total_time") else 0

        metricas_data = [
            {
                "key": "tiempo",
                "value": tiempo_minutos
            },
            {
                "key": "contenido",
                "value": comp_data_week.get("total_progress", 0)
            },
            {
                "key": "evaluaciones",
                "value": promedio_eval
            },
            {
                "key": "videos",
                "value": f"{vid_data.get('individual_video_count', 0)}/{vid_data.get('total_video_count', 0)}"
            }
        ]

        # Recomendaciones
        rec_vid_dict, rec_nav_dict, rec_eval_dict = get_recommendation(request.user, course_key, agg_data)
        # Contexto
        context = {
            "course": course,
            'page_url': reverse('learner_profile_view', kwargs={'course_id': six.text_type(course_key)}),
            "content": None,
            "max_unit": None,
            
            "nav_week_json": json.dumps(nav_data_week),
            "comp_week_json": json.dumps(comp_data_week),
            "nav_chapter_json": json.dumps(nav_data_chapter),
            "comp_chapter_json": json.dumps(comp_data_chapter),
            "videos_json": json.dumps(vid_data),
            "problems_time_json": json.dumps(prob_data_time),
            
            "metricas_json": json.dumps(metricas_data),
            "uid_actual_json": json.dumps(uid),
            "user_name_json": json.dumps(user_name),
            "evaluaciones_json": json.dumps(evaluaciones_data),

            "rec_videos_dict": rec_vid_dict,
            "rec_nav_dict": rec_nav_dict,
            "rec_eval_dict": rec_eval_dict,
        }

        # Render
        context['charts_fragment'] = render_to_string('eol_learner_profiles/_navigation_chart.html', context)
        context['evaluaciones_charts_fragment'] = render_to_string('eol_learner_profiles/_evaluaciones_chart.html', context)
        context['videos_charts_fragment'] = render_to_string('eol_learner_profiles/_videos_chart.html', context)

        return context
