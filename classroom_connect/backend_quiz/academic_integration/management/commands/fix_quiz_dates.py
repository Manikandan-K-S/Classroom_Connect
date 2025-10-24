from django.core.management.base import BaseCommand
import logging
from django.utils import timezone
from quiz.models import Quiz

class Command(BaseCommand):
    help = 'Fix timezone issues in quiz start and completion dates'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.SUCCESS('Starting to fix quiz dates...'))
        
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no changes will be made'))
            
        # Get all quizzes
        quizzes = Quiz.objects.all()
        self.stdout.write(f"Found {quizzes.count()} quizzes to check")
        
        fixed_count = 0
        
        for quiz in quizzes:
            has_issues = False
            
            # Check start_date
            if quiz.start_date and timezone.is_naive(quiz.start_date):
                self.stdout.write(f"Quiz {quiz.id} '{quiz.title}' has naive start_date: {quiz.start_date}")
                
                aware_date = timezone.make_aware(quiz.start_date)
                self.stdout.write(f"  Would convert to: {aware_date}")
                
                if not dry_run:
                    quiz.start_date = aware_date
                    has_issues = True
                
            # Check complete_by_date
            if quiz.complete_by_date and timezone.is_naive(quiz.complete_by_date):
                self.stdout.write(f"Quiz {quiz.id} '{quiz.title}' has naive complete_by_date: {quiz.complete_by_date}")
                
                aware_date = timezone.make_aware(quiz.complete_by_date)
                self.stdout.write(f"  Would convert to: {aware_date}")
                
                if not dry_run:
                    quiz.complete_by_date = aware_date
                    has_issues = True
            
            # Save if needed
            if has_issues and not dry_run:
                self.stdout.write(self.style.SUCCESS(f"Fixing dates for quiz {quiz.id}"))
                quiz.save()
                fixed_count += 1
                
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"\nDRY RUN completed: would fix {fixed_count} quizzes"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\nFixes completed: fixed {fixed_count} quizzes"))