"""
Gemini API Tester for Classroom Connect

This script provides a simple way to verify that the Gemini API is working correctly
for generating quiz questions. It uses the GeminiQuestionGenerator utility directly,
bypassing the Django views.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the project directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "classroom_connect", "backend_quiz")
sys.path.insert(0, backend_dir)

def test_gemini_api():
    """Test the Gemini API for generating quiz questions."""
    print("=" * 60)
    print("Gemini API Tester for Classroom Connect")
    print("=" * 60)
    
    # Load environment variables
    env_path = "classroom_connect/.env"
    print(f"Loading .env from: {env_path}")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print("✓ Loaded .env file")
    else:
        print("✗ .env file not found!")
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("✗ GEMINI_API_KEY not set in environment variables")
        return
    elif api_key == "your_gemini_api_key_here":
        print("✗ GEMINI_API_KEY is set to the placeholder value")
        return
    
    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***masked***"
    print(f"✓ Found API key: {masked_key}")
    
    # Import the GeminiQuestionGenerator class
    try:
        print("\nImporting GeminiQuestionGenerator...")
        # Try different import paths based on where the script is run from
        try:
            from classroom_connect.backend_quiz.academic_integration.utils.gemini_generator import GeminiQuestionGenerator
        except ImportError:
            try:
                from backend_quiz.academic_integration.utils.gemini_generator import GeminiQuestionGenerator
            except ImportError:
                from academic_integration.utils.gemini_generator import GeminiQuestionGenerator
                
        print("✓ Successfully imported GeminiQuestionGenerator")
    except ImportError as e:
        print(f"✗ Failed to import GeminiQuestionGenerator: {e}")
        print("\nPossible issues:")
        print("1. Make sure you're running this script from the root directory of the project")
        print("2. Check the path to your classroom_connect project")
        print("3. Try running: python -c \"import sys; print(sys.path)\" to see your Python path")
        return
    
    # Create an instance of the generator
    try:
        print("\nCreating GeminiQuestionGenerator instance...")
        generator = GeminiQuestionGenerator(api_key)
        print("✓ Successfully created generator instance")
    except Exception as e:
        print(f"✗ Failed to create generator instance: {e}")
        return
    
    # Test generating questions from text
    test_content = """
    Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, 
    especially computer systems. These processes include learning (the acquisition of information 
    and rules for using the information), reasoning (using rules to reach approximate or definite 
    conclusions), and self-correction.
    
    Machine Learning is a subset of AI that focuses on the development of computer programs that 
    can access data and use it to learn for themselves. Deep Learning is a subset of Machine Learning 
    that uses neural networks with many layers.
    
    Natural Language Processing (NLP) is a field of AI that gives computers the ability to understand 
    text and spoken words in much the same way as humans can. Computer Vision is another field that 
    enables computers to see, identify and process images in the same way that human vision does.
    """
    
    print("\nGenerating questions from sample text...")
    try:
        result = generator.generate_questions(
            content=test_content,
            num_questions=2,
            difficulty="medium",
            question_types=["mcq_single", "true_false"]
        )
        
        if result["success"]:
            print(f"✓ Successfully generated {len(result['questions'])} questions")
            
            print("\nGenerated Questions:")
            for i, question in enumerate(result["questions"]):
                print(f"\nQuestion {i+1}: {question['text']}")
                print(f"Type: {question['type']}")
                
                if question["choices"]:
                    print("Choices:")
                    for j, choice in enumerate(question["choices"]):
                        correct_mark = "✓" if choice["is_correct"] else " "
                        print(f"  {chr(65+j)}. [{correct_mark}] {choice['text']}")
        else:
            print(f"✗ Failed to generate questions: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error generating questions: {e}")
    
    print("\n" + "=" * 60)
    print("API Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_gemini_api()
    input("\nPress Enter to exit...")