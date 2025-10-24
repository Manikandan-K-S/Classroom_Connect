from django.core.management.base import BaseCommand
import logging
import json
import requests
from django.conf import settings
from quiz.models import Quiz, QuizAttempt
from django.db.models import Count

class Command(BaseCommand):
    help = 'Check quiz relationships with academic_analyzer models'
    
    def add_arguments(self, parser):
        parser.add_argument('--verbose', action='store_true', help='Show detailed information')
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        verbose = options.get('verbose', False)
        self.stdout.write(self.style.SUCCESS('Checking quiz relationships with academic_analyzer...'))
        
        # Check if quizzes have course_id
        quizzes = Quiz.objects.all()
        quizzes_with_course = quizzes.exclude(course_id__isnull=True).exclude(course_id='')
        quizzes_without_course = quizzes.filter(course_id__isnull=True) | quizzes.filter(course_id='')
        
        self.stdout.write(f"Total quizzes: {quizzes.count()}")
        self.stdout.write(f"Quizzes with course_id: {quizzes_with_course.count()}")
        self.stdout.write(f"Quizzes without course_id: {quizzes_without_course.count()}")
        
        if quizzes_without_course.exists() and verbose:
            self.stdout.write("\nQuizzes without course_id:")
            for quiz in quizzes_without_course:
                self.stdout.write(f"  - Quiz {quiz.id}: {quiz.title}")
        
        # Check if quizzes have tutorial_number (for tutorial quizzes)
        tutorial_quizzes = quizzes.filter(quiz_type='tutorial')
        tutorial_quizzes_with_number = tutorial_quizzes.exclude(tutorial_number__isnull=True)
        tutorial_quizzes_without_number = tutorial_quizzes.filter(tutorial_number__isnull=True)
        
        self.stdout.write(f"\nTotal tutorial quizzes: {tutorial_quizzes.count()}")
        self.stdout.write(f"Tutorial quizzes with tutorial_number: {tutorial_quizzes_with_number.count()}")
        self.stdout.write(f"Tutorial quizzes without tutorial_number: {tutorial_quizzes_without_number.count()}")
        
        if tutorial_quizzes_without_number.exists() and verbose:
            self.stdout.write("\nTutorial quizzes without tutorial_number:")
            for quiz in tutorial_quizzes_without_number:
                self.stdout.write(f"  - Quiz {quiz.id}: {quiz.title}")
        
        # Check quiz attempts that have been completed but not graded
        completed_attempts = QuizAttempt.objects.filter(
            completed_at__isnull=False
        )
        
        ungraded_tutorial_attempts = completed_attempts.filter(
            quiz__quiz_type='tutorial',
            marks_synced=False  # Check for marks_synced flag
        )
        
        self.stdout.write(f"\nTotal completed quiz attempts: {completed_attempts.count()}")
        self.stdout.write(f"Tutorial attempts not synced with Academic Analyzer: {ungraded_tutorial_attempts.count()}")
        
        if ungraded_tutorial_attempts.exists() and verbose:
            self.stdout.write("\nUnsynced tutorial attempts:")
            for attempt in ungraded_tutorial_attempts:
                self.stdout.write(
                    f"  - Attempt {attempt.id}: Quiz '{attempt.quiz.title}' by {attempt.user.username} "
                    f"completed on {attempt.completed_at.strftime('%Y-%m-%d %H:%M:%S')}"
                )
        
        # Check API configuration
        api_url = getattr(settings, 'ACADEMIC_ANALYZER_BASE_URL', None)
        
        self.stdout.write("\nAPI Configuration:")
        if api_url:
            self.stdout.write(self.style.SUCCESS(f"  ✓ API URL is configured: {api_url}"))
        else:
            self.stdout.write(self.style.ERROR("  ✗ API URL is not configured (ACADEMIC_ANALYZER_BASE_URL)"))
        
        # Summary
        self.stdout.write("\nSummary:")
        
        if quizzes_without_course.exists():
            self.stdout.write(self.style.WARNING(
                f"  ⚠ {quizzes_without_course.count()} quizzes need course_id"
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ All quizzes have course_id"))
            
        if tutorial_quizzes_without_number.exists():
            self.stdout.write(self.style.WARNING(
                f"  ⚠ {tutorial_quizzes_without_number.count()} tutorial quizzes need tutorial_number"
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ All tutorial quizzes have tutorial_number"))
            
        if ungraded_tutorial_attempts.exists():
            self.stdout.write(self.style.WARNING(
                f"  ⚠ {ungraded_tutorial_attempts.count()} tutorial attempts need to be synced with Academic Analyzer"
            ))
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ All tutorial attempts are synced with Academic Analyzer"))
            
        if api_url:
            self.stdout.write(self.style.SUCCESS("  ✓ API configuration is complete"))
        else:
            self.stdout.write(self.style.WARNING("  ⚠ API configuration is incomplete"))
        
        self.stdout.write("\nRecommended actions:")
        
        if quizzes_without_course.exists():
            self.stdout.write("  - Assign course_id to quizzes without it")
            
        if tutorial_quizzes_without_number.exists():
            self.stdout.write("  - Assign tutorial_number to tutorial quizzes without it")
            
        if ungraded_tutorial_attempts.exists():
            self.stdout.write(
                "  - Run 'python manage.py test_tutorial_marks' to sync tutorial quiz results with Academic Analyzer"
            )
            
        if not api_url:
            self.stdout.write("  - Configure ACADEMIC_ANALYZER_BASE_URL in settings.py")