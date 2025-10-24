from django.core.management.base import BaseCommand
import logging
import requests
from django.conf import settings
from django.utils import timezone
from quiz.models import Quiz, QuizAttempt

logger = logging.getLogger(__name__)

def _api_base_url():
    """Get the base URL for the Academic Analyzer API"""
    return getattr(settings, 'ACADEMIC_ANALYZER_BASE_URL', 'http://localhost:5000')

def _safe_json(response):
    """Safely extract JSON from a response or return empty dict"""
    try:
        return response.json()
    except:
        return {}

class Command(BaseCommand):
    help = 'Sync unsynced quiz attempts with Academic Analyzer'
    
    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force sync even for already synced attempts')
        parser.add_argument('--dry-run', action='store_true', help='Only report what would be synced, without actually syncing')
        parser.add_argument('--verbose', action='store_true', help='Show detailed information')
    
    def handle(self, *args, **options):
        force = options.get('force', False)
        dry_run = options.get('dry_run', False)
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.SUCCESS('Syncing unsynced quiz attempts with Academic Analyzer...'))
        
        # Check API configuration
        api_url = getattr(settings, 'ACADEMIC_ANALYZER_BASE_URL', None)
        
        if not api_url:
            self.stdout.write(self.style.ERROR(
                'ACADEMIC_ANALYZER_BASE_URL not configured in settings. '
                'Add it to settings.py or .env file.'
            ))
            return
        
        # Find tutorial quiz attempts that are completed but not synced
        query = QuizAttempt.objects.filter(
            completed_at__isnull=False,
            quiz__quiz_type='tutorial',
            quiz__course_id__isnull=False,
            quiz__tutorial_number__isnull=False
        )
        
        if not force:
            query = query.filter(marks_synced=False)
        
        attempts = query.select_related('quiz', 'user')
        
        if not attempts.exists():
            self.stdout.write(self.style.SUCCESS('No unsynced tutorial quiz attempts found.'))
            return
        
        self.stdout.write(f"Found {attempts.count()} tutorial quiz attempts to sync.")
        
        success_count = 0
        error_count = 0
        
        for attempt in attempts:
            quiz = attempt.quiz
            student_roll_number = attempt.user.username
            
            if verbose:
                self.stdout.write(f"\nProcessing attempt {attempt.id} by {student_roll_number} for quiz '{quiz.title}'")
            
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
            
            if verbose:
                self.stdout.write(f"  API payload: {api_data}")
            
            if dry_run:
                self.stdout.write(self.style.SUCCESS("  ✓ Would sync marks with Academic Analyzer API (dry run)"))
                success_count += 1
                continue
            
            try:
                # Send to Academic Analyzer API
                update_marks_url = f"{api_url.rstrip('/')}/staff/update-student-marks"
                
                if verbose:
                    self.stdout.write(f"  Sending request to {update_marks_url}")
                
                response = requests.post(
                    update_marks_url,
                    json=api_data,
                    timeout=10
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    self.stdout.write(self.style.SUCCESS(
                        f"  ✓ Successfully sent marks to Academic Analyzer API: {response.status_code}"
                    ))
                    
                    # Mark as synced
                    attempt.marks_synced = True
                    attempt.last_sync_at = timezone.now()
                    attempt.save()
                    
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR(
                        f"  ✗ API error: {response.status_code} - {response.text}"
                    ))
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Request error: {str(e)}"))
                error_count += 1
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\nDRY RUN completed: would sync {success_count} marks to Academic Analyzer API"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nSync completed: successfully sent {success_count} marks, encountered {error_count} errors"
            ))