from datetime import datetime
from django.views.generic import TemplateView, DetailView
from django.views import View
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from .models import Institute, Group, Teacher, Schedule
from .utils import get_week_type

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

        now = datetime.today().date()
        is_even_week = get_week_type(now)  # True = чётная = вторая

        # Определяем текст для отображения
        if now.weekday() == 6:  # воскресенье
            next_week_is_even = not is_even_week
            current_week_str = f"На следующей неделе - {'вторая' if next_week_is_even else 'первая'}"
        else:
            current_week_str = f"Эта неделя - {'вторая' if is_even_week else 'первая'}"

        # Определяем week_type для фильтрации расписания
        if now.weekday() == 6:
            # В воскресенье показываем расписание на следующую неделю
            week_type_for_db = 'even' if not is_even_week else 'odd'
        else:
            week_type_for_db = 'even' if is_even_week else 'odd'

        # Получаем week из GET (для переключения между неделями)
        week = self.request.GET.get('week', week_type_for_db)

        weekdays = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')

        # Расписание на выбранную неделю
        schedule = Schedule.objects.filter(
            group=group,
            week_type=week
        ).select_related(
            'teacher', 'subject', 'classroom', 'time_slot'
        ).order_by('day_of_week', 'time_slot__start_time')

        grouped_schedule = {day: [] for day in weekdays}
        for item in schedule:
            grouped_schedule[item.day_of_week].append(item)

        # Расписание на сегодня (только если не воскресенье)
        weekday_today = weekdays[now.weekday()]
        if now.weekday() != 6:
            schedule_today = Schedule.objects.filter(
                group=group,
                week_type=week_type_for_db,
                day_of_week=weekday_today
            ).select_related('teacher', 'subject', 'classroom', 'time_slot').order_by('time_slot__start_time')
        else:
            schedule_today = []

        context.update({
            'week_type': current_week_str,
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

        now = datetime.today().date()
        is_even_week = get_week_type(now)  # True = чётная = вторая

        # Определяем текст для отображения
        if now.weekday() == 6:  # воскресенье
            next_week_is_even = not is_even_week
            current_week_str = f"На следующей неделе - {'вторая (2)' if next_week_is_even else 'первая (1)'}"
        else:
            current_week_str = f"Эта неделя - {'вторая (2)' if is_even_week else 'первая (1)'}"

        # Определяем week_type для фильтрации расписания
        if now.weekday() == 6:
            # В воскресенье показываем расписание на следующую неделю
            week_type_for_db = 'even' if not is_even_week else 'odd'
        else:
            week_type_for_db = 'even' if is_even_week else 'odd'

        # Получаем week из GET (для переключения между неделями)
        week = self.request.GET.get('week', week_type_for_db)

        weekdays = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')

        # Расписание на выбранную неделю
        schedule = Schedule.objects.filter(
            teacher=teacher,
            week_type=week
        ).select_related(
            'teacher', 'subject', 'classroom', 'time_slot'
        ).order_by('day_of_week', 'time_slot__start_time')

        grouped_schedule = {day: [] for day in weekdays}
        for item in schedule:
            grouped_schedule[item.day_of_week].append(item)

        # Расписание на сегодня (только если не воскресенье)
        weekday_today = weekdays[now.weekday()]
        if now.weekday() != 6:
            schedule_today = Schedule.objects.filter(
                teacher=teacher,
                week_type=week_type_for_db,
                day_of_week=weekday_today
            ).select_related('teacher', 'subject', 'classroom', 'time_slot').order_by('time_slot__start_time')
        else:
            schedule_today = []

        context.update({
            'week_type': current_week_str,
            'week': week,
            'week_day': weekday_today,
            'lessons_now': schedule_today,
            'query': query,
            'teacher': teacher,
            'grouped_schedule': grouped_schedule,
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
