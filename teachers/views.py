from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from courses.models import Course, Lesson
from courses.forms import LessonForm
from django.contrib.auth.decorators import login_required
from teachers.models import Teacher
from .forms import TeacherEnrollmentForm
from teachers.forms import CourseSelectionForm, EnrollmentForm



@login_required
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    courses = Course.objects.filter(teacher=teacher)

    # ... (rest of your existing code, if any)

    return render(
        request,
        'teachers/teacher_dashboard.html',
        {'courses': courses}
    )

@login_required
def enroll_student_step1(request):
    if request.method == 'POST':
        form = CourseSelectionForm(request.POST)
        if form.is_valid():
            course_id = form.cleaned_data['course'].id
            return redirect('teachers:enroll_student_step2', course_id=course_id)
    else:
        form = CourseSelectionForm()
    return render(request, 'teachers/enroll_step1.html', {'form': form})

@login_required
def enroll_student_step2(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.course = course
            enrollment.save()
            return redirect('teachers:teacher_dashboard')
    else:
        form = EnrollmentForm()
    return render(request, 'teachers/enroll_step2.html', {'form': form, 'course': course})



@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'teachers/lesson_detail.html', {'lesson': lesson})

@login_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('teachers:lesson_detail', lesson_id=lesson.id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'teachers/edit_lesson.html', {'form': form})

@login_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect('teachers:course_detail', course_id=lesson.course.id)
    return render(request, 'teachers/delete_lesson.html', {'lesson': lesson})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'courses/course_detail.html', {'course': course})

@login_required
def create_lesson(request, course_id):
    teacher = get_object_or_404(Teacher, user=request.user)
    course = get_object_or_404(Course, id=course_id, teacher=teacher)
    
    if course.teacher != teacher:
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
