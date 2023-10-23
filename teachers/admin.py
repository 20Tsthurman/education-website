from django.contrib import admin
from courses.models import Lesson
from .models import Teacher
from .models import Quiz


admin.site.register(Teacher)
admin.site.register(Lesson)

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'course')  # Adjust the fields to match your model
    search_fields = ('title',)

admin.site.register(Quiz, QuizAdmin)
