# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Recommendation, RecommendationCase


class RecommendationInline(admin.TabularInline):
    model = Recommendation
    extra = 0


@admin.register(RecommendationCase)
class RecommendationCaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'key')
    search_fields = ('name', 'key')
    inlines = [RecommendationInline]


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('case', 'graph', 'first_level', 'second_level', 'updated_at')
    list_filter = ('case', 'graph', 'first_level', 'second_level')
    list_select_related = ('case',)
    search_fields = ('text',)
