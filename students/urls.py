from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('course_quizzes/<int:course_id>/', views.course_quizzes, name='course_quizzes'),
    path('quiz_results/<int:quiz_id>/', views.quiz_results, name='quiz_results'),
]
