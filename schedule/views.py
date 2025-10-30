from datetime import datetime
from django.views.generic import TemplateView, DetailView
from django.views import View
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from .models import Institute, Group, Teacher, Schedule
from .utlis import get_week_type  # ⚠️ Опечатка: должно быть utils

import os
from django.conf import settings


class IndexView(TemplateView):
    template_name = 'schedule/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # === Основная логика ===
        institutes = Institute.objects.all()
        groups = Group.objects.all()

        institute_data = []
        for institute in institutes:
            courses = set(group.course_number for group in groups if group.institute == institute)
            courses_data = []
            for course in sorted(courses):
                course_groups = [group for group in groups if
                                 group.institute == institute and group.course_number == course]
                courses_data.append({
                    'course': course,
                    'groups': course_groups,
                })
            institute_data.append({
                'institute': institute,
                'courses': courses_data,
            })

        query = self.request.GET.get('query', '')
        context.update({
            'query': query,
            'institute_data': institute_data,
        })

        # === ВРЕМЕННЫЙ ДИАГНОСТИЧЕСКИЙ БЛОК (для отладки статики) ===
        static_root = settings.STATIC_ROOT
        if os.path.exists(static_root):
            files = []
            for root, dirs, filenames in os.walk(static_root):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, static_root)
                    files.append(rel_path)
            context['static_files_list'] = sorted(files)
        else:
            context['static_files_list'] = ['STATIC_ROOT не существует!']
        # ===================================

        return context