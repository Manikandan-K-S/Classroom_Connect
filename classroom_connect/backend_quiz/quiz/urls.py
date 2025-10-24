from django.urls import path
from . import views
from . import views_debug

app_name = 'quiz'

urlpatterns = [
    # API endpoints only
    path("quizzes/", views.quiz_list, name="quiz_list"),
    path("quizzes/<int:pk>/", views.quiz_detail, name="quiz_detail"),
    path("quizzes/<int:quiz_id>/attempts/", views.quiz_attempts, name="quiz_attempts"),
    path("quizzes/<int:quiz_id>/end/", views.end_quiz, name="end_quiz"),
    path("quizzes/attempt/<int:quiz_id>/", views.get_or_create_attempt, name="get_or_create_attempt"),
    path("results/", views.quiz_result, name="quiz_result"),
    path("grade-answer/", views.grade_answer, name="grade_answer"),
    path("check-tutorial-availability/", views.check_tutorial_availability, name="check_tutorial_availability"),
    # New endpoint to get active quizzes for a student
    path("active-quizzes/student/<str:student_roll_number>/", views.get_active_quizzes, name="get_active_quizzes"),
    
    # Debug endpoints - for troubleshooting only
    path("debug/quiz/<int:quiz_id>/availability/", views_debug.debug_quiz_availability, name="debug_quiz_availability"),
    path("debug/timezone/", views_debug.debug_quiz_timezone, name="debug_timezone"),
    path("debug/quiz/<int:quiz_id>/", views.debug_quiz, name="debug_quiz_detail"),
    path("debug/quizzes/", views.debug_quiz, name="debug_quizzes"),
]
