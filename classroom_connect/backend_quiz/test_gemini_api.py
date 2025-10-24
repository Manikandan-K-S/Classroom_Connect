"""
test_gemini_api.py

This script tests the Gemini API integration for quiz generation.
It bypasses the web interface and directly calls the API to check if quiz generation is working.
"""

import os
import sys
import json
import base64
from dotenv import load_dotenv

# Add the project directory to the Python path so we can import Django modules
sys.path.append('.')

# Set up Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_quiz.settings')
django.setup()

from academic_integration.utils.gemini_generator import GeminiQuestionGenerator
from academic_integration.utils.direct_gemini_integration import create_quiz_from_file

def test_gemini_api():
    """Test the Gemini API connection and quiz generation"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        return False
    
    print(f"API key found: {api_key[:4]}...{api_key[-4:]}")
    
    try:
        # Create a generator instance (this will test API key validity)
        generator = GeminiQuestionGenerator()
        print("Generator initialized successfully")
        
        # Create a simple test prompt
        test_content = """
        The water cycle, also known as the hydrologic cycle, describes the continuous movement of water on, above, and below the surface of the Earth. 
        Water can change states among liquid, vapor, and ice at various places in the water cycle. The water cycle involves the following processes:
        
        1. Evaporation: The process where water transforms from liquid to gas.
        2. Transpiration: The process by which plants release water vapor into the atmosphere.
        3. Condensation: The process where water vapor transforms into liquid water.
        4. Precipitation: Water falling from clouds as rain, sleet, hail, or snow.
        5. Infiltration: Water soaking into the soil.
        6. Runoff: Water flowing over land.
        """
        
        print("Testing question generation from text...")
        
        # Try generating questions from text
        result = generator.generate_questions(
            content=test_content,
            num_questions=2,
            difficulty="easy",
            question_types=["mcq_single", "true_false"]
        )
        
        if result.get("success"):
            print("SUCCESS: Question generation successful")
            questions = result.get("questions", [])
            print(f"Generated {len(questions)} questions")
            
            # Print first question
            if questions:
                print("\nSample question:")
                print(f"Question: {questions[0]['text']}")
                print(f"Type: {questions[0]['type']}")
                if questions[0].get('choices'):
                    print("Choices:")
                    for choice in questions[0]['choices']:
                        print(f"- {choice['text']} (Correct: {choice['is_correct']})")
                        
            return True
        else:
            print(f"ERROR: Question generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"ERROR: An exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Gemini API test...")
    success = test_gemini_api()
    if success:
        print("\nAPI test completed successfully! The Gemini API is working correctly.")
    else:
        print("\nAPI test failed. Please check the errors above.")