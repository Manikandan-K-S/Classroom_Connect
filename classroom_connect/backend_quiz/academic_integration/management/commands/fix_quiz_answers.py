from django.core.management.base import BaseCommand
import logging
from quiz.models import Quiz, QuizAttempt, QuizAnswer, Question, Choice
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix quiz answers and ensure scores are calculated correctly'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
        parser.add_argument('--quiz', type=int, help='Fix answers for a specific quiz by ID')
        parser.add_argument('--attempt', type=int, help='Fix a specific attempt by ID')
        parser.add_argument('--recalculate-scores', action='store_true', help='Recalculate all scores')
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.SUCCESS('Starting to fix quiz answers...'))
        
        dry_run = options.get('dry_run', False)
        quiz_id = options.get('quiz')
        attempt_id = options.get('attempt')
        recalculate_scores = options.get('recalculate_scores', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no changes will be made'))
        
        # Get attempts to process
        attempts = QuizAttempt.objects.all()
        
        if quiz_id:
            attempts = attempts.filter(quiz_id=quiz_id)
            
        if attempt_id:
            attempts = attempts.filter(id=attempt_id)
        
        self.stdout.write(f"Found {attempts.count()} attempts to process")
        
        total_fixed = 0
        total_scores_updated = 0
        
        for attempt in attempts:
            self.stdout.write(f"\nProcessing attempt {attempt.id} by {attempt.user.username} for quiz '{attempt.quiz.title}'")
            
            # Get all questions for this quiz
            questions = Question.objects.filter(quiz=attempt.quiz)
            
            # Check if attempt has answers for all questions
            answers = QuizAnswer.objects.filter(attempt=attempt)
            missing_questions = []
            
            for question in questions:
                if not answers.filter(question=question).exists():
                    missing_questions.append(question)
            
            if missing_questions:
                self.stdout.write(self.style.WARNING(
                    f"  Attempt {attempt.id} is missing answers for {len(missing_questions)} questions"
                ))
                
                if not dry_run:
                    for question in missing_questions:
                        # Create a blank answer for this question
                        answer = QuizAnswer.objects.create(
                            attempt=attempt,
                            question=question,
                            is_correct=False,
                            points_earned=0
                        )
                        self.stdout.write(f"  Created blank answer for question {question.id}")
                        total_fixed += 1
            
            # Recalculate attempt score if needed
            if recalculate_scores or missing_questions:
                answers = QuizAnswer.objects.filter(attempt=attempt)
                
                # Recalculate all answers
                total_points = 0
                total_possible = 0
                
                for answer in answers:
                    question = answer.question
                    total_possible += question.points
                    
                    # Verify the correctness of each answer
                    selected_choices = answer.selected_choices.all()
                    
                    if question.question_type == 'mcq_single':
                        # Single choice question - only correct if exactly one correct choice is selected
                        correct_choices = Choice.objects.filter(question=question, is_correct=True)
                        
                        # Check if the selected choice matches the correct choice
                        if selected_choices.count() == 1 and selected_choices.filter(is_correct=True).exists():
                            if answer.is_correct != True or answer.points_earned != question.points:
                                self.stdout.write(f"  Fixing score for answer {answer.id} - should be correct")
                                
                                if not dry_run:
                                    answer.is_correct = True
                                    answer.points_earned = question.points
                                    answer.save()
                                    total_scores_updated += 1
                                
                            total_points += question.points
                        else:
                            if answer.is_correct != False or answer.points_earned != 0:
                                self.stdout.write(f"  Fixing score for answer {answer.id} - should be incorrect")
                                
                                if not dry_run:
                                    answer.is_correct = False
                                    answer.points_earned = 0
                                    answer.save()
                                    total_scores_updated += 1
                    
                    elif question.question_type == 'mcq_multiple':
                        # Multiple choice question - all correct choices must be selected and no incorrect ones
                        correct_choices = set(Choice.objects.filter(question=question, is_correct=True).values_list('id', flat=True))
                        selected_ids = set(selected_choices.values_list('id', flat=True))
                        
                        # Check if the selection exactly matches the correct choices
                        if correct_choices == selected_ids:
                            if answer.is_correct != True or answer.points_earned != question.points:
                                self.stdout.write(f"  Fixing score for answer {answer.id} - should be correct")
                                
                                if not dry_run:
                                    answer.is_correct = True
                                    answer.points_earned = question.points
                                    answer.save()
                                    total_scores_updated += 1
                                
                            total_points += question.points
                        else:
                            if answer.is_correct != False or answer.points_earned != 0:
                                self.stdout.write(f"  Fixing score for answer {answer.id} - should be incorrect")
                                
                                if not dry_run:
                                    answer.is_correct = False
                                    answer.points_earned = 0
                                    answer.save()
                                    total_scores_updated += 1
                    
                    elif question.question_type == 'true_false':
                        # True/False question
                        correct_choice = Choice.objects.filter(question=question, is_correct=True).first()
                        
                        # Check if the selected choice is correct
                        if selected_choices.count() == 1 and selected_choices.filter(id=correct_choice.id).exists():
                            if answer.is_correct != True or answer.points_earned != question.points:
                                self.stdout.write(f"  Fixing score for answer {answer.id} - should be correct")
                                
                                if not dry_run:
                                    answer.is_correct = True
                                    answer.points_earned = question.points
                                    answer.save()
                                    total_scores_updated += 1
                                
                            total_points += question.points
                        else:
                            if answer.is_correct != False or answer.points_earned != 0:
                                self.stdout.write(f"  Fixing score for answer {answer.id} - should be incorrect")
                                
                                if not dry_run:
                                    answer.is_correct = False
                                    answer.points_earned = 0
                                    answer.save()
                                    total_scores_updated += 1
                
                # Update the attempt score
                if attempt.score != total_points or attempt.total_possible != total_possible:
                    self.stdout.write(f"  Updating attempt {attempt.id} score from {attempt.score}/{attempt.total_possible} to {total_points}/{total_possible}")
                    
                    if not dry_run:
                        attempt.score = total_points
                        attempt.total_possible = total_possible
                        attempt.save()
                        total_scores_updated += 1
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\nDRY RUN completed: would fix {total_fixed} missing answers and update {total_scores_updated} scores"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nFixes completed: created {total_fixed} missing answers and updated {total_scores_updated} scores"
            ))