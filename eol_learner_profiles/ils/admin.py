# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import CourseILSConfig, ILSDefinition, ILSUserResponse


@admin.register(ILSDefinition)
class ILSDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'version')
    search_fields = ('name', 'markdown_content')


@admin.register(CourseILSConfig)
class CourseILSConfigAdmin(admin.ModelAdmin):
    list_display = (
        'course_id', 'ils_definition', 'reuse_policy',
        'retake_requested_at', 'updated_by', 'updated_at',
    )
    list_filter = ('reuse_policy',)
    search_fields = ('course_id',)
    raw_id_fields = ('updated_by',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ILSUserResponse)
class ILSUserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course_id', 'ils_definition', 'source', 'completed_at')
    list_filter = ('ils_definition', 'source')
    search_fields = ('user__username', 'user__email', 'course_id')
    autocomplete_fields = ('user',)
    list_select_related = ('user', 'ils_definition')
    show_full_result_count = False
    date_hierarchy = 'completed_at'
    ordering = ('-completed_at',)

