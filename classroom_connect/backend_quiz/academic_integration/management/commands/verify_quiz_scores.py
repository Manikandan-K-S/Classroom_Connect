from django.core.management.base import BaseCommand, CommandError
import logging
from quiz.models import Quiz, QuizAttempt, Question, Choice
from django.db.models import Count

class Command(BaseCommand):
    help = 'Verify quiz data consistency and update scores if needed'
    
    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='Fix any consistency issues that are found')
        parser.add_argument('--quiz', type=int, help='Check a specific quiz by ID')
        parser.add_argument('--student', type=str, help='Check attempts for a specific student by roll number')
    
    def handle(self, *args, **options):
        fix_mode = options['fix']
        quiz_id = options.get('quiz')
        student = options.get('student')
        
        self.stdout.write(self.style.SUCCESS('Starting quiz consistency check...'))
        self.stdout.write(f"Fix mode: {'ENABLED' if fix_mode else 'DISABLED (dry run)'}")
        
        # Get attempts to check
        attempts_query = QuizAttempt.objects.filter(
            completed_at__isnull=False
        ).select_related('quiz', 'user')
        
        # Filter by quiz if specified
        if quiz_id:
            attempts_query = attempts_query.filter(quiz_id=quiz_id)
            self.stdout.write(f"Filtering by quiz ID: {quiz_id}")
            
        # Filter by student if specified
        if student:
            attempts_query = attempts_query.filter(user__username=student)
            self.stdout.write(f"Filtering by student: {student}")
        
        attempts = attempts_query.all()
        self.stdout.write(f"Found {attempts.count()} completed quiz attempts to check")
        
        fixed_count = 0
        error_count = 0
        
        for attempt in attempts:
            self.stdout.write(f"\nChecking quiz attempt {attempt.id} by {attempt.user.username} for quiz: {attempt.quiz.title}")
            
            # Get all answers for this attempt
            answers = attempt.answers.all().select_related('question')
            
            # Calculate the correct score
            total_points = 0
            earned_points = 0
            
            for answer in answers:
                total_points += answer.question.points
                earned_points += answer.points_earned
                
            # Verify the total points is accurate
            if attempt.total_points != total_points:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠️ Total points mismatch: stored={attempt.total_points}, calculated={total_points}"
                ))
                
                if fix_mode:
                    attempt.total_points = total_points
                    
            # Verify the score is accurate
            if attempt.score != earned_points:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠️ Score mismatch: stored={attempt.score}, calculated={earned_points}"
                ))
                
                if fix_mode:
                    attempt.score = earned_points
                    
            # Verify percentage is accurate
            correct_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
            if abs(attempt.percentage - correct_percentage) > 0.01:  # Allow for slight floating point differences
                self.stdout.write(self.style.WARNING(
                    f"  ⚠️ Percentage mismatch: stored={attempt.percentage:.2f}%, calculated={correct_percentage:.2f}%"
                ))
                
                if fix_mode:
                    attempt.percentage = correct_percentage
                    
            # Verify passed status is accurate
            correct_passed = (correct_percentage >= attempt.quiz.passing_score)
            if attempt.passed != correct_passed:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠️ Passed status mismatch: stored={attempt.passed}, calculated={correct_passed}"
                ))
                
                if fix_mode:
                    attempt.passed = correct_passed
                    
            # Check if this attempt needs to be integrated with Academic Analyzer
            if (attempt.quiz.quiz_type == 'tutorial' and attempt.quiz.tutorial_number and 
                attempt.quiz.course_id and attempt.status != 'graded'):
                self.stdout.write(self.style.WARNING(
                    f"  ⚠️ Tutorial quiz result not integrated with Academic Analyzer"
                ))
                
                if fix_mode:
                    attempt.status = 'submitted'  # Mark for integration
                    
            # Save changes if in fix mode
            if fix_mode and attempt.is_dirty():
                self.stdout.write(self.style.SUCCESS(f"  ✓ Fixing score data for attempt {attempt.id}"))
                attempt.save()
                fixed_count += 1
                
        self.stdout.write(self.style.SUCCESS(
            f"\nFinished consistency check: {fixed_count} attempts fixed, {error_count} errors"
        ))
        
        if not fix_mode and fixed_count > 0:
            self.stdout.write(self.style.WARNING(
                f"Run with --fix to apply the {fixed_count} fixes identified in this dry run"
            ))