from django.core.management.base import BaseCommand
import logging
from quiz.models import Question, Choice, Quiz

class Command(BaseCommand):
    help = 'Repair quiz choice IDs to ensure they are sequential and consistent'
    
    def add_arguments(self, parser):
        parser.add_argument('--quiz', type=int, help='Fix a specific quiz by ID')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.SUCCESS('Starting to repair quiz choice IDs...'))
        
        dry_run = options.get('dry_run', False)
        quiz_id = options.get('quiz')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no changes will be made'))
            
        # Get quizzes to process
        if quiz_id:
            quizzes = Quiz.objects.filter(id=quiz_id)
            if not quizzes.exists():
                self.stdout.write(self.style.ERROR(f'Quiz with ID {quiz_id} not found'))
                return
        else:
            quizzes = Quiz.objects.all()
            
        self.stdout.write(f"Found {quizzes.count()} quizzes to process")
        
        total_questions = 0
        total_choices = 0
        total_questions_fixed = 0
        total_choices_fixed = 0
        
        # Process each quiz
        for quiz in quizzes:
            self.stdout.write(f"\nExamining quiz {quiz.id}: '{quiz.title}'")
            
            # Get all questions for this quiz
            questions = Question.objects.filter(quiz=quiz).order_by('id')
            self.stdout.write(f"  Quiz has {questions.count()} questions")
            
            total_questions += questions.count()
            
            # Process each question
            for question in questions:
                choices = Choice.objects.filter(question=question).order_by('id')
                total_choices += choices.count()
                
                self.stdout.write(f"  - Question {question.id}: '{question.text}' has {choices.count()} choices")
                
                # Check if choices need fixing
                choices_need_fixing = False
                
                # Check for duplicate order values
                order_counts = {}
                for choice in choices:
                    if choice.order in order_counts:
                        order_counts[choice.order] += 1
                    else:
                        order_counts[choice.order] = 1
                        
                duplicate_orders = [order for order, count in order_counts.items() if count > 1]
                if duplicate_orders:
                    self.stdout.write(self.style.WARNING(f"    ⚠️ Found duplicate order values: {duplicate_orders}"))
                    choices_need_fixing = True
                
                # Check for missing or non-sequential order values
                if choices.exists():
                    expected_orders = list(range(len(choices)))
                    actual_orders = sorted([choice.order for choice in choices])
                    
                    if expected_orders != actual_orders:
                        self.stdout.write(self.style.WARNING(
                            f"    ⚠️ Order values are not sequential: {actual_orders}, expected: {expected_orders}"
                        ))
                        choices_need_fixing = True
                
                # Fix choices if needed
                if choices_need_fixing:
                    total_questions_fixed += 1
                    self.stdout.write(f"    Fixing order values for {choices.count()} choices")
                    
                    for i, choice in enumerate(choices):
                        if choice.order != i:
                            self.stdout.write(f"    - Updating choice {choice.id} order from {choice.order} to {i}")
                            total_choices_fixed += 1
                            
                            if not dry_run:
                                choice.order = i
                                choice.save()
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\nDRY RUN completed: would fix {total_questions_fixed}/{total_questions} questions "
                f"and {total_choices_fixed}/{total_choices} choices"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nRepairs completed: fixed {total_questions_fixed}/{total_questions} questions "
                f"and {total_choices_fixed}/{total_choices} choices"
            ))