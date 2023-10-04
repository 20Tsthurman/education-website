from django.db import models
from django.apps import apps
from students.models import Student
from users.models import CustomUser
from django.db import transaction
from teachers.models import Teacher
from django.conf import settings



@transaction.atomic
def get_default_course():
    default_course, created = Course.objects.get_or_create(
        name='Default Course',
        defaults={'description': 'This is a default course for lessons without a specified course.'}
    )
    return default_course.id

@transaction.atomic
def default_teacher():
    Teacher = apps.get_model('teachers', 'Teacher')
    CustomUser = apps.get_model('users', 'CustomUser')
    default_user, _ = CustomUser.objects.get_or_create(email='default_teacher@example.com')
    default_teacher, _ = Teacher.objects.get_or_create(user=default_user)
    return default_teacher.id



class Course(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, null=True)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, default=default_teacher)  # Updated this line
    students = models.ManyToManyField(CustomUser, related_name="courses_enrolled", blank=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(default="Default lesson content.")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=get_default_course, db_index=True)
    # other fields...

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} enrolled in {self.course}'