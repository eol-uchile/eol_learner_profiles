import os
import json
import logging
import requests
import six
from urllib.parse import quote
from django.conf import settings

logger = logging.getLogger(__name__)

# ==========================================
# Rutas API
# ==========================================
def get_api_headers():
    api_token = getattr(settings, "EOL_ANALYTICS_API_TOKEN", "")
    return {"accept": "application/json", "X-API-KEY": api_token}

def get_base_url():
    return getattr(settings, "EOL_ANALYTICS_API_URL", "").rstrip("/")

def check_api_availability():
    url = get_base_url() + "/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        logger.warning("conexión exitosa a la api: %s", response.json())
        return True
    except Exception as e:
        logger.error("falló la conexión a la api: %s", str(e))
        return False

def get_api_navigation_time(uid, course_id, group="week"):
    url = "{}/metrics/navigation/time/{}/{}".format(get_base_url(), uid, quote(six.text_type(course_id), safe=""))
    try:
        response = requests.get(url, headers=get_api_headers(), params={"group": group}, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("ERROR API (navigation %s): %s", group, str(e))
        return {}

def get_api_problem_time(uid, course_id):
    url = "{}/metrics/problem/time/{}/{}".format(get_base_url(), uid, quote(six.text_type(course_id), safe=""))
    try:
        response = requests.get(url, headers=get_api_headers(), timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("ERROR API (problem): %s", str(e))
        return {}

def get_api_completion_progress(uid, course_id, group="week"):
    url = "{}/metrics/completion/progress/{}/{}".format(get_base_url(), uid, quote(six.text_type(course_id), safe=""))
    try:
        response = requests.get(url, headers=get_api_headers(), params={"group": group}, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("ERROR API (completion %s): %s", group, str(e))
        return {}

def get_api_video_metrics(uid, course_id):
    url = "{}/metrics/video/{}/{}".format(get_base_url(), uid, quote(six.text_type(course_id), safe=""))
    try:
        response = requests.get(url, headers=get_api_headers(), timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("ERROR API (video): %s", str(e))
        return {}

def get_api_engagement_metrics(uid, course_id):
    url = "{}/metrics/engagement/{}/{}".format(get_base_url(), uid, quote(six.text_type(course_id), safe=""))
    try:
        response = requests.get(url, headers=get_api_headers(), timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("ERROR API (engagement): %s", str(e))
        return {}


# ==========================================
# JSON local
# ==========================================
def get_local_dashboard_data(username):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'data', 'dashboard_data.json')
    
    if not os.path.exists(json_path):
        return {}, {"MEDIAN": {}}

    with open(json_path, 'r', encoding='utf-8') as f:
        dashboard_data = json.load(f)

    if "estudiantes" in dashboard_data:
        estudiantes = dashboard_data.get("estudiantes", {})
        agregaciones = dashboard_data.get("agregaciones", {})
        estudiante_data = estudiantes.get(username, list(estudiantes.values())[0] if estudiantes else {})
    else:
        estudiante_data = dashboard_data
        agregaciones = {"MEDIAN": {}}

    return estudiante_data, agregaciones


def get_local_metrics_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    metricas_path = os.path.join(current_dir, 'data', 'mock_metricas.json')
    
    if not os.path.exists(metricas_path):
        return []

    with open(metricas_path, 'r', encoding='utf-8') as f:
        return json.load(f)