from django.core.management.base import BaseCommand
import logging
from quiz.models import Quiz, QuizAttempt, QuizAnswer, Question, Choice

class Command(BaseCommand):
    help = 'Clean up quiz data and fix inconsistencies'
    
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        self.stdout.write(self.style.SUCCESS('Starting quiz data cleanup...'))
        
        # Check for quiz attempts with missing answers
        attempts = QuizAttempt.objects.all()
        self.stdout.write(f"Found {attempts.count()} quiz attempts to process")
        
        for attempt in attempts:
            self.stdout.write(f"\nExamining attempt {attempt.id} by {attempt.student} for quiz: {attempt.quiz}")
            answers = QuizAnswer.objects.filter(attempt=attempt)
            questions = Question.objects.filter(quiz=attempt.quiz)
            
            self.stdout.write(f"  Quiz has {questions.count()} questions")
            self.stdout.write(f"  Attempt has {answers.count()} answers")
            
            # Check for questions without answers
            answered_question_ids = [answer.question.id for answer in answers]
            all_question_ids = [q.id for q in questions]
            unanswered_questions = [qid for qid in all_question_ids if qid not in answered_question_ids]
            
            if unanswered_questions:
                self.stdout.write(self.style.WARNING(f"  ⚠️ Found {len(unanswered_questions)} questions without answers: {unanswered_questions}"))
            
            # Check for answers with non-existent choices
            for answer in answers:
                try:
                    if not Choice.objects.filter(id=answer.selected_choice_id, question=answer.question).exists():
                        self.stdout.write(self.style.ERROR(
                            f"  ❌ Answer {answer.id} references choice ID {answer.selected_choice_id} "
                            f"which does not exist for question {answer.question.id}"
                        ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"  ❌ Error checking answer {answer.id}: {str(e)}"
                    ))
            
            # Calculate and verify score
            correct_answers = 0
            for answer in answers:
                try:
                    choice = Choice.objects.get(id=answer.selected_choice_id)
                    if choice.is_correct:
                        correct_answers += 1
                except Choice.DoesNotExist:
                    pass
            
            calculated_score = correct_answers
            stored_score = attempt.score
            
            if calculated_score != stored_score:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠️ Score mismatch: Stored={stored_score}, Calculated={calculated_score}"
                ))
        
        self.stdout.write(self.style.SUCCESS('\nFinished cleaning up quiz data'))