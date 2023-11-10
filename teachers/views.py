from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from courses.models import Course, Enrollment, Lesson
from courses.forms import LessonForm
from django.contrib.auth.decorators import login_required
from teachers.models import Teacher
from django.contrib.auth.models import User
from .forms import ChoiceFormSet
from teachers.forms import CourseSelectionForm, EnrollmentForm
from .models import Attempt, Question
from .forms import QuizForm 
from .forms import QuestionForm
from django.db import transaction
from teachers.models import Grade, Quiz, Assignment
from django.db.models import Q


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


@login_required
def gradebook(request):
    if not hasattr(request.user, 'teacher'):
        return redirect('some_error_page')  # Replace with your error page

    teacher = request.user.teacher
    # Fetch all courses taught by the teacher
    courses = Course.objects.filter(teacher=teacher)
    
    # Prepare a list to hold all student grades data
    student_grades = []

    # Iterate over each course to fetch enrolled students and their grades
    for course in courses:
        enrollments = Enrollment.objects.filter(course=course)
        for enrollment in enrollments:
            student = enrollment.student
            # Fetch grades for quizzes and assignments for each student
            quiz_grades = Grade.objects.filter(attempt__quiz__course=course, attempt__student=student)
            assignment_grades = Grade.objects.filter(assignment__course=course, assignment__students=student)
            
            # Append the student and their grades to the student_grades list
            student_grades.append({
                'student': student,
                'quiz_grades': quiz_grades,
                'assignment_grades': assignment_grades
            })

    # Pass the student_grades list to the template
    return render(
        request,
        'teachers/gradebook.html',
        {'student_grades': student_grades}
    )


@login_required
@transaction.atomic
def create_quiz(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if not hasattr(request.user, 'teacher'):
        return redirect('some_error_page')

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.teacher = request.user.teacher
            quiz.course = course
            quiz.save()
            return redirect(quiz.get_absolute_url())
        else:
            messages.error(request, 'There was an error in the form. Please correct it and try again.')
            return render(request, 'teachers/create_quiz.html', {'form': form, 'course': course})
    else:
        form = QuizForm()
        return render(request, 'teachers/create_quiz.html', {'form': form, 'course': course})

@login_required
def create_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if quiz.teacher != request.user.teacher:
        return HttpResponseForbidden("You don't have permission to access this page.")
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            choice_formset = ChoiceFormSet(request.POST, instance=question)  # updated reference
            if choice_formset.is_valid():
                choice_formset.save()
                return redirect('teachers:quiz_detail', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()
        choice_formset = ChoiceFormSet(instance=Question())  # updated reference
    return render(
        request,
        'teachers/create_question.html',
        {'question_form': question_form, 'choice_formset': choice_formset, 'quiz': quiz}
    )


@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if quiz.teacher != request.user.teacher:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('teachers:quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'teachers/edit_quiz.html', {'form': form, 'quiz': quiz})

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if quiz.teacher != request.user.teacher:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    if request.method == 'POST':
        quiz.delete()
        return redirect('teachers:teacher_dashboard')

    return render(request, 'teachers/delete_quiz_confirm.html', {'quiz': quiz})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if quiz.teacher != request.user.teacher:
        return HttpResponseForbidden("You don't have permission to access this page.")

    questions = Question.objects.filter(quiz=quiz)
    return render(request, 'teachers/quiz_detail.html', {'quiz': quiz, 'questions': questions})