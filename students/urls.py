from django.urls import path
from . import views
from .views import view_course_grades

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    #path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('course_quizzes/<int:course_id>/', views.course_quizzes, name='course_quizzes'),
    path('quiz_results/<int:quiz_id>/', views.quiz_results, name='quiz_results'),
    path('view_grades/', views.view_grades, name='view_grades'),
    path('take_quiz/<int:quiz_id>/<int:question_number>/', views.take_quiz, name='take_quiz'),
    path('quiz_results/<int:quiz_id>/', views.quiz_results, name='quiz_results'),
    path('review_test/<int:quiz_id>/<int:attempt_number>/', views.review_test, name='review_test'),
    path('course/<int:course_id>/grades/', view_course_grades, name='view_course_grades'),

]
