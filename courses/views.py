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
from teachers.models import Grade, Attempt
from django.db.models import Q
from django.db.models import Max

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

    if request.user.user_type == 'teacher':
    # For teachers, fetch the best grades for each quiz and assignment for each student
        best_grades = Grade.objects.filter(
        attempt__quiz__course=course
        ).values(
        'attempt__student__email', 'attempt__quiz__title'
     ).annotate(
        best_grade=Max('grade')
     ).order_by('attempt__student__email', 'attempt__quiz__title')
    elif request.user.user_type == 'student':
        # For students, fetch the best grade for each quiz and assignment in the course
        best_grades = Grade.objects.filter(
            attempt__quiz__course=course,
            attempt__student=request.user
        ).values(
            'attempt__quiz__title'
        ).annotate(
            best_grade=Max('grade')
        ).order_by('attempt__quiz__title')
    else:
        # Handle other user types if necessary or set best_grades to None
        best_grades = None

    return render(
        request,
        'courses/course_detail.html',
         {
             'course': course,
             'students': students,
             'assignments': assignments,
             'best_grades': best_grades,  # Include this in the context
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
    # Check if the user is a teacher
    if hasattr(request.user, 'teacher_profile'):  # Assuming teacher profile is linked to user
        # Get courses where the user is the teacher
        courses_taught = Course.objects.filter(teacher=request.user)
        # You can pass 'courses_taught' directly or make it part of 'enrollments'
        return render(request, 'courses/my_courses.html', {'courses_taught': courses_taught})
    else:
        # Otherwise, assume the user is a student
        enrollments = Enrollment.objects.filter(student=request.user)
        return render(request, 'courses/my_courses.html', {'enrollments': enrollments})

