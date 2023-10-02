from django import forms
from courses.models import Course
from .models import Lesson

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'content']  # adjust the fields as needed