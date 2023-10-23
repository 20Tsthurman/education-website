# students/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from courses.models import Lesson
from teachers.models import Grade, Quiz
from .forms import AnswerForm

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

        # Create and save the Grade
        grade_record = Grade(student=request.user, quiz=quiz, teacher=quiz.teacher, grade=grade_value)
        grade_record.save()

        return redirect('students:quiz_results', quiz_id=quiz.id)
    else:
        forms = [
            AnswerForm(question=question, prefix=str(question.id))
            for question in quiz.question_set.all()
        ]
    return render(
        request,
        'students/take_quiz.html',
        {'quiz': quiz, 'forms': forms}
    )

def course_quizzes(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    quizzes = Quiz.objects.filter(course=course)
    return render(request, 'students/course_quizzes.html', {'course': course, 'quizzes': quizzes})

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    grade = get_object_or_404(Grade, quiz=quiz, student=request.user)
    return render(
        request,
        'students/quiz_results.html',
        {'quiz': quiz, 'grade': grade}
    )