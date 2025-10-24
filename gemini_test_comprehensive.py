"""
Gemini Question Generation Test

This script provides a comprehensive test for the Gemini question generation functionality.
It runs a standalone test that doesn't require Django or the full web application.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gemini_test")

# Add the project root to Python path to import the necessary modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'classroom_connect'))
sys.path.append(os.path.join(project_root, 'classroom_connect/backend_quiz'))

def import_gemini_generator():
    """Attempt to import the GeminiQuestionGenerator class with error handling."""
    try:
        # First try the direct import
        logger.info("Trying direct import...")
        from classroom_connect.backend_quiz.academic_integration.utils.gemini_generator import GeminiQuestionGenerator
        logger.info("Direct import successful!")
        return GeminiQuestionGenerator
    except ImportError as e1:
        logger.warning(f"Direct import failed: {e1}")
        
        try:
            # Try with backend_quiz prefix
            logger.info("Trying with backend_quiz prefix...")
            from backend_quiz.academic_integration.utils.gemini_generator import GeminiQuestionGenerator
            logger.info("Backend quiz prefix import successful!")
            return GeminiQuestionGenerator
        except ImportError as e2:
            logger.warning(f"Backend quiz prefix import failed: {e2}")
            
            try:
                # Try with just academic_integration prefix
                logger.info("Trying with academic_integration prefix...")
                from academic_integration.utils.gemini_generator import GeminiQuestionGenerator
                logger.info("Academic integration prefix import successful!")
                return GeminiQuestionGenerator
            except ImportError as e3:
                logger.error(f"All import attempts failed: {e3}")
                
                # Print details to help diagnose
                logger.info("Current directory: " + os.path.abspath('.'))
                logger.info("Python path: " + str(sys.path))
                
                # Try to find the file manually
                for root_dir in sys.path:
                    search_path = os.path.join(root_dir, 'academic_integration/utils/gemini_generator.py')
                    if os.path.exists(search_path):
                        logger.info(f"Found file at: {search_path}")
                
                raise ImportError("Could not import GeminiQuestionGenerator") from e3

def test_question_generation():
    """Test generating questions using Gemini API."""
    print("=" * 70)
    print("GEMINI QUESTION GENERATION TEST")
    print("=" * 70)
    
    # 1. Load environment variables
    env_path = os.path.join(project_root, "classroom_connect", ".env")
    if os.path.exists(env_path):
        print(f"Loading environment from {env_path}")
        load_dotenv(env_path)
    else:
        print(f"Warning: .env file not found at {env_path}")
        print("Looking for .env in current directory")
        load_dotenv()
    
    # 2. Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set in environment")
        print("Please create a .env file with your Gemini API key")
        print("Example: GEMINI_API_KEY=your_api_key_here")
        return False
    
    if api_key == "your_gemini_api_key_here":
        print("ERROR: GEMINI_API_KEY contains placeholder value")
        print("Please update your .env file with a valid API key")
        return False
    
    print(f"Found API key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    
    # 3. Import GeminiQuestionGenerator
    try:
        print("\nImporting GeminiQuestionGenerator...")
        GeminiQuestionGenerator = import_gemini_generator()
        print("✓ Successfully imported GeminiQuestionGenerator")
    except Exception as e:
        print(f"ERROR: Failed to import GeminiQuestionGenerator: {e}")
        return False
    
    # 4. Create generator instance
    try:
        print("\nCreating GeminiQuestionGenerator instance...")
        generator = GeminiQuestionGenerator(api_key)
        print("✓ Successfully created generator instance")
    except Exception as e:
        print(f"ERROR: Failed to create generator: {e}")
        return False
    
    # 5. Test with simple content
    test_content = """
    The water cycle, also known as the hydrologic cycle, describes the continuous movement
    of water on, above, and below the surface of the Earth. Water can change states among
    liquid, vapor, and ice at various places in the water cycle. Although the balance of water
    on Earth remains fairly constant over time, individual water molecules can come and go.
    
    The water cycle involves the following processes:
    1. Evaporation: Water from oceans, lakes, and rivers turns into water vapor.
    2. Transpiration: Plants release water vapor into the air.
    3. Condensation: Water vapor cools and forms clouds.
    4. Precipitation: Water falls from clouds as rain, snow, sleet, or hail.
    5. Collection: Water is collected in oceans, lakes, rivers, and groundwater.
    """
    
    print("\nGenerating questions from test content...")
    
    try:
        result = generator.generate_questions(
            content=test_content,
            num_questions=2,
            difficulty="medium",
            question_types=["mcq_single", "true_false"]
        )
        
        if not result.get("success", False):
            print(f"ERROR: Question generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        questions = result.get("questions", [])
        if not questions:
            print("ERROR: No questions were generated")
            return False
        
        print(f"✓ Successfully generated {len(questions)} questions")
        
        # Display the generated questions
        print("\nGENERATED QUESTIONS:")
        print("-" * 40)
        
        for i, question in enumerate(questions):
            print(f"\nQUESTION {i+1}: {question['text']}")
            print(f"Type: {question['type']}")
            
            if question.get("choices"):
                print("Choices:")
                for j, choice in enumerate(question["choices"]):
                    correct = "✓" if choice.get("is_correct") else " "
                    print(f"  {chr(65+j)}. [{correct}] {choice['text']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Exception during question generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_content_extraction():
    """Test the file content extraction functionality."""
    print("\n" + "=" * 70)
    print("FILE CONTENT EXTRACTION TEST")
    print("=" * 70)
    
    # Import necessary modules
    try:
        GeminiQuestionGenerator = import_gemini_generator()
        print("✓ Successfully imported GeminiQuestionGenerator")
    except Exception as e:
        print(f"ERROR: Failed to import GeminiQuestionGenerator: {e}")
        return False
    
    # Try to import the extract_text_from_file function
    try:
        from classroom_connect.backend_quiz.academic_integration.utils.gemini_generator import extract_text_from_file
        print("✓ Successfully imported extract_text_from_file")
    except ImportError:
        try:
            # Check if the function exists in the module
            print("Direct import failed, checking if function exists in module...")
            import inspect
            source = inspect.getsource(GeminiQuestionGenerator.__module__)
            if "def extract_text_from_file" in source:
                print("✓ extract_text_from_file function exists in module")
            else:
                print("✗ extract_text_from_file function not found in module")
                return False
        except Exception as e:
            print(f"ERROR: Failed to check for extract_text_from_file: {e}")
            return False
    
    # Test with a simple text string
    test_text = "This is a test string."
    test_base64 = "VGhpcyBpcyBhIHRlc3Qgc3RyaW5nLg=="
    
    print("\nTesting base64 decoding with simple text...")
    
    try:
        # Create generator instance
        api_key = os.getenv("GEMINI_API_KEY")
        generator = GeminiQuestionGenerator(api_key)
        
        # Test direct file generation
        print("Testing file content extraction via generate_questions_from_file...")
        result = generator.generate_questions_from_file(
            file_content=test_base64,
            file_type="text/plain",
            num_questions=1,
            difficulty="easy",
            question_types=["mcq_single"]
        )
        
        if result.get("success", False):
            print("✓ Successfully generated questions from file content")
            return True
        else:
            print(f"✗ Failed to generate questions from file content: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"ERROR: Exception during file content extraction test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running Gemini Question Generation Test")
    print("This test verifies that the Gemini API integration works correctly")
    print("=" * 70)
    
    # Run the tests
    question_test = test_question_generation()
    file_test = test_file_content_extraction()
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Question Generation Test: {'PASSED' if question_test else 'FAILED'}")
    print(f"File Content Extraction Test: {'PASSED' if file_test else 'FAILED'}")
    
    if question_test and file_test:
        print("\nALL TESTS PASSED!")
        print("The Gemini API integration is working correctly.")
    else:
        print("\nSome tests FAILED!")
        print("Please check the error messages above for troubleshooting.")
    
    input("\nPress Enter to exit...")