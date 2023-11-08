from django.contrib import admin
from courses.models import Lesson
from .models import Attempt, Teacher
from .models import Quiz
from django.contrib import admin
from .models import Question, Choice
from .models import Grade
from django.db.models import Avg


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


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('get_student_email', 'get_quiz_title', 'highest_average_grade', 'get_teacher_email')

    def get_student_email(self, obj):
        return obj.attempt.student.email if obj.attempt and obj.attempt.student else "-"
    get_student_email.admin_order_field = 'attempt__student__email'
    get_student_email.short_description = 'Student Email'

    def get_quiz_title(self, obj):
        return obj.attempt.quiz.title if obj.attempt and obj.attempt.quiz else "-"
    get_quiz_title.admin_order_field = 'attempt__quiz__title'
    get_quiz_title.short_description = 'Quiz Title'

    def highest_average_grade(self, obj):
        if not obj.attempt:
            return "No Attempt"
        student = obj.attempt.student
        quiz = obj.attempt.quiz

        # Retrieve the final grades from the attempts directly, assuming they have been calculated and saved already.
        attempts = Attempt.objects.filter(student=student, quiz=quiz)
        final_grades = [attempt.final_grade for attempt in attempts if attempt.final_grade is not None]

        if final_grades:
            highest_average = max(final_grades)
            return f"{highest_average:.2f}%"
        return "No Grades"
    highest_average_grade.short_description = 'Highest Average Grade'



    def get_teacher_email(self, obj):
        return obj.teacher.user.email if obj.teacher and obj.teacher.user else 'No teacher'
    get_teacher_email.admin_order_field = 'teacher__user__email'
    get_teacher_email.short_description = 'Teacher Email'