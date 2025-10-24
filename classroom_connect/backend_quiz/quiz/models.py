from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Fix related_name conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='quiz_user_set',
        related_query_name='quiz_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='quiz_user_set',
        related_query_name='quiz_user',
    )
    
    def is_student(self):
        return self.role == 'student'
    
    def is_admin(self):
        return self.role == 'admin'


class Quiz(models.Model):
    """
    Represents a quiz that can be assigned to courses from Academic Analyzer
    """
    QUIZ_TYPES = [
        ('tutorial', 'Tutorial Quiz'),
        ('mock', 'Mock Test'),
        ('exam', 'Examination'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Optional description of the quiz")
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True, help_text="Start date and time of the quiz")
    complete_by_date = models.DateTimeField(null=True, blank=True, help_text="Optional deadline for quiz completion")
    course_id = models.CharField(max_length=100, null=True, blank=True, help_text="Academic Analyzer Course ID")
    tutorial_number = models.IntegerField(null=True, blank=True, help_text="Tutorial number (1-4) in Academic Analyzer")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_quizzes", null=True, blank=True)
    quiz_type = models.CharField(max_length=10, choices=QUIZ_TYPES, default='tutorial')
    duration_minutes = models.IntegerField(default=30, help_text="Duration of the quiz in minutes")
    passing_score = models.FloatField(default=50.0, help_text="Minimum percentage required to pass the quiz")
    allow_retake = models.BooleanField(default=False, help_text="Whether students can retake the quiz if they fail")
    is_active = models.BooleanField(default=True, help_text="Whether the quiz is currently active")
    show_results = models.BooleanField(default=True, help_text="Whether to show results immediately after submission")
    allow_review = models.BooleanField(default=True, help_text="Whether students can review their answers after completion")
    is_ended = models.BooleanField(default=False, help_text="Whether the quiz has been ended by the teacher")
    
    @property
    def is_mock_test(self):
        return self.quiz_type == 'mock' or not self.tutorial_number
        
    @property
    def is_available(self):
        """Check if the quiz is available to take based on dates and active status"""
        now = timezone.now()
        # If quiz has been manually ended by teacher
        if self.is_ended:
            return False
        # If quiz is not active
        if not self.is_active:
            return False
        # If start date is set and it's in the future
        if self.start_date:
            # Ensure start_date is timezone aware before comparison
            start_date = timezone.make_aware(self.start_date) if timezone.is_naive(self.start_date) else self.start_date
            if now < start_date:
                return False
        # If deadline is set and it's in the past
        if self.complete_by_date:
            # Ensure complete_by_date is timezone aware before comparison
            complete_by_date = timezone.make_aware(self.complete_by_date) if timezone.is_naive(self.complete_by_date) else self.complete_by_date
            if now > complete_by_date:
                return False
        return True

    def debug_visibility_status(self):
        """
        Debug method to explain why a quiz might not be visible
        Returns a tuple of (is_visible, reason)
        """
        now = timezone.now()
        
        if not self.is_active:
            return False, "Quiz is not active (is_active=False)"
            
        if self.is_ended:
            return False, "Quiz has been manually ended by teacher (is_ended=True)"
            
        if self.start_date:
            # Check if start_date is naive and report it
            start_is_naive = timezone.is_naive(self.start_date)
            if start_is_naive:
                # Make it aware for proper comparison
                aware_start = timezone.make_aware(self.start_date)
                if now < aware_start:
                    return False, f"Quiz start date ({self.start_date}) is in the future (TIMEZONE ISSUE: naive datetime)"
            else:
                if now < self.start_date:
                    return False, f"Quiz start date ({self.start_date}) is in the future"
                    
        if self.complete_by_date:
            # Check if complete_by_date is naive and report it
            complete_is_naive = timezone.is_naive(self.complete_by_date)
            if complete_is_naive:
                # Make it aware for proper comparison
                aware_complete = timezone.make_aware(self.complete_by_date)
                if now > aware_complete:
                    return False, f"Quiz deadline ({self.complete_by_date}) has passed (TIMEZONE ISSUE: naive datetime)"
            else:
                if now > self.complete_by_date:
                    return False, f"Quiz deadline ({self.complete_by_date}) has passed"
            
        # Check if quiz has questions
        question_count = self.questions.count()
        if question_count == 0:
            return False, "Quiz has no questions"
            
        return True, "Quiz should be visible"
            
    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Represents a question in a quiz
    """
    QUESTION_TYPES = [
        ('mcq_single', 'Multiple Choice (Single Answer)'),
        ('mcq_multiple', 'Multiple Choice (Multiple Answers)'),
        ('text', 'Text Input'),
        ('true_false', 'True or False'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq_single')
    points = models.IntegerField(default=1)  # Points awarded for correct answer
    order = models.PositiveIntegerField(default=0)
    correct_answer = models.CharField(max_length=500, blank=True, null=True, help_text="Correct answer for text or true/false questions")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class Choice(models.Model):
    """
    Represents an answer choice for a question
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    """
    Records a student's attempt at a quiz
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)  # Added for point-based scoring
    percentage = models.FloatField(default=0.0)
    duration_seconds = models.IntegerField(default=0)  # Track how long the attempt took
    passed = models.BooleanField(default=False)  # Whether the attempt was passed
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="graded_attempts", null=True, blank=True)
    marks_synced = models.BooleanField(default=False)  # Track if marks were synced with Academic Analyzer
    last_sync_at = models.DateTimeField(null=True, blank=True)  # When marks were last synced
    
    class Meta:
        unique_together = ['user', 'quiz']  # One attempt per user per quiz
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.percentage}%)"
        
    @property
    def time_remaining_seconds(self):
        """Calculate remaining time in seconds"""
        if not self.started_at or not self.quiz.duration_minutes:
            return 0
            
        end_time = self.started_at + timezone.timedelta(minutes=self.quiz.duration_minutes)
        now = timezone.now()
        
        if now > end_time:
            return 0
            
        return (end_time - now).total_seconds()


class QuizAnswer(models.Model):
    """
    Records a student's answer to a specific question in a quiz attempt
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name="selected_in")
    text_answer = models.TextField(blank=True, null=True)  # For text questions
    boolean_answer = models.BooleanField(null=True, blank=True)  # For true/false questions
    points_earned = models.IntegerField(default=0)
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)  # For instructor feedback
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer for {self.question} in {self.attempt}"
