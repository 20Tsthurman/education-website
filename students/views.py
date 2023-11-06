# students/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course, Enrollment
from courses.models import Lesson
from teachers.models import Attempt, Grade, Quiz
from .forms import AnswerForm
from django.contrib import messages
from django.db.models import Avg
from django.db.models import Max

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
    best_quizzes = Grade.objects.filter(student=request.user, quiz__isnull=False)\
                                .values('quiz__title')\
                                .annotate(best_grade=Max('grade'))\
                                .order_by('quiz')

    best_assignments = Grade.objects.filter(student=request.user, assignment__isnull=False)\
                                    .values('assignment__title')\
                                    .annotate(best_grade=Max('grade'))\
                                    .order_by('assignment')

    # Combine the two querysets into one
    best_grades = list(best_quizzes) + list(best_assignments)

    return render(
        request,
        'students/view_grades.html',
        {'best_grades': best_grades}
    )


@login_required
def take_quiz(request, quiz_id, question_number):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.question_set.all()
    total_questions = questions.count()
    teacher = quiz.teacher

    # Get the current attempt number or initialize it
    current_attempts = Attempt.objects.filter(student=request.user, quiz=quiz).count()
    if 'current_attempt_number' not in request.session:
        request.session['current_attempt_number'] = current_attempts + 1
    attempt_number = request.session['current_attempt_number']

    # Check if max attempts have been reached and redirect if so
    if current_attempts >= 3:
        messages.error(request, "You have reached the maximum number of attempts for this quiz.")
        return redirect('students:quiz_results', quiz_id=quiz_id)

    if question_number > total_questions:
    # Calculate final grade based on correct answers
        correct_answers = Grade.objects.filter(
            attempt__quiz=quiz, 
            attempt__student=request.user, 
            attempt__attempt_number=attempt_number, 
            grade=100
        ).count()
        final_grade_percentage = (correct_answers / total_questions) * 100

    # Retrieve the attempt instance
        attempt = Attempt.objects.get(
            student=request.user, 
            quiz=quiz, 
            attempt_number=attempt_number
         )
    # Update the final grade for the attempt
        attempt.final_grade = final_grade_percentage
        attempt.save()

    # Reset attempt count after finishing the quiz
        del request.session['current_attempt_number']
        return redirect('students:quiz_results', quiz_id=quiz_id)

    question = questions[question_number - 1]
    form = AnswerForm(question=question)  # Initialize form here for GET requests

    # Create or get attempt outside the POST check to avoid UnboundLocalError
    attempt, created = Attempt.objects.get_or_create(
        student=request.user,
        quiz=quiz,
        attempt_number=attempt_number
    )

    if request.method == 'POST':
        form = AnswerForm(request.POST, question=question)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            # Create a Grade instance for the current attempt and question
            Grade.objects.create(
                attempt=attempt,
                assignment=None,  # Assuming this is a quiz, not an assignment
                grade=100 if choice.is_correct else 0,
                teacher=teacher
            )

            next_question_number = question_number + 1
            if next_question_number > total_questions:
                # Redirect to process the final grade calculation
                return redirect('students:take_quiz', quiz_id=quiz_id, question_number=question_number+1)
            else:
                # Move to the next question
                return redirect('students:take_quiz', quiz_id=quiz_id, question_number=next_question_number)
    else:
        # GET request or form is not valid
        form = AnswerForm(question=question)

    context = {
        'quiz': quiz,
        'question': question,
        'form': form,
        'question_number': question_number,
        'total_questions': total_questions,
        'current_attempt_number': attempt_number,
    }
    return render(request, 'students/take_quiz.html', context)



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


