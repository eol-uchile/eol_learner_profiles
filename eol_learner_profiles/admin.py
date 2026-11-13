# -*- coding: utf-8 -*-
"""Django autodescubre ``<app>.admin``; el admin vive en cada carpeta."""

from .ils import admin as ils_admin  # noqa: F401
from .recommendations import admin as recommendations_admin  # noqa: F401
