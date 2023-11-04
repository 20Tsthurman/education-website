from django.shortcuts import redirect, render
from .forms import CourseForm
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from courses.models import Course, Enrollment
from courses.forms import LessonForm
from django.contrib.auth.decorators import login_required
from teachers.models import Teacher 
from .forms import EnrollmentForm
from courses.models import Course
from teachers.models import Grade
from django.db.models import Q

@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user.teacher  # Assume the logged in user is a Teacher
            course.save()
            return redirect('courses:course_detail', course.id)  # Assume 'courses' is the namespace for your courses app URLs
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})


@login_required
def create_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
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
            return redirect('courses:course_detail', course_id=course.id)
    else:
        form = LessonForm()
    return render(request, 'courses/create_lesson.html', {'form': form, 'course': course})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollments = Enrollment.objects.filter(course=course)
    students = [enrollment.student for enrollment in enrollments]
    assignments = course.assignments.all()
    
    # Determine user type and fetch grades accordingly
    if request.user.user_type == 'teacher':
        grades = Grade.objects.filter(
            Q(student__in=students, quiz__course=course) |
            Q(student__in=students, assignment__course=course)
        )
    else:  # Assuming the only other user type is 'student'
        grades = Grade.objects.filter(
            Q(quiz__course=course) | Q(assignment__course=course),
            student=request.user
        )

    return render(
        request,
        'courses/course_detail.html',
        {
            'course': course,
            'students': students,
            'assignments': assignments,
            'grades': grades,
        }
    )


@login_required
def enroll_student(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            # Create an Enrollment record
            Enrollment.objects.create(student=student, course=course)
            # Also update the ManyToMany relationship on the Course model
            course.students.add(student)
            return redirect('courses:course_detail', pk=course_id)
    else:
        form = EnrollmentForm()
    return render(request, 'courses/enroll_student.html', {'form': form, 'course': course})




@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'courses/my_courses.html', {'enrollments': enrollments})