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
    context = {'course': course}

    if hasattr(request.user, 'teacher'):
        # Teacher's view
        # Fetch enrolled students for the course
        enrollments = course.enrollments.all()
        students = [enrollment.student for enrollment in enrollments]

        students_attempts = {}
        quizzes = course.quizzes.all()

        for quiz in quizzes:
            attempts = Attempt.objects.filter(quiz=quiz).select_related('student').order_by('student', '-timestamp')
            
            for attempt in attempts:
                student_email = attempt.student.email
                if student_email not in students_attempts:
                    students_attempts[student_email] = {}

                if quiz.title not in students_attempts[student_email]:
                    students_attempts[student_email][quiz.title] = []

                # Limit to latest three attempts
                if len(students_attempts[student_email][quiz.title]) < 3:
                    students_attempts[student_email][quiz.title].append(attempt)

        # Update context with both the student roster and the attempts
        context.update({
            'students': students,
            'students_attempts': students_attempts
        })

    elif hasattr(request.user, 'student'):
        student = request.user.student

        # Fetch best grades for quizzes in this course
        best_quiz_grades = Grade.objects.filter(
            attempt__quiz__course=course,
            attempt__student=student
        ).values(
            'attempt__quiz__title'
        ).annotate(
            best_grade=Max('grade')
        ).order_by('attempt__quiz__title')

        # Fetch best grades for assignments in this course
        best_assignment_grades = Grade.objects.filter(
            attempt__assignment__course=course,
            attempt__student=student
        ).values(
            'attempt__assignment__title'
        ).annotate(
            best_grade=Max('grade')
        ).order_by('attempt__assignment__title')

        context.update({
            'best_quiz_grades': best_quiz_grades,
            'best_assignment_grades': best_assignment_grades,
        })

    # Common context data for both teachers and students
    lessons = course.lesson_set.all()
    context['lessons'] = lessons

    return render(request, 'courses/course_detail.html', context)


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

