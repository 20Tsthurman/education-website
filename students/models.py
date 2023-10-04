# students/models.py

from django.db import models
from django.conf import settings  # Import the settings module

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use settings.AUTH_USER_MODEL
    enrolled_courses = models.ManyToManyField('courses.Course', related_name='enrolled_students')

    def __str__(self):
        return self.user.username
    pass