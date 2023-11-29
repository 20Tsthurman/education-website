# students/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from courses.models import Lesson
from teachers.models import Attempt, Grade, Quiz
from .forms import AnswerForm
from django.contrib import messages
from django.db.models import Avg
from django.utils import timezone
from django.db.models import Max, Q

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
    # Retrieve all quizzes that the student has attempted
    attempted_quizzes = Quiz.objects.filter(attempt__student=request.user).distinct()

    # Prepare a list to hold the best grade for each quiz
    best_grades = []

    for quiz in attempted_quizzes:
        # Get the best grade for the current quiz
        best_grade = Attempt.objects.filter(student=request.user, quiz=quiz).order_by('-final_grade').first()

        if best_grade:
            best_grades.append({
                'quiz_title': quiz.title,
                'final_grade': best_grade.final_grade
            })

    return render(request, 'students/view_grades.html', {'best_grades': best_grades})


@login_required
def view_course_grades(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    quizzes = Quiz.objects.filter(course=course)

    quizzes_with_grades = []
    for quiz in quizzes:
        attempts = Attempt.objects.filter(student=request.user, quiz=quiz).order_by('-final_grade')
        highest_grade = attempts.first().final_grade if attempts.exists() else None
        quizzes_with_grades.append({
            'quiz': quiz,
            'attempts': attempts,
            'highest_grade': highest_grade
        })

    return render(request, 'students/course_grades.html', {'course': course, 'quizzes_with_grades': quizzes_with_grades})

@login_required
def take_quiz(request, quiz_id, question_number):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.question_set.all()
    total_questions = questions.count()

    # Get the current or latest attempt for the student
    attempt = Attempt.objects.filter(student=request.user, quiz=quiz).order_by('-attempt_number').first()

    # If no attempt exists or the latest is marked as completed, start a new one
    if not attempt or attempt.is_completed:
        attempt_number = 1 if not attempt else attempt.attempt_number + 1
        attempt = Attempt.objects.create(
            student=request.user,
            quiz=quiz,
            attempt_number=attempt_number,
            is_completed=False  # This needs to be added to the Attempt model
        )
    else:
        # Increment the attempt number for a new attempt, if not completed
        if attempt.attempt_number > 3:
            messages.error(request, "You have reached the maximum number of attempts for this quiz.")
            return redirect('students:quiz_results', quiz_id=quiz_id)

    # Proceed with quiz taking
    question = questions[question_number - 1]
    form = AnswerForm(question=question)

    if request.method == 'POST':
        form = AnswerForm(request.POST, question=question)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            Grade.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={'grade': 100 if choice.is_correct else 0}
            )
            next_question_number = question_number + 1
            
            # Check if it's the last question and mark the attempt as completed
            if next_question_number > total_questions:
                calculate_and_save_final_grade(attempt)
                attempt.is_completed = True
                attempt.completed_timestamp = timezone.now()
                attempt.save()
                return redirect('students:quiz_results', quiz_id=quiz_id)
            else:
                return redirect('students:take_quiz', quiz_id=quiz_id, question_number=next_question_number)

    context = {
        'quiz': quiz,
        'question': question,
        'form': form,
        'question_number': question_number,
        'total_questions': total_questions,
        'current_attempt_number': attempt.attempt_number,
    }
    return render(request, 'students/take_quiz.html', context)

def calculate_and_save_final_grade(attempt):
    # Calculate the final grade based on the correct answers
    correct_answers_count = Grade.objects.filter(attempt=attempt, grade=100).count()
    total_questions = attempt.quiz.question_set.count()
    final_grade = (correct_answers_count / total_questions) * 100
    attempt.final_grade = final_grade
    attempt.save()



def course_quizzes(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    quizzes = Quiz.objects.filter(course=course)
    return render(request, 'students/course_quizzes.html', {'course': course, 'quizzes': quizzes})

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = Attempt.objects.filter(quiz=quiz, student=request.user).order_by('-attempt_number')

    # Check if there are any attempts made by the student for the quiz
    if not attempts:
        messages.error(request, "No attempts found for this quiz.")
        return redirect('some_error_handling_view')

    # Get all attempt numbers for this student and this quiz
    attempt_numbers = attempts.values_list('attempt_number', flat=True).distinct()

    # Get the latest attempt's grades
    latest_attempt_number = attempt_numbers.first()
    grades = Grade.objects.filter(attempt__quiz=quiz, attempt__student=request.user, attempt__attempt_number=latest_attempt_number)

    # Calculate the remaining attempts
    remaining_attempts = 3 - attempt_numbers.count()

    # Calculate average scores for each attempt
    average_scores = {}
    for attempt_number in attempt_numbers:
        grades_for_attempt = Grade.objects.filter(
            attempt__quiz=quiz, 
            attempt__student=request.user, 
            attempt__attempt_number=attempt_number
        )
        average_score = grades_for_attempt.aggregate(Avg('grade'))['grade__avg']
        average_scores[attempt_number] = average_score

    context = {
        'quiz': quiz,
        'grades': grades,
        'remaining_attempts': remaining_attempts,
        'average_scores': average_scores,
        'attempt_numbers': list(attempt_numbers),
        'latest_attempt_number': latest_attempt_number,
    }
    return render(request, 'students/quiz_results.html', context)



def calculate_average_scores(grades_queryset):
    average_scores = {}
    for attempt_number in grades_queryset.values_list('attempt_number', flat=True).distinct():
        grades = grades_queryset.filter(attempt_number=attempt_number)
        total_score = sum(grade.grade for grade in grades)
        average_score = total_score / len(grades) if grades else 0
        average_scores[attempt_number] = round(average_score, 2)
    return average_scores


def get_average_score(request, quiz_id, attempt_number):
    # Get the quiz object
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    # Assume grades is a queryset of Grade objects for a particular attempt
    grades = Grade.objects.filter(student=request.user, quiz=quiz, attempt_number=attempt_number)
    # Call the calculate_average_scores function (corrected the function name)
    average_scores = calculate_average_scores(grades)
    # Assuming you want the average score for the specific attempt
    average_score = average_scores.get(attempt_number, 0)
    return average_score

@login_required
def review_test(request, quiz_id, attempt_number):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(Attempt, quiz=quiz, student=request.user, attempt_number=attempt_number)
    grades = Grade.objects.filter(attempt=attempt)

    return render(
        request,
        'students/review_test.html',
        {
            'quiz': quiz,
            'grades': grades,
            'attempt_number': attempt_number,
        }
    )


