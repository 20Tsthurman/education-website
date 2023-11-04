# students/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from courses.models import Lesson
from teachers.models import Grade, Quiz
from .forms import AnswerForm
from django.contrib import messages

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

@login_required
def view_grades(request):
    grades = Grade.objects.filter(student=request.user)
    return render(
        request,
        'students/view_grades.html',
        {'grades': grades}
    )

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        correct_answers = 0
        total_questions = quiz.question_set.count()
        for question in quiz.question_set.all():
            answer_form = AnswerForm(request.POST, prefix=str(question.id), question=question)
            if answer_form.is_valid():
                choice = answer_form.cleaned_data['choice']
                if choice.is_correct:
                    correct_answers += 1
        grade_value = (correct_answers / total_questions) * 100  # Assuming grades are out of 100

        # Determine the next attempt number
        previous_attempts = Grade.objects.filter(student=request.user, quiz=quiz).count()
        if previous_attempts < 3:
            attempt_number = previous_attempts + 1
            # Create and save the Grade
            grade_record = Grade(student=request.user, quiz=quiz, teacher=quiz.teacher, grade=grade_value, attempt_number=attempt_number)
            grade_record.save()
        else:
            messages.error(request, "You have already attempted this quiz 3 times.")
            return redirect('students:quiz_results', quiz_id=quiz.id)

        return redirect('students:quiz_results', quiz_id=quiz.id)
    else:
        form_question_pairs = [
            (question, AnswerForm(question=question, prefix=str(question.id)))
            for question in quiz.question_set.all()
        ]
    return render(
        request,
        'students/take_quiz.html',
        {'quiz': quiz, 'form_question_pairs': form_question_pairs}
    )

def course_quizzes(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    quizzes = Quiz.objects.filter(course=course)
    return render(request, 'students/course_quizzes.html', {'course': course, 'quizzes': quizzes})

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    grades = Grade.objects.filter(quiz=quiz, student=request.user)
    remaining_attempts = 3 - grades.count()
    return render(
        request,
        'students/quiz_results.html',
        {'quiz': quiz, 'grades': grades, 'remaining_attempts': remaining_attempts}
    )

