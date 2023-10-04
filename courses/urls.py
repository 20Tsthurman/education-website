from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('create_course/', views.create_course, name='create_course'),
    path('course_detail/<int:pk>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_student, name='enroll_student'),
    path('my_courses/', views.my_courses, name='my_courses'),
]
