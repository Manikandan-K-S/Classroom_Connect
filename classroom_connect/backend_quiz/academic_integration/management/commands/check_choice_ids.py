from django.core.management.base import BaseCommand
import logging
from quiz.models import Question, Choice

class Command(BaseCommand):
    help = 'Check and fix quiz question choices to ensure they have consistent IDs'
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.SUCCESS('Starting to check quiz choice IDs...'))
        
        questions = Question.objects.all()
        self.stdout.write(f"Found {questions.count()} questions to process")
        
        for question in questions:
            self.stdout.write(f"\nExamining question {question.id}: '{question.text}'")
            choices = Choice.objects.filter(question=question).order_by('id')
            self.stdout.write(f"  Has {choices.count()} choices:")
            
            for i, choice in enumerate(choices):
                self.stdout.write(f"  - Choice {i+1}: ID={choice.id}, '{choice.text}', is_correct={choice.is_correct}")
                
            # Check if there are any missing IDs in sequence
            choice_ids = [choice.id for choice in choices]
            if choice_ids:
                min_id = min(choice_ids)
                max_id = max(choice_ids)
                expected_ids = set(range(min_id, min_id + choices.count()))
                actual_ids = set(choice_ids)
                
                missing_ids = expected_ids - actual_ids
                extra_ids = actual_ids - expected_ids
                
                if missing_ids:
                    self.stdout.write(self.style.WARNING(f"  ⚠️ Missing IDs in sequence: {missing_ids}"))
                if extra_ids:
                    self.stdout.write(self.style.WARNING(f"  ⚠️ Extra IDs outside expected sequence: {extra_ids}"))
                    
        self.stdout.write(self.style.SUCCESS('\nFinished checking quiz choice IDs'))