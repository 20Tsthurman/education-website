from django.db import models
from django.conf import settings
from users.models import CustomUser

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher')
    bio = models.TextField(blank=True)
    # Add more fields as needed

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)  # Updated this line
    students = models.ManyToManyField('users.CustomUser', through='QuizEnrollment')
    # Add more fields as needed

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)  # Updated this line
    students = models.ManyToManyField('users.CustomUser', through='AssignmentEnrollment')
    # Add more fields as needed

class Grade(models.Model):
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    # Add more fields as needed

class LessonEnrollment(models.Model):
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE)  # Ensure this line stays as is
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

class QuizEnrollment(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

class AssignmentEnrollment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)