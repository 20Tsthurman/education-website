# students/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Enrollment
from courses.models import Lesson

@login_required
def student_dashboard(request):
    # Get the courses the student is enrolled in
    enrollments = Enrollment.objects.filter(student=request.user)
    courses_enrolled = [enrollment.course for enrollment in enrollments]
    return render(request, 'students/dashboard.html', {'courses_enrolled': courses_enrolled})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'students/lesson_detail.html', {'lesson': lesson})
