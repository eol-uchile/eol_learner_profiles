from django.conf import settings
from django.utils.translation import ugettext_noop

from lms.djangoapps.courseware.tabs import EnrolledTab
from xmodule.tabs import TabFragmentViewMixin
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.instructor import permissions


class EolLearnerProfileTab(TabFragmentViewMixin, EnrolledTab):
    type = 'eol_learner_profiles'
    title = ugettext_noop('Recomendaciones')
    priority = None
    view_name = 'learner_profile_view'
    fragment_view_name = 'eol_learner_profiles.views.EolCompletionFragmentView'
    is_hideable = False
    is_default = True
    body_class = 'eol_learner_profiles'
    online_help_token = 'eol_learner_profiles'
    # True if this tab should be displayed only for instructors
    course_staff_only = False

    @classmethod
    def is_enabled(cls, course, user=None):
        """
        Returns true if the specified user has staff access.
        """
        return True
