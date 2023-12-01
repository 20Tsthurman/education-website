# students/views.py
from datetime import datetime
import json
from django.http import JsonResponse
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
from teachers.utils import score_to_letter_grade

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

from decimal import Decimal, getcontext

# Set the precision for Decimal operations if necessary
getcontext().prec = 5

# Helper function to calculate percentile
def get_percentile(grades, percentile):
    # Ensure grades are sorted and in Decimal format
    grades = sorted(map(Decimal, grades))
    index = Decimal((len(grades) - 1) * percentile) / 100
    floor_index = int(index)
    ceil_index = min(floor_index + 1, len(grades) - 1)
    
    # When the index is an integer
    if floor_index == ceil_index:
        return grades[floor_index]
    else:
        # Perform the interpolation using Decimal arithmetic
        floor_value = grades[floor_index]
        ceil_value = grades[ceil_index]
        proportion = index - Decimal(floor_index)
        interpolated_value = floor_value + (ceil_value - floor_value) * proportion
        return interpolated_value

@login_required
def view_percentiles(request):
    if not request.user.is_student:
        messages.error(request, "This page is only accessible to students.")
        return redirect('users:dashboard')

    # Determine the course(s) the student is enrolled in
    enrollments = Enrollment.objects.filter(student=request.user)
    courses = [enrollment.course for enrollment in enrollments]

    # Fetch all final grades for all students in those courses
    all_grades_list = list(Attempt.objects.filter(
        quiz__course__in=courses, 
        is_completed=True
    ).values_list('final_grade', flat=True))
    all_grades_list = [grade for grade in all_grades_list if grade is not None]  # filter out None values
    all_grades_decimal = list(map(Decimal, all_grades_list))

    # Calculate the percentiles for the entire class
    class_percentiles = {
        '25th': get_percentile(all_grades_decimal, 25),
        '50th (Median)': get_percentile(all_grades_decimal, 50),
        '75th': get_percentile(all_grades_decimal, 75),
    }

    # Calculate the percentile rank for the logged-in student within the class
    student_highest_grade = Attempt.objects.filter(
        student=request.user,
        is_completed=True
    ).aggregate(Max('final_grade'))['final_grade__max'] or Decimal('0.00')
    student_highest_grade = Decimal(student_highest_grade)
    student_percentile_rank = sum(grade <= student_highest_grade for grade in all_grades_decimal) / len(all_grades_decimal) * 100

    # Get the list of all attempts for the logged-in student
    student_attempts = Attempt.objects.filter(
        student=request.user, 
        is_completed=True
    ).order_by('quiz', '-timestamp')

    # Fetch the subject scores for the logged-in student's completed attempts
    final_grades = list(Attempt.objects.filter(
        student=request.user, 
        is_completed=True
    ).values_list('final_grade', flat=True))
    final_grades = [float(grade) for grade in final_grades if grade is not None]  # Convert to float and filter out None

    # Prepare context with all data
    context = {
        'class_percentiles': class_percentiles,
        'student_percentile_rank': student_percentile_rank,
        'student_attempts': student_attempts,
        'final_grades': json.dumps(final_grades),
    }

    return render(request, 'students/view_percentiles.html', context)


@login_required
def view_grades(request):
    # Retrieve all quizzes that the student has attempted
    attempted_quizzes = Quiz.objects.filter(attempt__student=request.user).distinct()

    quizzes_with_grades = []

    for quiz in attempted_quizzes:
        best_attempt = Attempt.objects.filter(student=request.user, quiz=quiz).order_by('-final_grade').first()

        if best_attempt:
            weighted_score = best_attempt.final_grade * quiz.weight
            letter_grade = score_to_letter_grade(weighted_score)

            quizzes_with_grades.append({
                'quiz': quiz,
                'highest_grade': best_attempt.final_grade,
                'weighted_score': weighted_score,
                'letter_grade': letter_grade,
                'attempts': Attempt.objects.filter(student=request.user, quiz=quiz)
        })

    return render(request, 'students/view_grades.html', {'quizzes_with_grades': quizzes_with_grades})

@login_required
def view_course_grades(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    quizzes = Quiz.objects.filter(course=course)

    total_weighted_score = 0
    total_weight = 0
    quizzes_with_grades = []

    for quiz in quizzes:
        attempts = Attempt.objects.filter(student=request.user, quiz=quiz).order_by('-final_grade')
        highest_grade = attempts.first().final_grade if attempts.exists() else None

        if highest_grade is not None:
            weighted_score = highest_grade * quiz.weight / 100
            total_weighted_score += weighted_score
            total_weight += quiz.weight

            quizzes_with_grades.append({
                'quiz': quiz,
                'attempts': attempts,
                'highest_grade': highest_grade,
                'weighted_score': weighted_score
            })

    final_grade = None
    letter_grade = None
    if total_weight > 0:
        final_grade = round((total_weighted_score / total_weight) * 100, 2)  # Multiply by 100 to convert to percentage
        letter_grade = score_to_letter_grade(final_grade)

    return render(request, 'students/course_grades.html', {
        'course': course, 
        'quizzes_with_grades': quizzes_with_grades,
        'final_grade': final_grade,
        'letter_grade': letter_grade
    })


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

@login_required
def calculate_student_final_grade(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    student = request.user.student

    total_weighted_score = 0
    total_weight = 0

    for quiz in course.quizzes.all():
        best_attempt = Attempt.objects.filter(student=student, quiz=quiz).order_by('-final_grade').first()
        if best_attempt and best_attempt.final_grade is not None:
            weighted_score = best_attempt.final_grade * quiz.weight / 100
            total_weighted_score += weighted_score
            total_weight += quiz.weight

    if total_weight > 0:
        final_grade = total_weighted_score / total_weight
        return JsonResponse({'final_grade': final_grade})
    else:
        return JsonResponse({'final_grade': None})

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


