"""
Management command to manually trigger synchronization of quiz attempts with Academic Analyzer.
"""
import logging
import requests
import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from quiz.models import QuizAttempt
from academic_integration.utils import api_base_url

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Manually trigger synchronization of quiz attempts with Academic Analyzer"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync all tutorial quiz attempts, even if already synced',
        )
        parser.add_argument(
            '--attempt-id',
            type=int,
            help='Sync only the specified attempt ID',
        )
        parser.add_argument(
            '--student',
            type=str,
            help='Sync only attempts by the specified student username',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Do not actually sync, just show what would be synced',
        )

    def handle(self, *args, **options):
        api_url = api_base_url()
        self.stdout.write(self.style.SUCCESS(f'Using Academic Analyzer API: {api_url}'))
        
        # Build the query based on command arguments
        query = {
            'completed_at__isnull': False,
            'quiz__quiz_type': 'tutorial',
            'quiz__course_id__isnull': False,
            'quiz__tutorial_number__isnull': False,
        }
        
        # Add filters based on options
        if not options['force']:
            query['marks_synced'] = False
            
        if options['attempt_id']:
            query['id'] = options['attempt_id']
            
        if options['student']:
            query['user__username'] = options['student']
            
        # Find matching quiz attempts
        attempts = QuizAttempt.objects.filter(**query).select_related('quiz', 'user')
        
        if not attempts.exists():
            self.stdout.write(self.style.SUCCESS('No matching tutorial quiz attempts found to sync'))
            return
            
        self.stdout.write(self.style.SUCCESS(f'Found {attempts.count()} tutorial quiz attempts to sync'))
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry run mode - no actual syncing'))
            for attempt in attempts:
                quiz = attempt.quiz
                self.stdout.write(
                    f'Would sync: Student {attempt.user.username}, ' +
                    f'Quiz {quiz.title}, Tutorial {quiz.tutorial_number}, ' +
                    f'Course {quiz.course_id}, Score {attempt.percentage/10}/10'
                )
            return
            
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
            
            self.stdout.write(
                f'Syncing attempt {attempt.id}: Student {student_roll_number}, ' +
                f'Quiz {quiz.title}, Tutorial {tutorial_number}, ' +
                f'Course {quiz.course_id}, Score {scaled_score}/10'
            )
            
            try:
                # Send to Academic Analyzer API
                update_marks_url = f"{api_base_url()}/staff/update-student-marks"
                
                response = requests.post(
                    update_marks_url,
                    json=api_data,
                    timeout=10
                )
                
                if response.status_code == 200 or response.status_code == 201:
                    self.stdout.write(self.style.SUCCESS(f'  Success! API response: {response.text}'))
                    
                    # Mark as synced
                    attempt.marks_synced = True
                    attempt.last_sync_at = timezone.now()
                    attempt.save()
                    
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  API error: {response.status_code} - {response.text}'
                        )
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Request error: {str(e)}'))
                error_count += 1
                
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        self.stdout.write('-------------------------------------------')
        self.stdout.write(
            self.style.SUCCESS(
                f'Sync completed: successfully sent {success_count} marks, encountered {error_count} errors'
            )
        )