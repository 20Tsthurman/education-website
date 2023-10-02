from django.shortcuts import redirect, render
from .forms import CourseForm

def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('teacher_dashboard')
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})

