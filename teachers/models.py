from django.db import models
from django.conf import settings
from courses.models import Course
from users.models import CustomUser
from django.urls import reverse
from django.db.models import Sum, Avg

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='teacher')
    bio = models.TextField(blank=True)
    # Add more fields as needed

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)  # Updated this line
    students = models.ManyToManyField('users.CustomUser', through='AssignmentEnrollment')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assignments', null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

class Quiz(models.Model):
    title = models.CharField(max_length=100, db_column='quiz_title')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    students = models.ManyToManyField('users.CustomUser', through='QuizEnrollment')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='quizzes', null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    
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
    is_completed = models.BooleanField(default=False)
    completed_timestamp = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'quiz', 'attempt_number')

    def __str__(self):
        return f"Attempt {self.attempt_number} by {self.student} for {self.quiz}"

    def calculate_final_grade(self):
        # Count the number of correct responses by the student for this attempt.
        correct_responses_count = Response.objects.filter(
            attempt=self,
            choice__is_correct=True
        ).count()

        # Get the total number of questions in the quiz.
        total_questions_count = self.quiz.question_set.count()

        # Calculate the score as a percentage.
        if total_questions_count > 0:
            score_percentage = (correct_responses_count / total_questions_count) * 100
            self.final_grade = round(score_percentage, 2)
            self.save(update_fields=['final_grade'])
            return self.final_grade
        else:
            return 0

    def save(self, *args, **kwargs):
        # Only calculate the final grade if the attempt is completed and final_grade is not set.
        if self.is_completed and self.final_grade is None:
            self.calculate_final_grade()
        super().save(*args, **kwargs)

class Grade(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, null=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)

    
    def calculate_weighted_score(self):
        if self.assignment:
            return self.grade * self.assignment.weight
        elif self.quiz:
            return self.grade * self.quiz.weight
        return self.grade  # Default case if no weight is defined

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
    grade = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Add this line if you want to grade each choice.

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

