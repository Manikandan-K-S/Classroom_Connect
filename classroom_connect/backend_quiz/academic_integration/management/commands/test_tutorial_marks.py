from django.core.management.base import BaseCommand
import logging
import json
import requests
from django.conf import settings
from quiz.models import Quiz, QuizAttempt
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'Test tutorial marks integration with Academic Analyzer API'
    
    def add_arguments(self, parser):
        parser.add_argument('--quiz', type=int, help='Test with a specific quiz by ID')
        parser.add_argument('--attempt', type=int, help='Test with a specific attempt by ID')
        parser.add_argument('--dry-run', action='store_true', help='Do not actually send data to API')
        parser.add_argument('--force', action='store_true', help='Send data even if already sent')
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.SUCCESS('Testing tutorial marks integration with Academic Analyzer API...'))
        
        dry_run = options.get('dry_run', False)
        quiz_id = options.get('quiz')
        attempt_id = options.get('attempt')
        force = options.get('force', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no API calls will be made'))
            
        # Check API configuration
        api_url = getattr(settings, 'ACADEMIC_ANALYZER_BASE_URL', None)
        
        if not api_url:
            self.stdout.write(self.style.ERROR(
                'ACADEMIC_ANALYZER_BASE_URL not configured in settings. '
                'Add it to settings.py or .env file.'
            ))
            return
        
        # Get attempts to process - use completed_at to check if completed
        attempts = QuizAttempt.objects.filter(completed_at__isnull=False)
        
        if quiz_id:
            attempts = attempts.filter(quiz_id=quiz_id)
            
        if attempt_id:
            attempts = attempts.filter(id=attempt_id)
            
        if not force:
            # Filter out attempts that are already graded
            attempts = attempts.filter(status='submitted')
        
        self.stdout.write(f"Found {attempts.count()} attempts to process")
        
        success_count = 0
        error_count = 0
        
        for attempt in attempts:
            quiz = attempt.quiz
            course = None
            
            # Since we don't have a Course model, just use the course_id as our reference
            course_id = quiz.course_id
            
            if not course_id:
                self.stdout.write(self.style.WARNING(
                    f"Quiz {quiz.id} '{quiz.title}' is not linked to any course, skipping attempt {attempt.id}"
                ))
                continue
                
            # Prepare data for Academic Analyzer API - format for /staff/update-student-marks
            tutorial_number = quiz.tutorial_number if hasattr(quiz, 'tutorial_number') else 1
            
            # Calculate percentage as a value from 0-10 for the tutorial mark
            percentage = round((attempt.score / attempt.total_points * 10) if attempt.total_points else 0, 1)
            
            api_data = {
                'studentId': attempt.user.username,  # Use username as roll number
                'courseId': course_id,
                'teacherEmail': 'mks.mca@psgtech.ac.in',  # Use valid teacher email from login.txt
                'marks': {
                    f'tutorial{tutorial_number}': percentage  # Set the correct tutorial number
                }
            }
            
            self.stdout.write(f"\nProcessing attempt {attempt.id} by {attempt.user.username} for quiz '{quiz.title}'")
            self.stdout.write(f"  API payload: {json.dumps(api_data, indent=2)}")
            
            if not dry_run:
                try:
                    # Construct tutorial marks endpoint URL
                    tutorial_marks_url = f"{api_url.rstrip('/')}/staff/update-student-marks"
                    
                    # Prepare headers
                    headers = {'Content-Type': 'application/json'}
                    
                    # Make API call
                    self.stdout.write(f"  Sending request to {tutorial_marks_url}")
                    response = requests.post(
                        tutorial_marks_url,
                        json=api_data,
                        headers=headers,
                        timeout=10
                    )
                    
                    # Process response
                    if response.status_code == 200 or response.status_code == 201:
                        self.stdout.write(self.style.SUCCESS(
                            f"  ✓ Successfully sent marks to Academic Analyzer API: {response.status_code}"
                        ))
                        
                        # Mark as synced
                        # First check if these fields exist in the model
                        if hasattr(attempt, 'marks_synced') and hasattr(attempt, 'last_sync_at'):
                            attempt.marks_synced = True
                            attempt.last_sync_at = timezone.now()
                            attempt.save()
                        else:
                            self.stdout.write(self.style.WARNING(
                                "  ⚠ Could not update marks_synced status - fields not found in QuizAttempt model"
                            ))
                        
                        success_count += 1
                    else:
                        self.stdout.write(self.style.ERROR(
                            f"  ✗ API error: {response.status_code} - {response.text}"
                        ))
                        error_count += 1
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Request error: {str(e)}"))
                    error_count += 1
            else:
                self.stdout.write(self.style.SUCCESS("  ✓ Would send marks to Academic Analyzer API (dry run)"))
                success_count += 1
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\nDRY RUN completed: would send {success_count} marks to Academic Analyzer API"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nTest completed: successfully sent {success_count} marks, encountered {error_count} errors"
            ))