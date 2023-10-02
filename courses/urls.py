from django.urls import path
from . import views

urlpatterns = [
    path('create_course/', views.create_course, name='create_course'),
]
