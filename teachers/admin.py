from django.contrib import admin
from courses.models import Lesson
from .models import Teacher
from .models import Quiz
from django.contrib import admin
from .models import Question, Choice



admin.site.register(Teacher)
admin.site.register(Lesson)

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'course')  # Adjust the fields to match your model
    search_fields = ('title',)

class ChoiceInline(admin.TabularInline):  # or admin.StackedInline if you prefer
    model = Choice
    extra = 3  # Number of empty choice fields to display

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question)
admin.site.register(Choice)
