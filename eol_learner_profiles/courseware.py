# -*- coding: utf-8 -*-
"""Acceso al curso compartido por las vistas de la pestaña y de ILS."""

import logging

from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.courseware.masquerade import setup_masquerade
from opaque_keys.edx.keys import CourseKey

logger = logging.getLogger(__name__)


def load_course(request, course_id):
    """
    Valida acceso al curso y devuelve ``(course_key, course, is_staff)``.

    Roles:
      * Estudiante matriculado -> ``is_staff`` False.
      * Equipo del curso (staff / instructor) o superusuario -> ``is_staff`` True.
      * Staff en "Ver el curso como: Estudiante" (masquerade) -> ``is_staff``
        False, y ``request.user`` pasa a ser el usuario suplantado.

    Quien no puede ver el curso obtiene Http404 en ``get_course_with_access``.
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course_with_access(request.user, "load", course_key)

    real_staff = (
        bool(has_access(request.user, 'staff', course))
        or bool(getattr(request.user, 'is_superuser', False))
    )

    masquerading_as_student = False
    if real_staff:
        try:
            course_masquerade, effective_user = setup_masquerade(request, course_key, real_staff)[:2]
            if effective_user is not None:
                request.user = effective_user
            masquerading_as_student = bool(
                course_masquerade is not None
                and getattr(course_masquerade, 'role', None) == 'student'
            )
        except Exception:  # pragma: no cover
            # Sólo corre para staff real: si falla, el staff sigue viendo el
            # panel de staff; nunca se le expone a un estudiante.
            logger.exception("eol_learner_profiles: no se pudo resolver masquerade")

    return course_key, course, real_staff and not masquerading_as_student
