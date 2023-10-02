from pyexpat.errors import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from courses.models import Course, Lesson
from courses.forms import LessonForm
from django.contrib.auth.decorators import login_required


def teacher_dashboard(request):
    # Retrieve the courses taught by the teacher
    courses = Course.objects.filter(teacher=request.user)
    return render(request, 'teachers/teacher_dashboard.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # other logic...
    return render(request, 'teachers/course_detail.html', {'course': course})

@login_required
def create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    
    # Check if the user is the teacher of the course
    if course.teacher != request.user:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            
            # Determine the next sequence number
            existing_lessons_count = course.lesson_set.count()
            lesson.sequence_number = existing_lessons_count + 1
            
            lesson.save()
            messages.success(request, "Lesson created successfully!")
            return redirect('teachers:course_detail', course_id=course.id)
    else:
        form = LessonForm()
    return render(request, 'teachers/create_lesson.html', {'form': form, 'course': course})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'teachers/lesson_detail.html', {'lesson': lesson})
