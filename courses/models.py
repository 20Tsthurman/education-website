from django.db import models
from users.models import CustomUser

class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="courses_taught")
    students = models.ManyToManyField(CustomUser, related_name="courses_enrolled", blank=True)

    def __str__(self):
        return self.name

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_lessons', null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()  # This can be more complex in the future (e.g., rich text, videos, etc.)
    sequence_number = models.PositiveIntegerField()

    def __str__(self):
        return self.title