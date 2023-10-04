from django.contrib import admin
from courses.models import Lesson
from .models import Teacher

admin.site.register(Teacher)
admin.site.register(Lesson)
