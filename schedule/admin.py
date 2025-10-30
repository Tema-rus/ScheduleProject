from django.contrib import admin
from .models import Group, Teacher, Subject, Classroom, TimeSlot, Schedule, Institute, LessonType

admin.site.register(Group)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Classroom)
admin.site.register(TimeSlot)
admin.site.register(Schedule)
admin.site.register(Institute)
admin.site.register(LessonType)