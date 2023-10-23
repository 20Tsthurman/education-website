from django import forms
from students.models import Student
from courses.models import Course, Enrollment
from .models import Question
from .models import Question, Choice, Quiz
from django.forms import modelformset_factory

class CourseSelectionForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all())

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student']

class TeacherEnrollmentForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']

ChoiceFormSet = modelformset_factory(Choice, fields=('text', 'is_correct'), extra=4, max_num=4)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title'] 
