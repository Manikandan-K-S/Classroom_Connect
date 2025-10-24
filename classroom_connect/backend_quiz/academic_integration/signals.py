"""
Signal handlers for the academic_integration app.
"""
import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from quiz.models import QuizAttempt

logger = logging.getLogger(__name__)


@receiver(post_save, sender=QuizAttempt)
def sync_completed_quiz_attempt(sender, instance, created, **kwargs):
    """
    Signal handler to sync a quiz attempt with Academic Analyzer when it's completed.
    """
    # Only sync completed tutorial quizzes that have required information
    if (instance.completed_at and 
            instance.quiz.quiz_type == 'tutorial' and 
            instance.quiz.course_id and 
            instance.quiz.tutorial_number and 
            not instance.marks_synced):
        
        logger.info(f"Detected completed quiz attempt {instance.id} that needs sync")
        
        api_url = getattr(settings, 'ACADEMIC_ANALYZER_BASE_URL', None)
        if not api_url:
            logger.warning("ACADEMIC_ANALYZER_BASE_URL not configured, skipping sync")
            return
            
        quiz = instance.quiz
        student_roll_number = instance.user.username
        
        # Format the score for academic analyzer - scale to 0-10 for tutorial marks
        tutorial_number = quiz.tutorial_number
        scaled_score = instance.percentage / 10  # Scale from 0-100% to 0-10
        
        api_data = {
            'studentId': student_roll_number,
            'courseId': quiz.course_id,
            'teacherEmail': 'mks.mca@psgtech.ac.in',  # Use valid teacher email
            'marks': {
                f'tutorial{tutorial_number}': scaled_score
            }
        }
        
        try:
            # Send to Academic Analyzer API
            update_marks_url = f"{api_url.rstrip('/')}/staff/update-student-marks"
            
            logger.info(f"Syncing marks for student {student_roll_number}, " +
                       f"course {quiz.course_id}, tutorial {tutorial_number}")
            
            response = requests.post(
                update_marks_url,
                json=api_data,
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"Successfully synced marks for attempt {instance.id}")
                
                # Mark as synced
                instance.marks_synced = True
                instance.last_sync_at = timezone.now()
                instance.save()
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Request error: {str(e)}")