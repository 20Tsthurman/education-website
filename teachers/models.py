from django.db import models
from django.conf import settings

from courses.models import Course

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    # Add more fields as needed

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField('users.CustomUser', through='QuizEnrollment')
    # Add more fields as needed

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField('users.CustomUser', through='AssignmentEnrollment')
    # Add more fields as needed
    
class Lesson(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(default="Default lesson content.")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ManyToManyField('users.CustomUser', through='LessonEnrollment')



class Grade(models.Model):
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    # Add more fields as needed

class Discussion(models.Model):
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    # Add more fields as needed

class File(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='uploads/')  # You can define a custom upload path
    # Add more fields as needed

# Create enrollment models for quizzes, assignments, and lessons

class QuizEnrollment(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

class AssignmentEnrollment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

class LessonEnrollment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
