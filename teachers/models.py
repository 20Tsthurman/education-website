from django.db import models
from django.conf import settings
from courses.models import Course
from users.models import CustomUser
from django.urls import reverse

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher')
    bio = models.TextField(blank=True)
    # Add more fields as needed

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    students = models.ManyToManyField('users.CustomUser', through='QuizEnrollment')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='quizzes', null=True)
    
    def get_absolute_url(self):
        return reverse('teachers:quiz_detail', kwargs={'quiz_id': self.id})

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

class AssignmentEnrollment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

class Response(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class QuizEnrollment(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)