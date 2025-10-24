from django.http import JsonResponse, HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib import messages
import json
import logging
import os
import traceback

# Import the direct Gemini integration module
from .utils.direct_gemini_integration import create_quiz_from_file

# Set up logging
logger = logging.getLogger(__name__)

def direct_question_generation(request: HttpRequest) -> HttpResponse:
    """
    View for staff to generate questions directly from an uploaded file
    using the Gemini API and save them to a new quiz.
    
    This is a simplified endpoint that doesn't require additional authentication
    beyond being logged in as a staff member.
    """
    # Debug: Log API key status
    api_key = os.environ.get("GEMINI_API_KEY")
    logger.info(f"GEMINI_API_KEY available: {bool(api_key)}, length: {len(api_key) if api_key else 0}")
    
    # Ensure staff is logged in
    staff_email = request.session.get('staff_email')
    if not staff_email:
        messages.error(request, "You must be logged in as staff")
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Parse JSON request body
        data = json.loads(request.body)
        
        # Extract parameters
        file_content = data.get('fileContent')
        file_type = data.get('fileType')
        quiz_title = data.get('quizTitle', 'Generated Quiz')
        quiz_description = data.get('quizDescription', 'Automatically generated from uploaded content')
        course_id = data.get('courseId')
        tutorial_number = data.get('tutorialNumber')
        num_questions = int(data.get('numQuestions', 5))
        difficulty = data.get('difficulty', 'medium')
        question_types = data.get('questionTypes', ['mcq_single', 'mcq_multiple', 'true_false'])
        duration_minutes = int(data.get('durationMinutes', 30))
        
        # Validate required fields
        if not file_content:
            return JsonResponse({'success': False, 'error': 'No file content provided'}, status=400)
        if not file_type:
            return JsonResponse({'success': False, 'error': 'No file type provided'}, status=400)
        
        # Additional quiz options that can be passed to create_quiz_from_file
        quiz_options = {
            'quiz_type': data.get('quizType', 'tutorial'),
            'is_active': data.get('isActive', True),
            'show_results': data.get('showResults', True),
            'allow_review': data.get('allowReview', True),
            'start_date': data.get('startDate'),
            'complete_by_date': data.get('completeByDate')
        }
        
        # Log the request parameters (excluding the file content for brevity)
        logger.info(
            f"Generating quiz: title='{quiz_title}', course_id='{course_id}', "
            f"num_questions={num_questions}, difficulty='{difficulty}', "
            f"question_types={question_types}, file_type='{file_type}'"
        )
        
        # Generate questions and create the quiz
        result = create_quiz_from_file(
            file_content=file_content,
            file_type=file_type,
            quiz_title=quiz_title,
            quiz_description=quiz_description,
            course_id=course_id,
            tutorial_number=tutorial_number,
            num_questions=num_questions,
            difficulty=difficulty,
            question_types=question_types,
            staff_email=staff_email,
            duration_minutes=duration_minutes,
            **quiz_options
        )
        
        if result.get('success'):
            logger.info(f"Quiz created successfully: ID={result.get('quiz_id')}, questions={result.get('question_count')}")
            return JsonResponse({
                'success': True, 
                'quiz_id': result.get('quiz_id'),
                'question_count': result.get('question_count'),
                'message': result.get('message', 'Quiz created successfully')
            })
        else:
            logger.error(f"Quiz creation failed: {result.get('error')}")
            return JsonResponse({
                'success': False, 
                'error': result.get('error', 'Failed to create quiz')
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON in request body'}, status=400)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        error_details = traceback.format_exc()
        logger.exception(f"Unexpected error in direct_question_generation: {e}")
        logger.error(f"Error details: {error_details}")
        # Return more detailed error information in development
        if os.environ.get('DJANGO_DEVELOPMENT', 'True') == 'True':
            return JsonResponse({
                'success': False, 
                'error': str(e),
                'details': error_details,
                'api_key_available': bool(os.environ.get('GEMINI_API_KEY'))
            }, status=500)
        else:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)