"""
Middleware to handle background tasks in the Django application.
"""
import threading
import time
import logging
import requests
from django.conf import settings
from django.utils import timezone
from quiz.models import QuizAttempt

logger = logging.getLogger(__name__)


class BackgroundTaskThread(threading.Thread):
    """
    Thread to handle background tasks.
    """
    def __init__(self, *args, **kwargs):
        self._stop_event = threading.Event()
        self.interval = kwargs.pop('interval', 300)  # Default interval is 5 minutes
        super().__init__(*args, **kwargs)
        self.daemon = True  # Thread will exit when main process exits
        
    def stop(self):
        """Stop the background task thread."""
        self._stop_event.set()
        
    def stopped(self):
        """Check if the thread is stopped."""
        return self._stop_event.is_set()
        
    def run(self):
        """Run the background task thread."""
        logger.info("Starting background task thread to sync quiz attempts with Academic Analyzer")
        
        while not self.stopped():
            try:
                # Sync unsynced quiz attempts with Academic Analyzer
                self.sync_unsynced_quiz_attempts()
            except Exception as e:
                logger.exception(f"Error in background task thread: {e}")
            
            # Sleep for interval seconds, checking for stop every second
            for _ in range(self.interval):
                if self.stopped():
                    break
                time.sleep(1)
                
    def sync_unsynced_quiz_attempts(self):
        """Sync unsynced quiz attempts with Academic Analyzer."""
        api_url = getattr(settings, 'ACADEMIC_ANALYZER_BASE_URL', None)
        if not api_url:
            logger.warning("ACADEMIC_ANALYZER_BASE_URL not configured, skipping sync")
            return
            
        # Find tutorial quiz attempts that are completed but not synced
        attempts = QuizAttempt.objects.filter(
            completed_at__isnull=False,
            quiz__quiz_type='tutorial',
            quiz__course_id__isnull=False,
            quiz__tutorial_number__isnull=False,
            marks_synced=False
        ).select_related('quiz', 'user')
        
        if not attempts.exists():
            # No unsynced attempts found, nothing to do
            return
            
        logger.info(f"Found {attempts.count()} unsynced tutorial quiz attempts to sync")
        
        success_count = 0
        error_count = 0
        
        for attempt in attempts:
            quiz = attempt.quiz
            student_roll_number = attempt.user.username
            
            # Format the score for academic analyzer - scale to 0-10 for tutorial marks
            tutorial_number = quiz.tutorial_number
            scaled_score = attempt.percentage / 10  # Scale from 0-100% to 0-10
            
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
                
                response = requests.post(
                    update_marks_url,
                    json=api_data,
                    timeout=10
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    logger.info(f"Successfully synced marks for attempt {attempt.id} by {student_roll_number}")
                    
                    # Mark as synced
                    attempt.marks_synced = True
                    attempt.last_sync_at = timezone.now()
                    attempt.save()
                    
                    success_count += 1
                else:
                    logger.error(f"API error for attempt {attempt.id}: {response.status_code} - {response.text}")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"Request error for attempt {attempt.id}: {str(e)}")
                error_count += 1
        
        if success_count > 0 or error_count > 0:
            logger.info(f"Sync completed: successfully sent {success_count} marks, encountered {error_count} errors")


class BackgroundTaskMiddleware:
    """
    Middleware to start and manage background tasks.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.background_task_thread = None
        self.start_background_tasks()
        
    def start_background_tasks(self):
        """Start background tasks."""
        if not self.background_task_thread or not self.background_task_thread.is_alive():
            self.background_task_thread = BackgroundTaskThread(
                name="QuizSyncThread",
                interval=300  # Run every 5 minutes
            )
            self.background_task_thread.start()
            
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Ensure background tasks are running
        if not self.background_task_thread or not self.background_task_thread.is_alive():
            self.start_background_tasks()
            
        return response
