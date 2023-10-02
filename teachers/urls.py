from django.urls import path
from . import views

urlpatterns = [
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/create_lesson/', views.create_lesson, name='create_lesson'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
]

