"""
This module adds the views for synchronizing tutorial attempts with Academic Analyzer.
"""
import logging
import requests
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.db.models import Count, Q
from quiz.models import QuizAttempt, Quiz
from .utils import api_base_url

logger = logging.getLogger(__name__)


@staff_member_required
def sync_dashboard(request):
    """
    Display a dashboard showing tutorial sync status.
    """
    # Get statistics for the dashboard
    total_tutorial_attempts = QuizAttempt.objects.filter(
        completed_at__isnull=False,
        quiz__quiz_type='tutorial',
        quiz__tutorial_number__isnull=False,
        quiz__course_id__isnull=False
    ).count()
    
    unsynced_attempts = QuizAttempt.objects.filter(
        marks_synced=False,
        completed_at__isnull=False,
        quiz__quiz_type='tutorial',
        quiz__tutorial_number__isnull=False,
        quiz__course_id__isnull=False
    )
    
    unsynced_count = unsynced_attempts.count()
    synced_count = total_tutorial_attempts - unsynced_count
    
    # Get list of unsynced attempts with details
    unsynced_attempts_list = unsynced_attempts.select_related('user', 'quiz').order_by('-completed_at')[:50]
    
    # Get sync history (recently synced attempts)
    recently_synced = QuizAttempt.objects.filter(
        marks_synced=True,
        last_sync_at__isnull=False
    ).select_related('user', 'quiz').order_by('-last_sync_at')[:20]
    
    # Get course-wise statistics
    course_stats = QuizAttempt.objects.filter(
        completed_at__isnull=False,
        quiz__quiz_type='tutorial',
        quiz__course_id__isnull=False
    ).values('quiz__course_id').annotate(
        total=Count('id'),
        synced=Count('id', filter=Q(marks_synced=True)),
        unsynced=Count('id', filter=Q(marks_synced=False))
    ).order_by('quiz__course_id')
    
    # Check API status
    try:
        api_response = requests.get(f"{api_base_url()}/status", timeout=2)
        api_status = {
            'available': api_response.ok,
            'status_code': api_response.status_code if hasattr(api_response, 'status_code') else None,
            'url': api_base_url()
        }
    except requests.RequestException:
        api_status = {
            'available': False,
            'error': 'Connection failed',
            'url': api_base_url()
        }
    
    context = {
        'total_tutorial_attempts': total_tutorial_attempts,
        'synced_count': synced_count,
        'unsynced_count': unsynced_count,
        'sync_percentage': (synced_count / total_tutorial_attempts * 100) if total_tutorial_attempts > 0 else 0,
        'unsynced_attempts': unsynced_attempts_list,
        'recently_synced': recently_synced,
        'course_stats': course_stats,
        'api_status': api_status,
        'staff_email': request.session.get('staff_email', request.user.email if hasattr(request.user, 'email') else None),
        'staff_name': request.session.get('staff_name', request.user.get_full_name() if hasattr(request.user, 'get_full_name') else None),
        'now': timezone.now()
    }
    
    return render(request, 'academic_integration/sync_dashboard.html', context)


@staff_member_required
def sync_tutorial_attempt(request, attempt_id):
    """Manually sync a specific quiz attempt with Academic Analyzer."""
    
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    if attempt.quiz.quiz_type != 'tutorial' or not attempt.quiz.course_id or not attempt.quiz.tutorial_number:
        messages.error(request, "This attempt is not a valid tutorial attempt")
        return redirect('academic_integration:sync_dashboard')
    
    if attempt.completed_at is None:
        messages.error(request, "This attempt is not yet completed")
        return redirect('academic_integration:sync_dashboard')
    
    api_url = api_base_url()
    
    # Format the score for academic analyzer - properly calculate the scaled score
    quiz = attempt.quiz
    student_roll_number = attempt.user.username
    tutorial_number = quiz.tutorial_number
    
    # Calculate the scaled score properly - using actual points ratio
    # This ensures the score reflects the actual performance 
    if attempt.total_points > 0:
        scaled_score = (attempt.score / attempt.total_points) * 10  # Convert to 0-10 scale
        logger.info(f"Calculated tutorial mark for sync: {attempt.score}/{attempt.total_points} * 10 = {scaled_score}")
    else:
        scaled_score = 0
        logger.warning(f"Total points is 0 for attempt {attempt.id}, setting scaled score to 0")
    
    # Get teacher's email from multiple sources
    teacher_email = None
    
    # First, check if the quiz has a creator with an email
    if quiz.created_by and quiz.created_by.email:
        teacher_email = quiz.created_by.email
        logger.info(f"Using quiz creator's email for sync: {teacher_email}")
    
    # If no teacher email from quiz creator, try to get from API
    if not teacher_email:
        try:
            course_response = requests.get(
                f"{api_base_url()}/staff/course-detail",
                params={"courseId": quiz.course_id},
                timeout=5,
            )
            
            if course_response.ok:
                course_data = course_response.json()
                if course_data.get("success"):
                    # Use instructor email if available
                    teacher_email = course_data.get("instructorEmail")
                    if teacher_email:
                        logger.info(f"Found instructor email for course {quiz.course_id}: {teacher_email}")
        except Exception as e:
            logger.warning(f"Failed to get instructor email from API: {str(e)}")
    
    # If still no teacher email, check if there's a staff email in the session
    if not teacher_email and hasattr(request, 'session') and request.session.get('staff_email'):
        teacher_email = request.session.get('staff_email')
        logger.info(f"Using staff email from session: {teacher_email}")
    
    # If still no email, use the requesting staff member's email
    if not teacher_email and hasattr(request, 'user') and hasattr(request.user, 'email'):
        teacher_email = request.user.email
        logger.info(f"Using staff email from request.user: {teacher_email}")
    
    # As a last resort, use a default format based on course ID
    if not teacher_email:
        teacher_email = f"teacher_{quiz.course_id.lower()}@psgtech.ac.in"
        logger.warning(f"No teacher email found, using generated fallback: {teacher_email}")
    
    api_data = {
        'studentId': student_roll_number,
        'courseId': quiz.course_id,
        'teacherEmail': teacher_email,
        'marks': {
            f'tutorial{tutorial_number}': scaled_score
        }
    }
    
    try:
        # Send to Academic Analyzer API
        update_marks_url = f"{api_url}/staff/update-student-marks"
        
        response = requests.post(
            update_marks_url,
            json=api_data,
            timeout=10
        )
        
        if response.status_code == 200 or response.status_code == 201:
            attempt.marks_synced = True
            attempt.last_sync_at = timezone.now()
            attempt.save()
            messages.success(request, f"Successfully synced marks for {student_roll_number}")
        else:
            messages.error(request, f"API error: {response.status_code} - {response.text}")
    except Exception as e:
        messages.error(request, f"Request error: {str(e)}")
    
    return redirect('academic_integration:sync_dashboard')


@staff_member_required
def sync_all_tutorials(request):
    """Manually sync all unsynced tutorial quiz attempts with Academic Analyzer."""
    
    unsynced_attempts = QuizAttempt.objects.filter(
        completed_at__isnull=False,
        quiz__quiz_type='tutorial',
        quiz__course_id__isnull=False,
        quiz__tutorial_number__isnull=False,
        marks_synced=False
    ).select_related('quiz', 'user')
    
    if not unsynced_attempts.exists():
        messages.info(request, "No unsynced attempts found")
        return redirect('academic_integration:sync_dashboard')
    
    api_url = api_base_url()
    
    success_count = 0
    error_count = 0
    
    for attempt in unsynced_attempts:
        quiz = attempt.quiz
        student_roll_number = attempt.user.username
        tutorial_number = quiz.tutorial_number
        
        # Calculate the scaled score properly - using actual points ratio
        if attempt.total_points > 0:
            scaled_score = (attempt.score / attempt.total_points) * 10  # Convert to 0-10 scale
            logger.info(f"Calculated tutorial mark for sync: {attempt.score}/{attempt.total_points} * 10 = {scaled_score}")
        else:
            scaled_score = 0
            logger.warning(f"Total points is 0 for attempt {attempt.id}, setting scaled score to 0")
        
        # Get teacher's email from multiple sources
        teacher_email = None
        
        # First, check if the quiz has a creator with an email
        if quiz.created_by and quiz.created_by.email:
            teacher_email = quiz.created_by.email
            logger.info(f"Using quiz creator's email for batch sync: {teacher_email}")
        
        # If no teacher email from quiz creator, try to get from API
        if not teacher_email:
            try:
                course_response = requests.get(
                    f"{api_base_url()}/staff/course-detail",
                    params={"courseId": quiz.course_id},
                    timeout=5,
                )
                
                if course_response.ok:
                    course_data = course_response.json()
                    if course_data.get("success"):
                        # Use instructor email if available
                        teacher_email = course_data.get("instructorEmail")
                        if teacher_email:
                            logger.info(f"Found instructor email for course {quiz.course_id}: {teacher_email}")
            except Exception as e:
                logger.warning(f"Failed to get instructor email from API: {str(e)}")
        
        # If still no teacher email, use requesting user's info
        if not teacher_email and hasattr(request, 'session') and request.session.get('staff_email'):
            teacher_email = request.session.get('staff_email')
            logger.info(f"Using staff email from session for batch sync: {teacher_email}")
        
        # As a last resort, use a default format based on course ID
        if not teacher_email:
            teacher_email = f"teacher_{quiz.course_id.lower()}@psgtech.ac.in"
            logger.warning(f"No teacher email found for batch sync, using generated fallback: {teacher_email}")
        
        api_data = {
            'studentId': student_roll_number,
            'courseId': quiz.course_id,
            'teacherEmail': teacher_email,
            'marks': {
                f'tutorial{tutorial_number}': scaled_score
            }
        }
        
        try:
            # Send to Academic Analyzer API
            update_marks_url = f"{api_url}/staff/update-student-marks"
            
            response = requests.post(
                update_marks_url,
                json=api_data,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                attempt.marks_synced = True
                attempt.last_sync_at = timezone.now()
                attempt.save()
                success_count += 1
            else:
                error_count += 1
                logger.error(f"API error for attempt {attempt.id}: {response.status_code} - {response.text}")
        except Exception as e:
            error_count += 1
            logger.error(f"Request error for attempt {attempt.id}: {str(e)}")
    
    if success_count > 0:
        messages.success(request, f"Successfully synced {success_count} attempts")
    if error_count > 0:
        messages.warning(request, f"Failed to sync {error_count} attempts. Check logs for details.")
    
    return redirect('academic_integration:sync_dashboard')


def check_api_status(request):
    """Check if Academic Analyzer API is up and running."""
    try:
        # Simple GET request to check API availability
        response = requests.get(f"{api_base_url()}/status", timeout=3)
        if response.ok:
            return JsonResponse({
                'success': True,
                'message': 'Academic Analyzer API is available',
                'status': response.status_code,
                'api_url': api_base_url()
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': f'API responded with status code: {response.status_code}',
                'status': response.status_code,
                'api_url': api_base_url()
            })
    except requests.RequestException as e:
        return JsonResponse({
            'success': False, 
            'message': f'Failed to connect to Academic Analyzer API: {str(e)}',
            'error': str(e),
            'api_url': api_base_url()
        })