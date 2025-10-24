from django.core.management.base import BaseCommand
import logging
import requests
from django.conf import settings
from quiz.models import Quiz, QuizAttempt

class Command(BaseCommand):
    help = 'Integrate quiz results with Academic Analyzer API for tutorial marks'
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.SUCCESS('Starting quiz integration with Academic Analyzer...'))
        
        # Find all quiz attempts that have been completed but not yet integrated
        attempts = QuizAttempt.objects.filter(
            status='submitted',
            completed_at__isnull=False,
            quiz__quiz_type='tutorial',
            quiz__tutorial_number__isnull=False,
            quiz__course_id__isnull=False
        ).select_related('quiz', 'user')
        
        self.stdout.write(f"Found {attempts.count()} quiz attempts to integrate")
        
        # Get base URL for Academic Analyzer API
        try:
            base_url = getattr(settings, "ACADEMIC_ANALYZER_BASE_URL", "http://localhost:5000").rstrip("/")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error getting Academic Analyzer API URL: {e}"))
            return
            
        success_count = 0
        error_count = 0
        
        for attempt in attempts:
            self.stdout.write(f"\nProcessing quiz attempt {attempt.id} by {attempt.user.username}")
            
            # Skip if the user doesn't have a valid username (assumed to be student roll number)
            if not attempt.user.username:
                self.stdout.write(self.style.WARNING(f"  User has no username, skipping"))
                error_count += 1
                continue
                
            # Format the score for academic analyzer - scale to 0-100%
            scaled_score = attempt.percentage
            
            try:
                # Call Academic Analyzer API to update tutorial marks
                update_marks_response = requests.post(
                    f"{base_url}/student/tutorial-marks",
                    json={
                        "rollno": attempt.user.username,
                        "courseId": attempt.quiz.course_id,
                        "tutorialNumber": attempt.quiz.tutorial_number,
                        "marks": scaled_score
                    },
                    timeout=5
                )
                
                if update_marks_response.ok:
                    try:
                        marks_data = update_marks_response.json()
                        if marks_data.get('success'):
                            self.stdout.write(self.style.SUCCESS(
                                f"  ✓ Successfully updated tutorial marks for student {attempt.user.username} "
                                f"in course {attempt.quiz.course_id}, tutorial {attempt.quiz.tutorial_number}: {scaled_score}%"
                            ))
                            
                            # Mark attempt as integrated
                            attempt.status = 'graded'
                            attempt.save()
                            
                            success_count += 1
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"  ⚠️ API returned failure: {marks_data.get('message', 'Unknown error')}"
                            ))
                            error_count += 1
                    except ValueError:
                        self.stdout.write(self.style.ERROR(f"  ❌ Invalid JSON response from API"))
                        error_count += 1
                else:
                    self.stdout.write(self.style.ERROR(
                        f"  ❌ API responded with status code: {update_marks_response.status_code}"
                    ))
                    error_count += 1
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Request error: {e}"))
                error_count += 1
                
        self.stdout.write(self.style.SUCCESS(
            f"\nFinished integration: {success_count} successful, {error_count} errors"
        ))