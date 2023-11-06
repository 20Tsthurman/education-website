from django.db import models
from django.conf import settings
from courses.models import Course
from users.models import CustomUser
from django.urls import reverse

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher')
    bio = models.TextField(blank=True)
    # Add more fields as needed

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)  # Updated this line
    students = models.ManyToManyField('users.CustomUser', through='AssignmentEnrollment')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assignments', null=True)

class Quiz(models.Model):
    title = models.CharField(max_length=100, db_column='quiz_title')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    students = models.ManyToManyField('users.CustomUser', through='QuizEnrollment')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='quizzes', null=True)
    
    def get_absolute_url(self):
        return reverse('teachers:quiz_detail', kwargs={'quiz_id': self.id})
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)

    def __str__(self):
        return self.text
    
class Attempt(models.Model):
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    attempt_number = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'quiz', 'attempt_number')

class Grade(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, null=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

class LessonEnrollment(models.Model):
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE)  # Ensure this line stays as is
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

class AssignmentEnrollment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class Response(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, null=True)

class QuizEnrollment(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)

