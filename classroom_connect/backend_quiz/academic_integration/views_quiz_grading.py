from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Avg, Sum, F, Q, Case, When, Value, IntegerField
import logging

from quiz.models import Quiz, QuizAttempt, QuizAnswer, Question, Choice

logger = logging.getLogger(__name__)


def quiz_student_performance(request: HttpRequest, quiz_id: int) -> HttpResponse:
    """
    View for staff to see all student attempts on a specific quiz
    and their performance statistics.
    """
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    if not staff_email:
        messages.info(request, "Please log in to continue.")
        return redirect("academic_integration:staff_login")
    
    # Get the quiz
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Verify staff has access to this quiz
    has_access = False
    
    # Check if staff created the quiz
    if quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email):
        has_access = True
    
    # If access denied, redirect to dashboard
    if not has_access:
        messages.error(request, "You don't have permission to view this quiz's performance data.")
        return redirect("academic_integration:admin_quiz_dashboard")
    
    # Get all completed attempts for this quiz
    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        completed_at__isnull=False
    ).select_related('user').order_by('-completed_at')
    
    # Calculate performance metrics
    total_attempts = attempts.count()
    if total_attempts > 0:
        avg_score = sum(a.percentage for a in attempts) / total_attempts
        passing_count = sum(1 for a in attempts if a.percentage >= quiz.passing_score)
        passing_rate = (passing_count / total_attempts) * 100 if total_attempts > 0 else 0
    else:
        avg_score = 0
        passing_rate = 0
        passing_count = 0
    
    # Count attempts that need grading (status='submitted')
    needs_grading_count = attempts.filter(status='submitted').count()
    
    context = {
        'quiz': quiz,
        'attempts': attempts,
        'total_attempts': total_attempts,
        'avg_score': avg_score,
        'passing_rate': passing_rate,
        'passing_count': passing_count,
        'needs_grading_count': needs_grading_count,
        'staff_email': staff_email,
        'staff_name': request.session.get('staff_name', staff_email),
    }
    
    return render(request, "academic_integration/quiz_student_performance.html", context)


def grade_quiz_attempt(request: HttpRequest, attempt_id: int) -> HttpResponse:
    """
    View for staff to grade a specific quiz attempt, particularly for 
    text-based questions that require manual grading.
    """
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    if not staff_email:
        messages.info(request, "Please log in to continue.")
        return redirect("academic_integration:staff_login")
    
    # Get the quiz attempt
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id)
    quiz = attempt.quiz
    
    # Verify staff has access to this quiz
    has_access = False
    
    # Check if staff created the quiz
    if quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email):
        has_access = True
    
    # If access denied, redirect to dashboard
    if not has_access:
        messages.error(request, "You don't have permission to grade this quiz attempt.")
        return redirect("academic_integration:admin_quiz_dashboard")
    
    # Get all answers for this attempt that need manual grading (primarily text questions)
    answers_to_grade = attempt.answers.filter(question__question_type='text').order_by('question__order')
    
    # If no text questions but attempt status is 'submitted', include all answers for review
    if not answers_to_grade.exists() and attempt.status == 'submitted':
        answers_to_grade = attempt.answers.all().order_by('question__order')
    
    # Process form submission
    if request.method == 'POST':
        try:
            total_points = 0
            earned_points = 0
            
            # Process each answer
            for answer in answers_to_grade:
                # Get form data for this answer
                points_key = f"points_{answer.id}"
                feedback_key = f"feedback_{answer.id}"
                correct_key = f"correct_{answer.id}"
                
                # Update answer with grading information
                if points_key in request.POST:
                    points = min(int(request.POST.get(points_key, 0)), answer.question.points)
                    answer.points_earned = points
                
                if feedback_key in request.POST:
                    answer.feedback = request.POST.get(feedback_key)
                
                # Update correctness flag
                answer.is_correct = correct_key in request.POST
                
                # Save the answer
                answer.save()
                
                # Add to totals
                total_points += answer.question.points
                earned_points += answer.points_earned
            
            # Recalculate attempt score
            all_answers = attempt.answers.all()
            attempt_total_points = sum(a.question.points for a in all_answers)
            attempt_earned_points = sum(a.points_earned for a in all_answers)
            attempt.score = attempt_earned_points
            attempt.total_points = attempt_total_points
            
            # Calculate percentage
            if attempt_total_points > 0:
                attempt.percentage = (attempt_earned_points / attempt_total_points) * 100
            else:
                attempt.percentage = 0
            
            # Update passed status
            attempt.passed = attempt.percentage >= quiz.passing_score
            
            # Mark as graded
            attempt.status = 'graded'
            attempt.graded_by = quiz.created_by  # Assuming the created_by user is the staff grading
            attempt.save()
            
            messages.success(request, "Quiz attempt graded successfully!")
            return redirect('academic_integration:quiz_student_performance', quiz_id=quiz.id)
            
        except Exception as e:
            logger.exception(f"Error grading quiz attempt: {e}")
            messages.error(request, f"An error occurred while grading: {str(e)}")
    
    context = {
        'attempt': attempt,
        'answers_to_grade': answers_to_grade,
        'staff_email': staff_email,
        'staff_name': request.session.get('staff_name', staff_email),
    }
    
    return render(request, "academic_integration/grade_quiz_attempt.html", context)


def update_attempt_feedback(request: HttpRequest, attempt_id: int) -> HttpResponse:
    """
    View for staff to update overall feedback for a quiz attempt.
    """
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    if not staff_email:
        messages.info(request, "Please log in to continue.")
        return redirect("academic_integration:staff_login")
    
    # Get the quiz attempt
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id)
    quiz = attempt.quiz
    
    # Verify staff has access to this quiz
    has_access = False
    
    # Check if staff created the quiz
    if quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email):
        has_access = True
    
    # If access denied, redirect to dashboard
    if not has_access:
        messages.error(request, "You don't have permission to update feedback for this quiz attempt.")
        return redirect("academic_integration:admin_quiz_dashboard")
    
    # Process form submission
    if request.method == 'POST':
        try:
            # Update attempt feedback
            attempt.feedback = request.POST.get('feedback', '')
            attempt.save()
            
            messages.success(request, "Feedback updated successfully!")
        except Exception as e:
            logger.exception(f"Error updating feedback: {e}")
            messages.error(request, f"An error occurred while updating feedback: {str(e)}")
    
    # Redirect back to grading page
    return redirect('academic_integration:grade_quiz_attempt', attempt_id=attempt_id)


def quiz_answer_analysis(request: HttpRequest, quiz_id: int) -> HttpResponse:
    """
    View for staff to analyze answers to a specific quiz across all students.
    This view shows detailed statistics about each question, including:
    - How many students got it correct/incorrect
    - For MCQ questions: Distribution of answers across choices
    - For text questions: Samples of answers and grading patterns
    """
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    if not staff_email:
        messages.info(request, "Please log in to continue.")
        return redirect("academic_integration:staff_login")
    
    # Get the quiz
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Verify staff has access to this quiz
    has_access = False
    
    # Check if staff created the quiz
    if quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email):
        has_access = True
    
    # If access denied, redirect to dashboard
    if not has_access:
        messages.error(request, "You don't have permission to view this quiz's answer analysis.")
        return redirect("academic_integration:admin_quiz_dashboard")
    
    # Get completed attempts for this quiz
    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        completed_at__isnull=False
    )
    
    # Get all questions for this quiz
    questions = Question.objects.filter(quiz=quiz).order_by('order')
    
    # Initialize analysis data structure
    question_analysis = []
    
    for question in questions:
        # Get all answers for this question across all attempts
        answers = QuizAnswer.objects.filter(
            question=question,
            attempt__in=attempts
        ).select_related('attempt', 'attempt__user')
        
        # Calculate basic statistics
        total_answers = answers.count()
        correct_answers = answers.filter(is_correct=True).count()
        
        if total_answers > 0:
            correct_percentage = (correct_answers / total_answers) * 100
        else:
            correct_percentage = 0
        
        # Prepare analysis object based on question type
        analysis = {
            'question': question,
            'total_answers': total_answers,
            'correct_answers': correct_answers,
            'correct_percentage': correct_percentage,
            'avg_points': answers.aggregate(avg=Avg('points_earned'))['avg'] or 0,
        }
        
        # Add question type specific analysis
        if question.question_type in ['mcq_single', 'mcq_multiple']:
            # For MCQ questions, analyze choice distribution
            choices = Choice.objects.filter(question=question)
            choice_analysis = []
            
            for choice in choices:
                # Count how many times this choice was selected
                if question.question_type == 'mcq_single':
                    selection_count = answers.filter(selected_choices=choice).count()
                else:
                    # For multiple choice, we need to count differently
                    selection_count = answers.filter(selected_choices=choice).count()
                
                # Calculate percentage
                if total_answers > 0:
                    selection_percentage = (selection_count / total_answers) * 100
                else:
                    selection_percentage = 0
                    
                choice_analysis.append({
                    'choice': choice,
                    'selection_count': selection_count,
                    'selection_percentage': selection_percentage
                })
                
            analysis['choices'] = choice_analysis
            
        elif question.question_type == 'text':
            # For text questions, include sample answers
            # Get some graded correct answers as examples
            correct_samples = answers.filter(
                is_correct=True
            ).order_by('-points_earned')[:3]
            
            # Get some graded incorrect answers as examples
            incorrect_samples = answers.filter(
                is_correct=False
            ).order_by('points_earned')[:3]
            
            # Get answers needing grading (if any)
            needs_grading = answers.filter(
                points_earned=0,
                text_answer__isnull=False,
                is_correct=False,
                attempt__status='submitted'
            )[:5]
            
            analysis['correct_samples'] = correct_samples
            analysis['incorrect_samples'] = incorrect_samples
            analysis['needs_grading'] = needs_grading
            analysis['text_answers'] = answers.exclude(text_answer__isnull=True).exclude(text_answer='')
            
        elif question.question_type == 'true_false':
            # For true/false questions, count true vs false responses
            true_count = answers.filter(boolean_answer=True).count()
            false_count = answers.filter(boolean_answer=False).count()
            
            if total_answers > 0:
                true_percentage = (true_count / total_answers) * 100
                false_percentage = (false_count / total_answers) * 100
            else:
                true_percentage = false_percentage = 0
                
            analysis['true_count'] = true_count
            analysis['false_count'] = false_count
            analysis['true_percentage'] = true_percentage
            analysis['false_percentage'] = false_percentage
            
        question_analysis.append(analysis)
    
    # Calculate quiz-level statistics
    total_attempts = attempts.count()
    if total_attempts > 0:
        avg_score = attempts.aggregate(avg=Avg('percentage'))['avg']
        passing_count = attempts.filter(percentage__gte=quiz.passing_score).count()
        passing_rate = (passing_count / total_attempts) * 100
    else:
        avg_score = 0
        passing_count = 0
        passing_rate = 0
    
    context = {
        'quiz': quiz,
        'question_analysis': question_analysis,
        'total_attempts': total_attempts,
        'avg_score': avg_score,
        'passing_count': passing_count,
        'passing_rate': passing_rate,
        'staff_email': staff_email,
        'staff_name': request.session.get('staff_name', staff_email),
    }
    
    return render(request, "academic_integration/quiz_answer_analysis.html", context)