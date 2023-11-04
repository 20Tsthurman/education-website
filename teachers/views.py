from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from courses.models import Course, Enrollment, Lesson
from courses.forms import LessonForm
from django.contrib.auth.decorators import login_required
from teachers.models import Teacher
from .forms import ChoiceFormSet, TeacherEnrollmentForm
from teachers.forms import CourseSelectionForm, EnrollmentForm
from .models import Question
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
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not hasattr(request.user, 'teacher') or request.user.teacher != course.teacher:
        return redirect('some_error_page')  # Replace with your error page
    
    enrollments = Enrollment.objects.filter(course=course)
    students = [enrollment.student for enrollment in enrollments]
    grades = Grade.objects.filter(Q(quiz__course=course) | Q(assignment__course=course))
    
    return render(
        request,
        'courses/course_detail.html',
        {
            'course': course,
            'students': students,
            'grades': grades
        }
    )

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

    grades = Grade.objects.filter(teacher=request.user.teacher)
    quizzes = Quiz.objects.filter(teacher=request.user.teacher)
    assignments = Assignment.objects.filter(teacher=request.user.teacher)
    
    return render(
        request,
        'teachers/gradebook.html',
        {'grades': grades, 'quizzes': quizzes, 'assignments': assignments}
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
        choice_formset = ChoiceFormSet(request.POST, prefix='choices')
        if question_form.is_valid() and choice_formset.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()
            for choice_form in choice_formset:
                choice = choice_form.save(commit=False)
                choice.question = question
                choice.save()
            return redirect('teachers:quiz_detail', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()
        choice_formset = ChoiceFormSet(prefix='choices')
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