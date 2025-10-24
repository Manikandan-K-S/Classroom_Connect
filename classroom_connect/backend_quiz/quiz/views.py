from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, Question, Choice, QuizAttempt, User
from .serializers import QuizSerializer, QuizAttemptSerializer
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Prefetch, Count, Avg, Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
import json
import requests

def _api_base_url():
    """Return the Academic Analyzer API base URL"""
    from django.conf import settings
    base_url = getattr(settings, "ACADEMIC_ANALYZER_BASE_URL", "http://localhost:5000")
    return base_url.rstrip("/")

def get_student_courses(rollno):
    """Get a list of course IDs the student is enrolled in from Academic Analyzer"""
    try:
        response = requests.get(
            f"{_api_base_url()}/student/dashboard",
            params={"rollno": rollno},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if data.get('success'):
                return [course['courseId'] for course in data.get('courses', [])]
    except requests.RequestException:
        pass
    return []

def get_teacher_courses(email):
    """Get a list of course IDs the teacher is handling from Academic Analyzer"""
    try:
        response = requests.get(
            f"{_api_base_url()}/staff/dashboard",
            params={"email": email},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if data.get('success'):
                return [course['courseId'] for course in data.get('courses', [])]
    except requests.RequestException:
        pass
    return []

# GET list of all quizzes with filtering based on user role and enrollment
@api_view(["GET"])
def quiz_list(request):
    user_role = request.query_params.get('role', 'student')
    course_id = request.query_params.get('course_id')
    tutorial_number = request.query_params.get('tutorial_number')
    quiz_type = request.query_params.get('quiz_type')
    
    # Start with all quizzes and filter down
    quizzes = Quiz.objects.all()
    
    # Filter by course if specified
    if course_id:
        quizzes = quizzes.filter(course_id=course_id)
    
    # Filter by tutorial if specified
    if tutorial_number:
        quizzes = quizzes.filter(tutorial_number=tutorial_number)
    
    # Filter by quiz type if specified
    if quiz_type:
        if quiz_type == 'mock':
            # Either marked as mock or has no tutorial number
            quizzes = quizzes.filter(Q(quiz_type='mock') | Q(tutorial_number__isnull=True))
        else:
            quizzes = quizzes.filter(quiz_type=quiz_type)
    
    # If student, filter by enrollment
    if user_role == 'student' and 'student_roll_number' in request.session:
        roll_number = request.session['student_roll_number']
        enrolled_courses = get_student_courses(roll_number)
        
        if enrolled_courses:
            # Show quizzes for courses they are enrolled in
            quizzes = quizzes.filter(
                Q(course_id__in=enrolled_courses) | Q(course_id__isnull=True)
            )
        else:
            # If they're not enrolled in any courses, only show quizzes not linked to a course
            quizzes = quizzes.filter(course_id__isnull=True)
            
        # Only show quizzes that are active and within the time frame
        now = timezone.now()
        quizzes = quizzes.filter(
            is_active=True,
            is_ended=False
        ).filter(
            # Either no start date, or start date has passed
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            # Either no end date, or end date is in the future
            Q(complete_by_date__isnull=True) | Q(complete_by_date__gt=now)
        )
    
    # If staff, filter by their courses
    elif user_role == 'admin' and 'staff_email' in request.session:
        staff_email = request.session['staff_email']
        handled_courses = get_teacher_courses(staff_email)
        
        if handled_courses:
            # Show quizzes for courses they handle plus any quizzes they created
            quizzes = quizzes.filter(
                Q(course_id__in=handled_courses) | 
                Q(created_by__email=staff_email) |
                Q(created_by__username=staff_email)
            )
    
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)

# GET single quiz details
@api_view(["GET"])
def quiz_detail(request, pk):
    try:
        quiz = Quiz.objects.get(pk=pk)
        
        # Check if student is enrolled in the course for this quiz
        if request.query_params.get('role') == 'student' and 'student_roll_number' in request.session:
            roll_number = request.session['student_roll_number']
            enrolled_courses = get_student_courses(roll_number)
            
            # If quiz is linked to a course and student isn't enrolled, deny access
            if quiz.course_id and quiz.course_id not in enrolled_courses:
                return Response({"error": "You are not enrolled in this course"}, status=403)
            
            # Check quiz availability
            if not quiz.is_available:
                if quiz.is_ended:
                    return Response({"error": "This quiz has been ended by the teacher"}, status=403)
                if not quiz.is_active:
                    return Response({"error": "This quiz is not active"}, status=403)
                if quiz.start_date and quiz.start_date > timezone.now():
                    return Response({"error": "This quiz hasn't started yet"}, status=403)
                if quiz.complete_by_date and quiz.complete_by_date < timezone.now():
                    return Response({"error": "This quiz has expired"}, status=403)
        
        # Check if staff has access to this quiz
        elif request.query_params.get('role') == 'admin' and 'staff_email' in request.session:
            staff_email = request.session['staff_email']
            handled_courses = get_teacher_courses(staff_email)
            
            # If quiz is linked to a course and staff doesn't handle it, check if they created it
            if quiz.course_id and quiz.course_id not in handled_courses:
                if not (quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email)):
                    return Response({"error": "You don't have access to this quiz"}, status=403)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=404)
    
    serializer = QuizSerializer(quiz)
    return Response(serializer.data)

# GET student's attempt for a quiz or create a new one
# This function is temporarily simplified while we rebuild the models
@api_view(["GET"])
def get_or_create_attempt(request, quiz_id):
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
        
        # Ensure student is logged in
        student_id = request.session.get('student_id')
        student_roll_number = request.session.get('student_roll_number')
        
        if not student_id or not student_roll_number:
            return Response({"error": "You must be logged in as a student"}, status=403)
            
        # Verify enrollment
        enrolled_courses = get_student_courses(student_roll_number)
        if quiz.course_id and quiz.course_id not in enrolled_courses:
            return Response({"error": "You are not enrolled in this course"}, status=403)
        
        # Check quiz availability
        if not quiz.is_available:
            if quiz.is_ended:
                return Response({"error": "This quiz has been ended by the teacher"}, status=403)
            if not quiz.is_active:
                return Response({"error": "This quiz is not active"}, status=403)
            if quiz.start_date and quiz.start_date > timezone.now():
                return Response({"error": "This quiz hasn't started yet"}, status=403)
            if quiz.complete_by_date and quiz.complete_by_date < timezone.now():
                return Response({"error": "This quiz has expired"}, status=403)
        
        # Get or create user
        user, created = User.objects.get_or_create(
            username=student_roll_number,
            defaults={
                'email': f"{student_roll_number}@example.com",
                'role': 'student'
            }
        )
        
        # Get or create attempt
        attempt, created = QuizAttempt.objects.get_or_create(
            user=user,
            quiz=quiz
        )
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)
            
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=404)

# POST quiz result (submit answers)
@api_view(["POST"])
def quiz_result(request):
    try:
        quiz_id = request.data.get('quiz_id')
        answers = request.data.get('answers', {})
        
        if not quiz_id:
            return Response({"error": "Quiz ID is required"}, status=400)
        
        # Get the quiz
        quiz = Quiz.objects.get(pk=quiz_id)
        
        # Ensure student is logged in
        student_id = request.session.get('student_id')
        student_roll_number = request.session.get('student_roll_number')
        
        if not student_id or not student_roll_number:
            return Response({"error": "You must be logged in as a student"}, status=403)
        
        # Verify enrollment
        enrolled_courses = get_student_courses(student_roll_number)
        if quiz.course_id and quiz.course_id not in enrolled_courses:
            return Response({"error": "You are not enrolled in this course"}, status=403)
        
        # Check quiz availability
        if not quiz.is_available:
            return Response({"error": "This quiz is not available"}, status=403)
        
        # Get user
        user, created = User.objects.get_or_create(
            username=student_roll_number,
            defaults={
                'email': f"{student_roll_number}@example.com",
                'role': 'student'
            }
        )
        
        # Process answers
        questions = quiz.questions.all()
        total_questions = questions.count()
        correct_answers = 0
        
        for question in questions:
            question_key = f"question_{question.id}"
            user_answer = answers.get(question_key)
            
            if question.question_type == 'mcq_single':
                # Single choice question
                if user_answer:
                    try:
                        selected_choice = Choice.objects.get(id=user_answer, question=question)
                        if selected_choice.is_correct:
                            correct_answers += 1
                    except Choice.DoesNotExist:
                        pass
            elif question.question_type == 'mcq_multiple':
                # Multiple choice question
                if user_answer and isinstance(user_answer, list):
                    correct_choices = question.choices.filter(is_correct=True).count()
                    selected_correct = 0
                    selected_incorrect = 0
                    
                    for choice_id in user_answer:
                        try:
                            choice = Choice.objects.get(id=choice_id, question=question)
                            if choice.is_correct:
                                selected_correct += 1
                            else:
                                selected_incorrect += 1
                        except Choice.DoesNotExist:
                            pass
                    
                    # Only count as correct if all correct choices are selected and no incorrect ones
                    if selected_correct == correct_choices and selected_incorrect == 0:
                        correct_answers += 1
            elif question.question_type == 'text':
                # Text input - for now, we'll count as correct if any answer is provided
                if user_answer and user_answer.strip():
                    correct_answers += 1
            elif question.question_type == 'true_false':
                # True/False question
                if user_answer is not None:
                    try:
                        # For true/false, we expect the answer to be a boolean or string representation
                        if isinstance(user_answer, str):
                            user_answer = user_answer.lower() in ['true', '1', 'yes']
                        elif isinstance(user_answer, int):
                            user_answer = bool(user_answer)
                        
                        # Get the correct answer from the first choice (True/False questions have only one choice)
                        correct_choice = question.choices.first()
                        if correct_choice and correct_choice.is_correct == user_answer:
                            correct_answers += 1
                    except (ValueError, AttributeError):
                        pass
        
        percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        
        # Create or update quiz attempt record
        attempt, created = QuizAttempt.objects.get_or_create(
            user=user,
            quiz=quiz,
            defaults={
                'score': correct_answers,
                'total_questions': total_questions,
                'percentage': percentage
            }
        )
        
        if not created:
            # Update existing attempt
            attempt.score = correct_answers
            attempt.total_questions = total_questions
            attempt.percentage = percentage
            attempt.save()
        
        # Return results based on show_results setting
        if quiz.show_results:
            return Response({
                "quiz_id": quiz_id,
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "percentage": percentage,
                "score": f"{correct_answers}/{total_questions}"
            })
        else:
            return Response({
                "quiz_id": quiz_id,
                "message": "Quiz submitted successfully"
            })
            
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

def home_page(request):
    # Check if user is already logged in
    if 'staff_email' in request.session:
        return redirect('quiz:admin_dashboard')
    elif 'student_roll_number' in request.session:
        return redirect('quiz:student_dashboard')
    
    return render(request, "quiz/home.html")

def quiz_detail_page(request, quiz_id):
    # Get the quiz
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Check for appropriate access
    user_type = None
    user_identifier = None
    
    if 'staff_email' in request.session:
        user_type = 'staff'
        user_identifier = request.session['staff_email']
        
        # Verify staff has access to this quiz
        handled_courses = get_teacher_courses(user_identifier)
        can_access = False
        
        # Check if staff handles the course or created the quiz
        if quiz.course_id and quiz.course_id in handled_courses:
            can_access = True
        elif quiz.created_by and (quiz.created_by.email == user_identifier or quiz.created_by.username == user_identifier):
            can_access = True
        elif not quiz.course_id:  # Quizzes not linked to any course can be accessed by any staff
            can_access = True
        
        if not can_access:
            messages.error(request, "You don't have permission to view this quiz")
            return redirect('academic_integration:staff_dashboard')
            
    elif 'student_roll_number' in request.session:
        user_type = 'student'
        user_identifier = request.session['student_roll_number']
        
        # Verify enrollment
        enrolled_courses = get_student_courses(user_identifier)
        if quiz.course_id and quiz.course_id not in enrolled_courses:
            messages.error(request, "You are not enrolled in this course")
            return redirect('academic_integration:student_dashboard')
        
        # Check quiz availability
        if not quiz.is_available:
            if quiz.is_ended:
                messages.error(request, "This quiz has been ended by the teacher")
            elif not quiz.is_active:
                messages.error(request, "This quiz is not active")
            elif quiz.start_date and quiz.start_date > timezone.now():
                messages.error(request, "This quiz hasn't started yet")
            elif quiz.complete_by_date and quiz.complete_by_date < timezone.now():
                messages.error(request, "This quiz has expired")
            return redirect('quiz:student_dashboard')
            
        # Get or create user
        user, created = User.objects.get_or_create(
            username=user_identifier,
            defaults={
                'email': f"{user_identifier}@example.com",
                'role': 'student'
            }
        )
        
        # Check if already attempted
        attempt = QuizAttempt.objects.filter(user=user, quiz=quiz).first()
        if attempt and attempt.completed_at:
            if quiz.allow_review:
                return redirect('quiz:quiz_result_page', quiz_id=quiz_id)
            else:
                messages.error(request, "You have already completed this quiz and cannot review it")
                return redirect('quiz:student_dashboard')
    else:
        messages.error(request, "Please log in to access quizzes")
        return redirect('academic_integration:home')
    
    questions = quiz.questions.all()
    
    return render(request, "quiz/quiz_detail_page.html", {
        "quiz": quiz, 
        "questions": questions,
        "user_type": user_type,
        "user_name": request.session.get('staff_name' if user_type == 'staff' else 'student_name', user_identifier)
    })

def quiz_result_page(request, quiz_id):
    # Get the quiz
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Check for appropriate access
    user_type = None
    user_identifier = None
    attempt = None
    
    if 'staff_email' in request.session:
        user_type = 'staff'
        user_identifier = request.session['staff_email']
        
        # Verify staff has access to this quiz
        handled_courses = get_teacher_courses(user_identifier)
        can_access = False
        
        # Check if staff handles the course or created the quiz
        if quiz.course_id and quiz.course_id in handled_courses:
            can_access = True
        elif quiz.created_by and (quiz.created_by.email == user_identifier or quiz.created_by.username == user_identifier):
            can_access = True
        elif not quiz.course_id:  # Quizzes not linked to any course can be accessed by any staff
            can_access = True
        
        if not can_access:
            messages.error(request, "You don't have permission to view this quiz")
            return redirect('academic_integration:staff_dashboard')
            
        # For staff, we'll get all attempts in the template
        
    elif 'student_roll_number' in request.session:
        user_type = 'student'
        user_identifier = request.session['student_roll_number']
        
        # Verify enrollment
        enrolled_courses = get_student_courses(user_identifier)
        if quiz.course_id and quiz.course_id not in enrolled_courses:
            messages.error(request, "You are not enrolled in this course")
            return redirect('academic_integration:student_dashboard')
        
        # Get user
        user, created = User.objects.get_or_create(
            username=user_identifier,
            defaults={
                'email': f"{user_identifier}@example.com",
                'role': 'student'
            }
        )
        
        # Check if attempted
        attempt = QuizAttempt.objects.filter(user=user, quiz=quiz).first()
        if not attempt or not attempt.completed_at:
            messages.error(request, "You haven't completed this quiz yet")
            return redirect('quiz:student_dashboard')
            
        # Check if allowed to view results
        if not quiz.show_results and not quiz.allow_review:
            messages.error(request, "Results for this quiz are not available")
            return redirect('quiz:student_dashboard')
    else:
        messages.error(request, "Please log in to access quiz results")
        return redirect('academic_integration:home')
    
    return render(request, "quiz/quiz_result.html", {
        "quiz": quiz,
        "quiz_id": quiz_id,
        "attempt": attempt,
        "user_type": user_type,
        "user_name": request.session.get('staff_name' if user_type == 'staff' else 'student_name', user_identifier)
    })

def create_quiz(request):
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    staff_id = request.session.get('staff_teacher_id')
    
    if not staff_email:
        messages.error(request, "You must be logged in as staff")
        return redirect('academic_integration:staff_login')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create or get the staff user
            staff_user, created = User.objects.get_or_create(
                username=staff_email,
                defaults={
                    'email': staff_email,
                    'role': 'admin'
                }
            )
            
            # Set is_mock_test based on tutorial_number
            quiz_type = data.get('quiz_type', 'tutorial')
            if not data.get('tutorial_number') and quiz_type == 'tutorial':
                quiz_type = 'mock'
            
            # Create the quiz
            quiz = Quiz.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                start_date=data.get('start_date'),
                complete_by_date=data.get('complete_by_date'),
                course_id=data.get('course_id'),
                tutorial_number=data.get('tutorial_number'),
                created_by=staff_user,
                quiz_type=quiz_type,
                duration_minutes=int(data.get('duration_minutes', 30)),
                is_active=data.get('is_active', True),
                show_results=data.get('show_results', True),
                allow_review=data.get('allow_review', True)
            )
            
            # Create questions
            for question_data in data['questions']:
                question = Question.objects.create(
                    quiz=quiz,
                    text=question_data['text'],
                    question_type=question_data['type'],
                    order=question_data.get('order', 0)
                )
                if question_data['type'] in ['mcq_single', 'mcq_multiple', 'true_false']:
                    for choice_data in question_data['choices']:
                        Choice.objects.create(
                            question=question,
                            text=choice_data['text'],
                            is_correct=choice_data['is_correct'],
                            order=choice_data.get('order', 0)
                        )
            return JsonResponse({'success': True, 'quiz_id': quiz.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get courses for the dropdown menu
    courses = []
    try:
        response = requests.get(
            f"{_api_base_url()}/staff/dashboard",
            params={"email": staff_email},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if data.get('success'):
                courses = data.get('courses', [])
    except requests.RequestException:
        pass
    
    return render(request, "quiz/create_quiz.html", {
        'courses': courses,
        'staff_email': staff_email,
        'staff_name': request.session.get('staff_name', staff_email),
    })

# Grade a quiz attempt
@api_view(["POST"])
def grade_answer(request):
    try:
        quiz_attempt_id = request.data.get('quiz_attempt_id')
        points = float(request.data.get('points', 0))
        feedback = request.data.get('feedback', '')
        
        if not quiz_attempt_id:
            return Response({"error": "Quiz Attempt ID is required"}, status=400)
            
        # Ensure staff is logged in
        staff_email = request.session.get('staff_email')
        if not staff_email:
            return Response({"error": "You must be logged in as staff"}, status=403)
            
        # Get the quiz attempt
        attempt = QuizAttempt.objects.get(pk=quiz_attempt_id)
        
        # Verify staff has access to this quiz
        quiz = attempt.quiz
        handled_courses = get_teacher_courses(staff_email)
        
        # Only allow grading if staff handles the course or created the quiz
        if quiz.course_id and quiz.course_id not in handled_courses:
            if not (quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email)):
                return Response({"error": "You don't have access to grade this quiz"}, status=403)
        
        # Get or create staff user
        staff_user, created = User.objects.get_or_create(
            username=staff_email,
            defaults={
                'email': staff_email,
                'role': 'admin'
            }
        )
        
        # Update the quiz attempt
        attempt.score = points
        attempt.feedback = feedback
        attempt.graded_by = staff_user
        attempt.status = 'graded'
        attempt.save()
            
        # Calculate percentage
        if attempt.total_questions > 0:
            attempt.percentage = (points / attempt.total_questions) * 100
            attempt.save()
            
        return Response({
            "success": True,
            "attempt_id": quiz_attempt_id,
            "points": points,
            "percentage": attempt.percentage
        })
        
    except QuizAttempt.DoesNotExist:
        return Response({"error": "Quiz attempt not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# End a quiz (mark as ended)
@api_view(["POST"])
def end_quiz(request, quiz_id):
    try:
        # Ensure staff is logged in
        staff_email = request.session.get('staff_email')
        if not staff_email:
            return Response({"error": "You must be logged in as staff"}, status=403)
            
        # Get the quiz
        quiz = Quiz.objects.get(pk=quiz_id)
        
        # Verify staff has access to this quiz
        handled_courses = get_teacher_courses(staff_email)
        
        # Only allow ending if staff handles the course or created the quiz
        if quiz.course_id and quiz.course_id not in handled_courses:
            if not (quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email)):
                return Response({"error": "You don't have access to end this quiz"}, status=403)
        
        # Update the quiz
        quiz.is_ended = True
        quiz.save()
        
        return Response({
            "success": True,
            "quiz_id": quiz_id,
            "message": "Quiz has been ended"
        })
        
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# Check if a tutorial already has a quiz assigned
@api_view(["GET"])
def check_tutorial_availability(request):
    course_id = request.query_params.get('course_id')
    tutorial_number = request.query_params.get('tutorial_number')
    
    # If no course or tutorial specified, it's available
    if not course_id or not tutorial_number:
        return Response({"available": True})
    
    # Check if there's already a quiz for this tutorial and course
    existing_quiz = Quiz.objects.filter(
        course_id=course_id, 
        tutorial_number=tutorial_number
    ).first()
    
    if existing_quiz:
        return Response({
            "available": False,
            "message": f"Tutorial {tutorial_number} already has a quiz: '{existing_quiz.title}' assigned."
        })
    else:
        return Response({"available": True})

# Get all attempts for a quiz
@api_view(["GET"])
def quiz_attempts(request, quiz_id):
    try:
        # Ensure staff is logged in
        staff_email = request.session.get('staff_email')
        if not staff_email:
            return Response({"error": "You must be logged in as staff"}, status=403)
            
        # Get the quiz
        quiz = Quiz.objects.get(pk=quiz_id)
        
        # Verify staff has access to this quiz
        handled_courses = get_teacher_courses(staff_email)
        
        # Only allow viewing attempts if staff handles the course or created the quiz
        if quiz.course_id and quiz.course_id not in handled_courses:
            if not (quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email)):
                return Response({"error": "You don't have access to view attempts for this quiz"}, status=403)
        
        # Get all attempts for this quiz
        attempts = QuizAttempt.objects.filter(quiz=quiz).order_by('-completed_at')
        
        serializer = QuizAttemptSerializer(attempts, many=True)
        return Response(serializer.data)
        
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

def edit_quiz(request, quiz_id):
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    staff_id = request.session.get('staff_teacher_id')
    
    if not staff_email:
        messages.error(request, "You must be logged in as staff")
        return redirect('academic_integration:staff_login')
    
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Verify staff has access to this quiz
    handled_courses = get_teacher_courses(staff_email)
    can_edit = False
    
    # Check if staff handles the course or created the quiz
    if quiz.course_id and quiz.course_id in handled_courses:
        can_edit = True
    elif quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email):
        can_edit = True
    elif not quiz.course_id:  # Quizzes not linked to any course can be edited by any staff
        can_edit = True
    
    if not can_edit:
        messages.error(request, "You don't have permission to edit this quiz")
        return redirect('academic_integration:staff_dashboard')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quiz.title = data['title']
            quiz.description = data.get('description', '')
            quiz.start_date = data.get('start_date')
            quiz.complete_by_date = data.get('complete_by_date')
            quiz.course_id = data.get('course_id')
            quiz.tutorial_number = data.get('tutorial_number')
            quiz.quiz_type = data.get('quiz_type', 'tutorial')
            quiz.duration_minutes = int(data.get('duration_minutes', 30))
            quiz.is_active = data.get('is_active', True)
            quiz.show_results = data.get('show_results', True)
            quiz.allow_review = data.get('allow_review', True)
            
            # Create or get the staff user
            staff_user, created = User.objects.get_or_create(
                username=staff_email,
                defaults={
                    'email': staff_email,
                    'role': 'admin'
                }
            )
            
            # Set created_by if not already set
            if not quiz.created_by:
                quiz.created_by = staff_user
                
            quiz.save()
            
            # Delete existing questions
            quiz.questions.all().delete()
            
            # Create new questions
            for question_data in data['questions']:
                question = Question.objects.create(
                    quiz=quiz,
                    text=question_data['text'],
                    question_type=question_data['type'],
                    order=question_data.get('order', 0)
                )
                if question_data['type'] in ['mcq_single', 'mcq_multiple', 'true_false']:
                    for choice_data in question_data['choices']:
                        Choice.objects.create(
                            question=question,
                            text=choice_data['text'],
                            is_correct=choice_data['is_correct'],
                            order=choice_data.get('order', 0)
                        )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Get courses for the dropdown menu
    courses = []
    try:
        response = requests.get(
            f"{_api_base_url()}/staff/dashboard",
            params={"email": staff_email},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if data.get('success'):
                courses = data.get('courses', [])
    except requests.RequestException:
        pass
    
    return render(request, "quiz/edit_quiz.html", {
        'quiz': quiz,
        'courses': courses,
        'staff_email': staff_email,
        'staff_name': request.session.get('staff_name', staff_email),
    })

def delete_quiz(request, quiz_id):
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    
    if not staff_email:
        messages.error(request, "You must be logged in as staff")
        return redirect('academic_integration:staff_login')
    
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Verify staff has access to this quiz
    handled_courses = get_teacher_courses(staff_email)
    can_delete = False
    
    # Check if staff handles the course or created the quiz
    if quiz.course_id and quiz.course_id in handled_courses:
        can_delete = True
    elif quiz.created_by and (quiz.created_by.email == staff_email or quiz.created_by.username == staff_email):
        can_delete = True
    
    if not can_delete:
        messages.error(request, "You don't have permission to delete this quiz")
        return redirect('academic_integration:staff_dashboard')
    
    if request.method == 'POST':
        quiz.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@api_view(["GET"])
def get_active_quizzes(request, student_roll_number):
    """
    Get active quizzes for a specific student by roll number.
    Returns quizzes that:
    1. Are active and not ended
    2. Student is enrolled in the course
    3. Current time is between start date and complete by date
    4. Has not been completed by the student or allows retaking
    """
    # Get today's date for filtering active quizzes
    today = timezone.now()
    
    # Get courses the student is enrolled in
    enrolled_courses = get_student_courses(student_roll_number)
    
    # Get active quizzes for enrolled courses
    active_quizzes = Quiz.objects.filter(
        Q(course_id__in=enrolled_courses) &
        Q(is_active=True) &
        Q(is_ended=False) &
        (Q(start_date__lte=today) | Q(start_date__isnull=True)) &
        (Q(complete_by_date__gte=today) | Q(complete_by_date__isnull=True))
    ).prefetch_related('questions')
    
    # Check for attempt status
    result_quizzes = []
    for quiz in active_quizzes:
        # Get the user
        user = User.objects.filter(username=student_roll_number).first()
        if not user:
            continue
            
        # Check if there's an attempt and if it's complete
        attempt = QuizAttempt.objects.filter(
            quiz=quiz,
            user=user
        ).order_by('-started_at').first()
        
        # Include quiz if:
        # 1. No attempt exists
        # 2. Attempt exists but is not completed
        # 3. Attempt is completed but quiz allows retaking
        if (not attempt or 
            not attempt.completed_at or 
            quiz.allow_retake):
            
            quiz_data = {
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'course_id': quiz.course_id,
                'tutorial_number': quiz.tutorial_number,
                'quiz_type': quiz.quiz_type,
                'duration_minutes': quiz.duration_minutes,
                'start_date': quiz.start_date,
                'complete_by_date': quiz.complete_by_date,
                'question_count': quiz.questions.count(),
                'attempt_status': 'in_progress' if attempt and not attempt.completed_at else 'not_started' if not attempt else 'completed'
            }
            result_quizzes.append(quiz_data)
    
    return Response({
        'count': len(result_quizzes),
        'quizzes': result_quizzes
    })

def admin_dashboard(request):
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    
    if not staff_email:
        messages.info(request, "Please log in to continue.")
        return redirect('academic_integration:staff_login')
    
    # Get courses taught by the teacher
    courses = []
    try:
        response = requests.get(
            f"{_api_base_url()}/staff/dashboard",
            params={"email": staff_email},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if data.get('success'):
                courses = data.get('courses', [])
    except requests.RequestException:
        pass
    
    # Create a dictionary to store courses by ID
    course_dict = {course['courseId']: course for course in courses}
    
    # Include both course-specific quizzes and quizzes created by this staff
    course_ids = [course['courseId'] for course in courses]
    
    quizzes = Quiz.objects.filter(
        Q(course_id__in=course_ids) | 
        Q(created_by__email=staff_email) |
        Q(created_by__username=staff_email)
    ).order_by('-created_at')
    
        # Get quiz statistics and enhance with course information
    for quiz in quizzes:
        quiz.num_attempts = QuizAttempt.objects.filter(quiz=quiz).count()
        quiz.num_completed = QuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=False).count()
        quiz.avg_score = QuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=False).aggregate(Avg('percentage'))['percentage__avg'] or 0
        
        # Check for submissions that need grading (status='submitted')
        quiz.needs_grading = QuizAttempt.objects.filter(
            quiz=quiz,
            status='submitted'
        ).exists()
        
        # Add course information if available
        if quiz.course_id and quiz.course_id in course_dict:
            quiz.course_name = course_dict[quiz.course_id]['courseName']
        else:
            quiz.course_name = None
    
    return render(request, 'quiz/admin_dashboard.html', {
        'quizzes': quizzes,
        'courses': courses,
        'staff_email': staff_email,
        'staff_name': request.session.get('staff_name', staff_email),
    })

def student_dashboard(request):
    # Ensure student is logged in
    student_roll_number = request.session.get('student_roll_number')
    
    if not student_roll_number:
        messages.info(request, "Please log in to continue.")
        return redirect('academic_integration:student_login')
    
    # Get courses the student is enrolled in
    enrolled_courses = get_student_courses(student_roll_number)
    
    # Get available quizzes for the enrolled courses
    now = timezone.now()
    quizzes = Quiz.objects.filter(
        Q(course_id__in=enrolled_courses) | Q(course_id__isnull=True),
        is_active=True,
        is_ended=False
    ).filter(
        # Either no start date, or start date has passed
        Q(start_date__isnull=True) | Q(start_date__lte=now)
    ).filter(
        # Either no end date, or end date is in the future
        Q(complete_by_date__isnull=True) | Q(complete_by_date__gt=now)
    ).order_by('complete_by_date')
    
    # Get student's attempts
    user, created = User.objects.get_or_create(
        username=student_roll_number,
        defaults={
            'email': f"{student_roll_number}@example.com",
            'role': 'student'
        }
    )
    
    attempts = QuizAttempt.objects.filter(user=user).select_related('quiz')
    attempted_quiz_ids = [attempt.quiz_id for attempt in attempts]
    
    # Mark quizzes as attempted
    for quiz in quizzes:
        quiz.attempted = quiz.id in attempted_quiz_ids
        # Find the matching attempt if any
        quiz.attempt = next((a for a in attempts if a.quiz_id == quiz.id), None)
    
    # Get course details
    courses = []
    try:
        response = requests.get(
            f"{_api_base_url()}/student/dashboard",
            params={"rollno": student_roll_number},
            timeout=5,
        )
        if response.ok:
            data = response.json()
            if data.get('success'):
                courses = data.get('courses', [])
    except requests.RequestException:
        pass
    
    return render(request, 'quiz/student_dashboard.html', {
        'quizzes': quizzes,
        'courses': courses,
        'attempts': attempts,
        'student_roll_number': student_roll_number,
        'student_name': request.session.get('student_name', student_roll_number),
    })

# Debug views for quiz availability issues
@login_required
def debug_quiz(request, quiz_id=None):
    """
    View for debugging quiz availability issues
    Shows timezone information and quiz dates
    """
    from django.conf import settings
    import datetime
    
    # General system information
    context = {
        'django_timezone': settings.TIME_ZONE,
        'current_time_aware': timezone.now(),
        'current_time_naive': datetime.datetime.now(),
        'is_dst': timezone.now().dst() != datetime.timedelta(0),
    }
    
    # Get quizzes with availability issues if no specific quiz is requested
    if quiz_id is None:
        # Get all quizzes
        quizzes = Quiz.objects.all().order_by('-created_at')[:20]  # Limit to 20 most recent
        
        # Add debug information for each quiz
        quiz_debug_info = []
        for quiz in quizzes:
            is_visible, reason = quiz.debug_visibility_status()
            
            quiz_info = {
                'id': quiz.id,
                'title': quiz.title,
                'is_visible': is_visible,
                'reason': reason,
                'start_date': quiz.start_date,
                'start_date_naive': timezone.is_naive(quiz.start_date) if quiz.start_date else None,
                'complete_by_date': quiz.complete_by_date,
                'complete_by_naive': timezone.is_naive(quiz.complete_by_date) if quiz.complete_by_date else None,
                'is_active': quiz.is_active,
                'is_ended': quiz.is_ended,
            }
            quiz_debug_info.append(quiz_info)
        
        context['quiz_debug_info'] = quiz_debug_info
        return render(request, 'quiz/debug_quizzes.html', context)
    
    # Get specific quiz information
    else:
        quiz = get_object_or_404(Quiz, id=quiz_id)
        is_visible, reason = quiz.debug_visibility_status()
        
        # Add detailed quiz information
        context.update({
            'quiz': quiz,
            'is_visible': is_visible,
            'reason': reason,
            'start_date_naive': timezone.is_naive(quiz.start_date) if quiz.start_date else None,
            'complete_by_naive': timezone.is_naive(quiz.complete_by_date) if quiz.complete_by_date else None,
        })
        
        return render(request, 'quiz/debug_quiz_detail.html', context)