"""
Debug views for diagnosing issues with quizzes, especially availability problems.
These views are intended for development and troubleshooting only.
"""
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Quiz, QuizAttempt

def debug_quiz_availability(request, quiz_id):
    """
    Returns detailed information about why a quiz might not be available.
    This is helpful for debugging issues with quiz availability for students.
    """
    # Get the quiz
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    
    # Check all factors that might affect availability
    now = timezone.now()
    
    # Basic quiz info
    data = {
        "quiz_id": quiz.id,
        "title": quiz.title,
        "is_active": quiz.is_active,
        "is_ended": quiz.is_ended,
        "question_count": quiz.questions.count(),
        "current_server_time": now.isoformat(),
    }
    
    # Availability status
    availability_issues = []
    if not quiz.is_active:
        availability_issues.append("Quiz is not active (is_active=False)")
    
    if quiz.is_ended:
        availability_issues.append("Quiz has been manually ended by teacher (is_ended=True)")
    
    # Date checks
    data["start_date"] = quiz.start_date.isoformat() if quiz.start_date else None
    data["complete_by_date"] = quiz.complete_by_date.isoformat() if quiz.complete_by_date else None
    
    if quiz.start_date:
        if now < quiz.start_date:
            availability_issues.append(f"Quiz start date ({quiz.start_date}) is in the future")
        data["time_until_start"] = (quiz.start_date - now).total_seconds() if now < quiz.start_date else 0
        
    if quiz.complete_by_date:
        if now > quiz.complete_by_date:
            availability_issues.append(f"Quiz deadline ({quiz.complete_by_date}) has passed")
        data["time_until_deadline"] = (quiz.complete_by_date - now).total_seconds() if now < quiz.complete_by_date else 0
    
    # Question checks
    if quiz.questions.count() == 0:
        availability_issues.append("Quiz has no questions")
    
    # Overall availability status
    data["is_available"] = len(availability_issues) == 0
    data["availability_issues"] = availability_issues
    
    # Get debug visibility status
    debug_visible, reason = quiz.debug_visibility_status()
    data["debug_is_visible"] = debug_visible
    data["debug_reason"] = reason
    
    # Return JSON response
    return JsonResponse(data)

def debug_quiz_timezone(request):
    """
    Returns information about the server's timezone configuration.
    Useful for debugging timezone-related issues.
    """
    from django.conf import settings
    import datetime
    
    data = {
        "server_time": timezone.now().isoformat(),
        "server_time_naive": datetime.datetime.now().isoformat(),
        "timezone_setting": settings.TIME_ZONE,
        "use_tz_setting": settings.USE_TZ
    }
    
    return JsonResponse(data)