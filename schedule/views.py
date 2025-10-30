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

    class GroupDetailView(DetailView):
        model = Group
        template_name = 'schedule/group_detail.html'
        slug_field = 'slug'
        slug_url_kwarg = 'slug'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            group = self.object
            query = group.group_name

            now = datetime.today()
            result = get_week_type(now)
            current_week = 'Следующая неделя - первая' if now.weekday() == 6 and result else 'Сейчас идёт первая неделя' if not result else 'Сейчас идёт вторая неделя'

            week = self.request.GET.get('week', 'odd' if result else 'even')
            weekdays = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')

            schedule = Schedule.objects.filter(group=group, week_type=week).select_related(
                'teacher', 'subject', 'classroom', 'time_slot'
            ).order_by('day_of_week', 'time_slot__start_time')

            grouped_schedule = {day: [] for day in weekdays}
            for item in schedule:
                grouped_schedule[item.day_of_week].append(item)

            weekday_today = weekdays[now.weekday()]
            schedule_today = Schedule.objects.filter(
                group=group,
                week_type=('odd' if 'первая' in current_week else 'even'),
                day_of_week=weekday_today
            ).select_related('teacher', 'subject', 'classroom', 'time_slot').order_by('time_slot__start_time')

            context.update({
                'week_type': current_week,
                'week': week,
                'week_day': weekday_today,
                'lessons_now': schedule_today,
                'query': query,
                'group': group,
                'grouped_schedule': grouped_schedule,
            })
            return context

    class TeacherDetailView(DetailView):
        model = Teacher
        template_name = 'schedule/teacher_detail.html'
        slug_field = 'slug'
        slug_url_kwarg = 'slug'

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            teacher = self.object
            query = teacher.teacher_name

            now = datetime.today()
            result = get_week_type(now)
            current_week = 'Следующая неделя - первая' if now.weekday() == 6 and result else 'Сейчас идёт первая неделя' if not result else 'Сейчас идёт вторая неделя'

            week = self.request.GET.get('week', 'odd' if result else 'even')
            weekdays = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')

            schedule = Schedule.objects.filter(teacher=teacher, week_type=week).select_related(
                'group', 'subject', 'classroom', 'time_slot'
            ).order_by('day_of_week', 'time_slot__start_time')

            grouped_schedule = {day: [] for day in weekdays}
            for item in schedule:
                grouped_schedule[item.day_of_week].append(item)

            weekday_today = weekdays[now.weekday()]
            schedule_today = Schedule.objects.filter(
                teacher=teacher,
                week_type=('odd' if 'первая' in current_week else 'even'),
                day_of_week=weekday_today
            ).select_related('group', 'subject', 'classroom', 'time_slot').order_by('time_slot__start_time')

            context.update({
                'week_type': current_week,
                'week': week,
                'week_day': weekday_today,
                'lessons_now': schedule_today,
                'grouped_schedule': grouped_schedule,
                'query': query,
            })
            return context

    class SearchRedirectView(View):
        def get(self, request, *args, **kwargs):
            query = request.GET.get('query', '').strip()

            if not query:
                return redirect('home')

            groups = Group.objects.filter(group_name__icontains=query)
            if groups.count() >= 1:
                group = groups.first()
                return redirect('group_detail', slug=group.slug)

            try:
                teachers = Teacher.objects.filter(teacher_name__icontains=query)
                if teachers.count() >= 1:
                    teacher = teachers.first()
                    return redirect('teacher_detail', slug=teacher.slug)
            except Teacher.DoesNotExist:
                raise Http404("Не найдено ни группы, ни преподавателя по запросу")

    class SearchSuggestionsView(View):
        def get(self, request, *args, **kwargs):
            query = request.GET.get('query', '').strip()

            groups = Group.objects.filter(group_name__icontains=query)[:10]
            teachers = Teacher.objects.filter(teacher_name__icontains=query)[:10]

            suggestions = {
                'groups': [{'name': group.group_name, 'slug': group.slug} for group in groups],
                'teachers': [{'name': teacher.teacher_name, 'slug': teacher.slug} for teacher in teachers]
            }

            return JsonResponse(suggestions)
