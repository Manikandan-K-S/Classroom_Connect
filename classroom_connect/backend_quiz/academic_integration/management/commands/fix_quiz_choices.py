from django.core.management.base import BaseCommand
import logging
from quiz.models import Question, Choice

class Command(BaseCommand):
    help = 'Fix missing choices for quiz questions'
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.SUCCESS('Starting to fix quiz choices...'))
        
        questions = Question.objects.all()
        self.stdout.write(f"Found {questions.count()} questions to process")
        
        fixed_count = 0
        
        for question in questions:
            choices = Choice.objects.filter(question=question)
            
            if not choices.exists():
                self.stdout.write(self.style.WARNING(f"Question ID {question.id} has no choices, creating default options"))
                
                # Create default choices based on question type
                if question.question_type == 'mcq_single' or question.question_type == 'mcq_multiple':
                    # Create 4 options
                    for i in range(4):
                        is_correct = i == 0  # Make the first option correct by default
                        Choice.objects.create(
                            question=question,
                            text=f"Option {i + 1}",
                            is_correct=is_correct,
                            order=i
                        )
                    self.stdout.write(self.style.SUCCESS(f"Created 4 options for question ID {question.id}"))
                    fixed_count += 1
                    
                elif question.question_type == 'true_false':
                    # Create True and False options
                    true_choice = Choice.objects.create(
                        question=question,
                        text="True",
                        is_correct=question.correct_answer in ('True', 'true', True, '1', 1),
                        order=0
                    )
                    false_choice = Choice.objects.create(
                        question=question,
                        text="False",
                        is_correct=question.correct_answer in ('False', 'false', False, '0', 0),
                        order=1
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created True/False options for question ID {question.id}"))
                    fixed_count += 1
            else:
                self.stdout.write(f"Question ID {question.id} already has {choices.count()} choices")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed choices for {fixed_count} questions'))