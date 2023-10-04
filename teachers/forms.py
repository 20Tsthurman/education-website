from django import forms
from students.models import Student
from courses.models import Course, Enrollment

class CourseSelectionForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all())

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student']

class TeacherEnrollmentForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())