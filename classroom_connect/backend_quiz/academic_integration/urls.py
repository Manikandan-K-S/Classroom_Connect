from django.urls import path

from . import views
# Removed Gemini-related imports
from .views_quiz_grading import (
    quiz_student_performance, grade_quiz_attempt,
    quiz_answer_analysis
)
from .views_debug import debug_quiz_availability, debug_quiz_timezone
from .views_sync import sync_dashboard, sync_tutorial_attempt, sync_all_tutorials, check_api_status

app_name = "academic_integration"

urlpatterns = [
    path("", views.home, name="home"),
    
    # Staff routes
    path("staff/login/", views.staff_login, name="staff_login"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("staff/logout/", views.staff_logout, name="staff_logout"),
    path("staff/sync-dashboard/", sync_dashboard, name="sync_dashboard"),
    path("staff/sync-tutorial/<int:attempt_id>/", sync_tutorial_attempt, name="sync_tutorial_attempt"),
    path("staff/sync-all-tutorials/", sync_all_tutorials, name="sync_all_tutorials"),
    path("api/check-academic-analyzer-status/", check_api_status, name="check_api_status"),
    path("staff/course/create/", views.create_course, name="create_course"),
    path("staff/course/<str:course_id>/", views.manage_course, name="manage_course"),
    path("staff/course/<str:course_id>/remove-student/", views.remove_student_from_course, name="remove_student_from_course"),
    path("staff/course/<str:course_id>/download-marks-template/", views.download_marks_template, name="download_marks_template"),
    path("staff/students/template/download/", views.download_students_template, name="download_students_template"),
    
    # Archive management
    path("staff/archived-courses/", views.archived_courses, name="archived_courses"),
    path("staff/archived-course/<str:archived_course_id>/", views.archived_course_detail, name="archived_course_detail"),
    path("staff/course/<str:course_id>/archive/", views.archive_course, name="archive_course"),
    path("staff/archived-course/<str:archived_course_id>/restore/", views.restore_course, name="restore_course"),
    
    path("staff/students/", views.manage_students, name="manage_students"),
    path("staff/students/all/", views.view_all_students, name="view_all_students"),
    path("staff/student/detail/<str:rollno>/", views.student_detail, name="student_detail"),
    path("staff/student/create/", views.create_student, name="create_student"),
    path("staff/students/csv/", views.create_students_csv, name="create_students_csv"),
    
    # Analytics and grade management
    path("staff/analytics/", views.staff_analytics, name="staff_analytics"),
    path("staff/edit-marks/", views.edit_student_marks, name="edit_student_marks"),
    
    # Student course marks details (updated route)
    path("student/course/<str:course_id>/marks/", views.student_course_marks, name="student_course_marks"),
    
    # Quiz management routes for staff
    path("staff/quizzes/", views.admin_quiz_dashboard, name="admin_quiz_dashboard"),
    path("staff/quiz/create/", views.create_quiz, name="create_quiz"),
    # Removed simple quiz creation route
    path("staff/quiz/<int:quiz_id>/edit/", views.edit_quiz, name="edit_quiz"),
    path("staff/quiz/<int:quiz_id>/delete/", views.delete_quiz, name="delete_quiz"),
    path("staff/quiz/<int:quiz_id>/performance/", quiz_student_performance, name="quiz_student_performance"),
    path("staff/quiz/<int:quiz_id>/answers/", quiz_answer_analysis, name="quiz_answer_analysis"),
    path("staff/quiz/attempt/<int:attempt_id>/grade/", grade_quiz_attempt, name="grade_quiz_attempt"),
    
    # Student quiz routes
    path("student/quizzes/", views.student_quiz_dashboard, name="student_quiz_dashboard"),
    path("quiz/<int:quiz_id>/", views.quiz_detail, name="quiz_detail"),
    path("quiz/<int:quiz_id>/result/", views.quiz_result, name="quiz_result"),
    path("quiz/<int:quiz_id>/availability/", views.quiz_availability_info, name="quiz_availability_info"),
    
    # Quiz API endpoints
    path("api/quiz/<int:quiz_id>/", views.get_quiz_data, name="get_quiz_data"),
    path("api/quiz/<int:quiz_id>/end/", views.end_quiz, name="end_quiz"),
    path("api/quiz/<int:quiz_id>/attempt/", views.quiz_attempt, name="quiz_attempt"),
    path("api/quiz/<int:quiz_id>/submit/", views.submit_quiz, name="submit_quiz"),
    path("api/generate-questions/", views.generate_questions_from_content, name="generate_questions"),
    # Removed direct Gemini question generation API endpoint
    
    # Student routes
    path("student/login/", views.student_login, name="student_login"),
    path("student/dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student/profile/", views.student_profile, name="student_profile"),
    path("student/course/<str:course_id>/", views.course_detail, name="course_detail"),
    path("student/active-quizzes/", views.student_active_quizzes, name="student_active_quizzes"),
    path("student/logout/", views.student_logout, name="student_logout"),
    
    # Debug routes for staff
    path("staff/debug/quiz/availability/", debug_quiz_availability, name="debug_quiz_availability_list"),
    path("staff/debug/quiz/<int:quiz_id>/availability/", debug_quiz_availability, name="debug_quiz_availability"),
    path("staff/debug/timezone/", debug_quiz_timezone, name="debug_quiz_timezone"),
]