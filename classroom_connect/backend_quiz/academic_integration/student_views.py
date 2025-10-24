def view_all_students(request: HttpRequest) -> HttpResponse:
	"""
	View for staff to see all students in the system.
	"""
	staff_email = request.session.get("staff_email")
	if not staff_email:
		messages.info(request, "Please log in to continue.")
		return redirect("academic_integration:staff_login")

	students = []
	api_error = None

	try:
		# Get all students from the Academic Analyzer API
		response = requests.get(
			f"{api_base_url()}/staff/all-students",
			params={"email": staff_email},
			timeout=10,
		)
	except requests.RequestException as e:
		logger.exception(f"Failed to load student data: {str(e)}")
		api_error = "Could not reach Academic Analyzer API. Please check your internet connection and refresh the page."
	else:
		body = _safe_json(response)
		if response.ok and body.get("success"):
			students = body.get("students", [])
			logger.info(f"Successfully loaded {len(students)} students")
		else:
			error_message = body.get("message", "Unknown error")
			logger.error(f"API Error in view_all_students: {error_message}")
			api_error = f"API Error: {error_message}. Please try again later."

	context = {
		"staff_name": request.session.get("staff_name") or staff_email,
		"staff_email": staff_email,
		"students": students,
		"api_error": api_error,
	}
	return render(request, "academic_integration/view_all_students.html", context)


def student_detail(request: HttpRequest, rollno: str) -> HttpResponse:
	"""
	View for staff to see detailed information about a specific student.
	"""
	from quiz.models import QuizAttempt
	from django.db.models import Avg
	
	staff_email = request.session.get("staff_email")
	if not staff_email:
		messages.info(request, "Please log in to continue.")
		return redirect("academic_integration:staff_login")

	student = None
	enrolled_courses = []
	api_error = None

	try:
		# Get student details from the Academic Analyzer API
		response = requests.get(
			f"{api_base_url()}/staff/student-detail",
			params={"email": staff_email, "rollno": rollno},
			timeout=10,
		)
	except requests.RequestException as e:
		logger.exception(f"Failed to load student detail: {str(e)}")
		api_error = "Could not reach Academic Analyzer API. Please check your internet connection and refresh the page."
	else:
		body = _safe_json(response)
		if response.ok and body.get("success"):
			student = body.get("student", {})
			enrolled_courses = body.get("courses", [])
			logger.info(f"Successfully loaded details for student {rollno}")
		else:
			error_message = body.get("message", "Unknown error")
			logger.error(f"API Error in student_detail: {error_message}")
			api_error = f"API Error: {error_message}. Please try again later."

	# Get quiz attempts from the local database
	quiz_attempts = []
	completed_quizzes = 0
	avg_score = 0
	
	if student:
		quiz_attempts = QuizAttempt.objects.filter(
			user__username=rollno,
			completed_at__isnull=False
		).select_related('quiz').order_by('-completed_at')[:10]  # Get last 10 attempts
		
		# Add course names to quiz attempts
		course_lookup = {course['courseId']: course['courseName'] for course in enrolled_courses}
		for attempt in quiz_attempts:
			attempt.course_name = course_lookup.get(attempt.quiz.course_id, "Unknown Course")
		
		# Calculate statistics
		completed_quizzes = quiz_attempts.count()
		avg_score_obj = quiz_attempts.aggregate(Avg('percentage'))
		avg_score = avg_score_obj['percentage__avg'] or 0

	context = {
		"staff_name": request.session.get("staff_name") or staff_email,
		"staff_email": staff_email,
		"student": student,
		"enrolled_courses": enrolled_courses,
		"quiz_attempts": quiz_attempts,
		"completed_quizzes": completed_quizzes,
		"avg_score": avg_score,
		"api_error": api_error,
	}
	return render(request, "academic_integration/student_detail.html", context)