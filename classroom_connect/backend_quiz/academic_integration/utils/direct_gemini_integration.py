import os
import base64
import json
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
from dotenv import load_dotenv
import google.generativeai as genai

# Import our local file extraction utility
from .gemini_generator import extract_text_from_file, GeminiQuestionGenerator

# Import models
from quiz.models import Quiz, Question, Choice, User

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable is not set. Quiz generation will fail.")


def create_quiz_from_file(
    file_content: str, 
    file_type: str, 
    quiz_title: str,
    quiz_description: str,
    course_id: Optional[str] = None,
    tutorial_number: Optional[int] = None,
    num_questions: int = 5,
    difficulty: str = "medium",
    question_types: List[str] = None,
    staff_email: str = None,
    duration_minutes: int = 30,
    **quiz_options
) -> Dict[str, Any]:
    """
    Create a quiz with questions generated from a file using Gemini API.
    
    Args:
        file_content: Base64 encoded file content
        file_type: MIME type of the file
        quiz_title: Title of the quiz
        quiz_description: Description of the quiz
        course_id: Optional Academic Analyzer Course ID
        tutorial_number: Optional tutorial number (1-4)
        num_questions: Number of questions to generate
        difficulty: Difficulty level ("easy", "medium", "hard")
        question_types: Types of questions to generate
        staff_email: Email of the staff creating the quiz
        duration_minutes: Quiz duration in minutes
        quiz_options: Additional quiz options
        
    Returns:
        Dictionary with quiz creation status and result
    """
    try:
        if question_types is None:
            question_types = ["mcq_single", "mcq_multiple", "true_false"]
        
        # Initialize the Gemini generator
        generator = GeminiQuestionGenerator()
        
        # Log the generation attempt
        logger.info(f"Starting question generation from {file_type} file, requesting {num_questions} questions at {difficulty} difficulty")
        
        try:
            # Generate questions from file
            result = generator.generate_questions_from_file(
                file_content=file_content,
                file_type=file_type,
                num_questions=num_questions,
                difficulty=difficulty,
                question_types=question_types
            )
            
            if not result.get("success"):
                logger.error(f"Failed to generate questions: {result.get('error')}")
                return {"success": False, "error": result.get("error", "Failed to generate questions")}
                
            questions_data = result.get("questions", [])
            
            # Log question generation results
            logger.info(f"Generated {len(questions_data)} questions successfully")
            
            if not questions_data:
                logger.warning("API returned success but no questions were generated")
                return {"success": False, "error": "No questions were generated. The content may be too short or not suitable for question generation."}
        except Exception as e:
            logger.exception(f"Exception during question generation: {e}")
            return {"success": False, "error": f"Error during question generation: {str(e)}"}
        
        # Create or get the staff user
        staff_user = None
        if staff_email:
            staff_user, created = User.objects.get_or_create(
                username=staff_email,
                defaults={
                    'email': staff_email,
                    'role': 'admin'
                }
            )
        
        # Set is_mock_test based on tutorial_number
        quiz_type = quiz_options.get('quiz_type', 'tutorial')
        if not tutorial_number and quiz_type == 'tutorial':
            quiz_type = 'mock'
        
        # Create the quiz
        quiz = Quiz.objects.create(
            title=quiz_title,
            description=quiz_description,
            course_id=course_id,
            tutorial_number=tutorial_number,
            created_by=staff_user,
            quiz_type=quiz_type,
            duration_minutes=duration_minutes,
            is_active=quiz_options.get('is_active', True),
            show_results=quiz_options.get('show_results', True),
            allow_review=quiz_options.get('allow_review', True),
            start_date=quiz_options.get('start_date'),
            complete_by_date=quiz_options.get('complete_by_date')
        )
        
        # Create questions and choices
        for question_data in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=question_data['text'],
                question_type=question_data['type'],
                order=question_data.get('order', 0)
            )
            
            # Add choices for MCQ and true/false questions
            if question_data['type'] in ['mcq_single', 'mcq_multiple', 'true_false']:
                for choice_data in question_data.get('choices', []):
                    Choice.objects.create(
                        question=question,
                        text=choice_data['text'],
                        is_correct=choice_data['is_correct'],
                        order=choice_data.get('order', 0)
                    )
        
        return {
            "success": True, 
            "quiz_id": quiz.id, 
            "question_count": len(questions_data),
            "message": f"Successfully created quiz '{quiz_title}' with {len(questions_data)} questions"
        }
        
    except Exception as e:
        logger.exception(f"Error in create_quiz_from_file: {e}")
        return {
            "success": False,
            "error": str(e)
        }