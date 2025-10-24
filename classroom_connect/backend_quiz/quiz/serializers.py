from rest_framework import serializers
from django.utils import timezone
from .models import Quiz, Question, Choice, QuizAttempt, User

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "text", "is_correct"]

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "question_type", "choices", "order"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            "id", "title", "description", "created_at", "start_date", 
            "complete_by_date", "course_id", "tutorial_number", "questions", 
            "created_by", "quiz_type", "duration_minutes", "is_active", 
            "show_results", "allow_review", "is_ended", "is_available", 
            "is_mock_test"
        ]

class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    graded_by = UserSerializer(read_only=True)
    time_remaining_seconds = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'user', 'started_at', 'completed_at', 
            'score', 'total_questions', 'percentage', 'status',
            'feedback', 'graded_by', 'time_remaining_seconds'
        ]
