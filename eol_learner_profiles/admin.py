# -*- coding: utf-8 -*-
"""Django autodescubre ``<app>.admin``; el admin vive en cada carpeta."""

from .ils import admin as ils_admin  # noqa: F401
from .recommendations import admin as recommendations_admin  # noqa: F401

from django.contrib import admin

from .models import DataFile


@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    list_display = ('key', 'file', 'uploaded_at')
    list_filter = ('key',)
