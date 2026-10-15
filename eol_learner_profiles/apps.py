# -*- coding: utf-8 -*-

# Python Standard Libraries
import logging, time

# Installed packages (via pip)
from celery.signals import task_prerun, task_postrun
from django.apps import AppConfig

# Edx dependencies
from openedx.core.djangoapps.plugins.constants import PluginSettings, PluginURLs, ProjectType, SettingsType

# Internal project dependencies

logger = logging.getLogger(__name__)
_task_start = {}


class EolLearnerProfilesConfig(AppConfig):
    name = 'eol_learner_profiles'

    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: '',
                PluginURLs.REGEX: r'^',
                PluginURLs.RELATIVE_PATH: 'urls',
            }},
        PluginSettings.CONFIG: {
            ProjectType.CMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: 'settings.common'},
            },
            ProjectType.LMS: {
                SettingsType.COMMON: {
                    PluginSettings.RELATIVE_PATH: 'settings.common'},
            },
        },
        'mako_template_dirs': {
            ProjectType.LMS: 'templates',
            ProjectType.CMS: 'templates',
        }
    }

