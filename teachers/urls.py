from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('course/<int:course_id>/create_lesson/', views.create_lesson, name='create_lesson'),
    path('dashboard/enroll/', views.enroll_student_step1, name='enroll_student_step1'),
    path('dashboard/enroll/<int:course_id>/', views.enroll_student_step2, name='enroll_student_step2'),
]
