from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from students.models import Student
from courses.models import Course, Enrollment
from .models import Question, Choice, Quiz


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

ChoiceFormSet = inlineformset_factory(
    Question, Choice, fields=('text', 'is_correct'), extra=4, max_num=4
)  # renamed formset


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title'] 

class QuizWeightForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['weight']