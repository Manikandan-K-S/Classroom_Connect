from django.core.management.base import BaseCommand
from django.utils import timezone
from quiz.models import Quiz
import datetime
import logging

class Command(BaseCommand):
    help = 'Fix quiz dates that may have been stored incorrectly, causing availability issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without actually changing the database',
        )
        parser.add_argument(
            '--quiz-id',
            type=int,
            help='Fix a specific quiz by ID',
        )
        parser.add_argument(
            '--log-file',
            type=str,
            help='Path to save detailed logs',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        quiz_id = options['quiz_id']
        log_file = options.get('log_file')
        
        # Configure logging
        if log_file:
            logging.basicConfig(
                filename=log_file,
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        
        logger = logging.getLogger(__name__)
        
        # Query to get relevant quizzes
        if quiz_id:
            quizzes = Quiz.objects.filter(id=quiz_id)
            self.stdout.write(f"Checking quiz with ID {quiz_id}")
            logger.info(f"Checking quiz with ID {quiz_id}")
        else:
            quizzes = Quiz.objects.all()
            self.stdout.write(f"Checking all quizzes in the database ({quizzes.count()} total)")
            logger.info(f"Checking all quizzes in the database ({quizzes.count()} total)")
        
        now = timezone.now()
        fixed_count = 0
        no_issue_count = 0
        
        for quiz in quizzes:
            has_issue = False
            
            # Check if start_date is naive (not timezone-aware)
            if quiz.start_date and timezone.is_naive(quiz.start_date):
                has_issue = True
                self.stdout.write(self.style.WARNING(f"Quiz {quiz.id} '{quiz.title}' has naive start_date: {quiz.start_date}"))
                logger.warning(f"Quiz {quiz.id} has naive start_date: {quiz.start_date}")
                
                # Make it timezone-aware
                if not dry_run:
                    aware_start_date = timezone.make_aware(quiz.start_date)
                    quiz.start_date = aware_start_date
                    self.stdout.write(f"  → Fixed to: {aware_start_date}")
                    logger.info(f"Fixed start_date to: {aware_start_date}")
            
            # Check if complete_by_date is naive (not timezone-aware)
            if quiz.complete_by_date and timezone.is_naive(quiz.complete_by_date):
                has_issue = True
                self.stdout.write(self.style.WARNING(f"Quiz {quiz.id} '{quiz.title}' has naive complete_by_date: {quiz.complete_by_date}"))
                logger.warning(f"Quiz {quiz.id} has naive complete_by_date: {quiz.complete_by_date}")
                
                # Make it timezone-aware
                if not dry_run:
                    aware_complete_by_date = timezone.make_aware(quiz.complete_by_date)
                    quiz.complete_by_date = aware_complete_by_date
                    self.stdout.write(f"  → Fixed to: {aware_complete_by_date}")
                    logger.info(f"Fixed complete_by_date to: {aware_complete_by_date}")
            
            # Check for future start dates that may be preventing quiz availability
            if quiz.start_date and quiz.start_date > now:
                self.stdout.write(self.style.WARNING(f"Quiz {quiz.id} '{quiz.title}' has future start_date: {quiz.start_date}"))
                logger.warning(f"Quiz {quiz.id} has future start_date: {quiz.start_date} (not an issue if intended)")
            
            # Save the changes if needed and not in dry-run mode
            if has_issue and not dry_run:
                quiz.save()
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(f"Fixed quiz {quiz.id} '{quiz.title}'"))
                logger.info(f"Fixed quiz {quiz.id} '{quiz.title}'")
            elif not has_issue:
                no_issue_count += 1
            
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run completed. {quizzes.count() - no_issue_count} quizzes would be fixed."))
            logger.info(f"Dry run completed. {quizzes.count() - no_issue_count} quizzes would be fixed.")
        else:
            self.stdout.write(self.style.SUCCESS(f"Fixed {fixed_count} quizzes. {no_issue_count} quizzes had no issues."))
            logger.info(f"Fixed {fixed_count} quizzes. {no_issue_count} quizzes had no issues.")