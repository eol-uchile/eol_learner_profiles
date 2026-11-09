import os
import json
import logging
import six

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

# Edx dependencies
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.instructor import permissions
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.plugin_api.views import EdxFragmentView
from web_fragments.fragment import Fragment
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory

from .fetch_metrics import (
    get_api_navigation_time,
    get_api_problem_time,
    get_api_completion_progress,
    get_api_video_metrics,
    get_api_engagement_metrics,
    check_api_availability,
    get_local_dashboard_data,
    get_local_metrics_data
)

logger = logging.getLogger(__name__)

def get_recommendation(vid_data, nav_data, eval_data):
            try:
                rec_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'recomendaciones.json')
                with open(rec_path, 'r', encoding='utf-8') as f:
                    recomendaciones = json.load(f)
                    
                rec_mock = "rec_test" 

                rec_videos = recomendaciones.get("videos", {}).get(rec_mock, None)
                rec_nav = recomendaciones.get("navegacion", {}).get(rec_mock, None)
                rec_eval = recomendaciones.get("evaluaciones", {}).get(rec_mock, None)

                return rec_videos, rec_nav, rec_eval
            except Exception as e:
                logger.error("Error leyendo recomendaciones.json: %s", str(e))
                return None

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
        return Fragment(html)

    def get_context(self, request, course_id, course, course_key):
        uid = request.user.id
        current_username = request.user.username
        user_name = request.user.profile.name if hasattr(request.user, 'profile') else current_username

        logger.info("EOL Analytics - username=%s uid=%s", current_username, uid)

        # Flag uso API
        use_api_setting = getattr(settings, 'EOL_LEARNER_PROFILES_USE_API', True)
        USE_API = str(use_api_setting).lower() == 'false'

        if USE_API:
            check_api_availability()
            
            nav_data_week = get_api_navigation_time(uid, course_id, group="week")
            comp_data_week = get_api_completion_progress(uid, course_id, group="week")
            nav_data_chapter = get_api_navigation_time(uid, course_id, group="chapter")
            comp_data_chapter = get_api_completion_progress(uid, course_id, group="chapter")
            vid_data = get_api_video_metrics(uid, course_id)
            prob_data_time = get_api_problem_time(uid, course_id)
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
                
                logger.warning("Datos json local: %s", user_name)
            except Exception as e:
                logger.error("ERROR - Datos json local: %s", str(e))
                nav_data_week = comp_data_week = nav_data_chapter = comp_data_chapter = vid_data = prob_data_time = {}

        # Evaluaciones
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

        # Calcular el promedio de las evaluaciones
        promedio_eval = 0
        if evaluaciones_data:
            suma_notas = sum(item['score_user'] for item in evaluaciones_data)
            promedio_eval = round(suma_notas / len(evaluaciones_data), 1)

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
        rec_vid_dict, rec_nav_dict, rec_eval_dict = get_recommendation(vid_data, nav_data_week, evaluaciones_data)
        
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

        context['charts_fragment'] = render_to_string('eol_learner_profiles/_navigation_chart.html', context)
        context['evaluaciones_charts_fragment'] = render_to_string('eol_learner_profiles/_evaluaciones_chart.html', context)
        context['videos_charts_fragment'] = render_to_string('eol_learner_profiles/_videos_chart.html', context)

        return context