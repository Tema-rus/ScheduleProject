from datetime import date
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from unidecode import unidecode


class Institute(models.Model):
    institute_name = models.CharField(max_length=60, verbose_name=_('Название института'))
    address = models.CharField(max_length=255, verbose_name=_('Адрес'))

    def __str__(self):
        return f'{self.institute_name} - {self.address}'

    class Meta:
        verbose_name = _("Институт")
        verbose_name_plural = _("Институты")
        ordering = ['institute_name']


class Group(models.Model):
    group_name = models.CharField(max_length=20, verbose_name=_('Название группы'))
    start_year = models.PositiveIntegerField(default=date.today().year, verbose_name=_('Год начала'))
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, default=1, verbose_name=_('Институт'))
    slug = models.SlugField(unique=True, blank=True, verbose_name=_('Слаг'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.group_name))
        super().save(*args, **kwargs)

    @property
    def course_number(self):
        current_date = date.today()
        current_year = current_date.year
        if current_date.month < 9:
            current_year -= 1
        return current_year - self.start_year + 1

    def __str__(self):
        return self.group_name

    class Meta:
        verbose_name = _("Группа")
        verbose_name_plural = _("Группы")
        ordering = ['institute', 'group_name']


class Teacher(models.Model):
    teacher_name = models.CharField(max_length=60, verbose_name=_('Имя преподавателя'))
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name=_('Слаг'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.teacher_name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.teacher_name

    class Meta:
        verbose_name = _("Преподаватель")
        verbose_name_plural = _("Преподаватели")
        ordering = ['teacher_name']


class Subject(models.Model):
    subject_name = models.CharField(max_length=150, verbose_name=_('Название предмета'))

    def __str__(self):
        return self.subject_name

    class Meta:
        verbose_name = _("Предмет")
        verbose_name_plural = _("Предметы")
        ordering = ['subject_name']


class Classroom(models.Model):
    number = models.CharField(max_length=10, verbose_name=_('Номер аудитории'))
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name=_('Институт'))

    def __str__(self):
        return f'{self.institute}: {self.number}'

    class Meta:
        verbose_name = _("Аудитория")
        verbose_name_plural = _("Аудитории")
        ordering = ['institute', 'number']


class TimeSlot(models.Model):
    start_time = models.TimeField(verbose_name=_('Время начала'))
    end_time = models.TimeField(verbose_name=_('Время окончания'))

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"

    class Meta:
        verbose_name = _("Время")
        verbose_name_plural = _("Время занятий")
        ordering = ['start_time']


class LessonType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_('Тип занятия'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Тип занятия")
        verbose_name_plural = _("Типы занятий")
        ordering = ['name']


class Schedule(models.Model):
    day_of_week_choices = [
        ('Понедельник', _('Понедельник')),
        ('Вторник', _('Вторник')),
        ('Среда', _('Среда')),
        ('Четверг', _('Четверг')),
        ('Пятница', _('Пятница')),
        ('Суббота', _('Суббота')),
    ]
    week_type_choices = [
        ('even', _('Чётная')),
        ('odd', _('Нечётная')),
    ]

    day_of_week = models.CharField(max_length=15, choices=day_of_week_choices, verbose_name=_('День недели'))
    week_type = models.CharField(max_length=10, choices=week_type_choices, verbose_name=_('Тип недели'))
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name=_('Аудитория'))
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('Группа'))
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name=_('Преподаватель'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_('Предмет'))
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, verbose_name=_('Время занятий'))
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE, verbose_name=_('Тип занятия'))

    def __str__(self):
        return f"{self.day_of_week} - {self.subject} - {self.group}"

    class Meta:
        verbose_name = _("Занятие")
        verbose_name_plural = _("Занятия")
        ordering = ['day_of_week', 'week_type', 'time_slot']
        constraints = [
            models.UniqueConstraint(
                fields=['day_of_week', 'week_type', 'time_slot', 'classroom', 'group'],
                name='unique_schedule_constraint'
            )
        ]