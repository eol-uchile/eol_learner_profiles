""" Common settings for eol_learner_profiles."""


def plugin_settings(settings):
    # Timeout para requests HTTP (segundos)
    settings.EOL_LEARNER_PROFILES_REQUEST_TIMEOUT = 15
    # URL de servicio API de eol_analytics
    settings.EOL_LEARNER_PROFILES_ANALYTICS_API_URL = ''
    # Token para acceder a servicio API de eol_analytics
    settings.EOL_LEARNER_PROFILES_ANALYTICS_API_TOKEN = ''
    # Usar evaluaciones simuladas (mock) en vez de consultar la API de eol_analytics
    settings.EOL_LEARNER_PROFILES_MOCK_EVALS = True
    # Usar mapeo de UID (user_id de Open edX -> identificador usado por eol_analytics)
    settings.EOL_LEARNER_PROFILES_USE_UID_MAPPING = True
