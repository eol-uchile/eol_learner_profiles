""" Common settings for eol_learner_profiles."""


def plugin_settings(settings):
    # Timeout para requests HTTP (segundos)
    settings.EOL_LEARNER_PROFILES_REQUEST_TIMEOUT = 15
    # URL de servicio API de eol_analytics
    settings.EOL_ANALYTICS_API_URL = ''
    # Token para acceder a servicio API de eol_analytics
    settings.EOL_ANALYTICS_API_TOKEN = ''
