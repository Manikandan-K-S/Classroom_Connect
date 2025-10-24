"""
Gemini API Examples for Classroom Connect

This script demonstrates how to use the Gemini API for various educational tasks.
It provides examples of generating questions from different types of educational materials.
"""

import os
import sys
import base64
from dotenv import load_dotenv
import google.generativeai as genai
sys.path.append("classroom_connect")
from classroom_connect.backend_quiz.academic_integration.utils.gemini_generator import GeminiQuestionGenerator

def load_api_key():
    """Load API key from environment variables."""
    load_dotenv("classroom_connect/.env")
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    return api_key

def example_text_content():
    """Generate questions from plain text content."""
    api_key = load_api_key()
    
    # Sample text content
    content = """
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
    
    The water cycle is powered by solar energy and gravity. The sun drives evaporation of
    water from oceans, lakes, and rivers, as well as transpiration from plants. Gravity causes
    precipitation to fall from clouds and water to flow from higher to lower places.
    """
    
    # Create question generator
    generator = GeminiQuestionGenerator(api_key)
    
    # Generate questions
    print("\n=== GENERATING QUESTIONS FROM TEXT CONTENT ===")
    result = generator.generate_questions(
        content=content,
        num_questions=3,
        difficulty="medium",
        question_types=["mcq_single", "mcq_multiple", "true_false"]
    )
    
    # Display results
    if result["success"]:
        print(f"Successfully generated {len(result['questions'])} questions!\n")
        for i, q in enumerate(result["questions"]):
            print(f"Question {i+1}: {q['text']}")
            print(f"Type: {q['type']}")
            if q['type'] in ["mcq_single", "mcq_multiple", "true_false"]:
                for choice in q["choices"]:
                    correct_mark = "✓" if choice["is_correct"] else " "
                    print(f"  [{correct_mark}] {choice['text']}")
            print()
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

def example_from_file(file_path):
    """Generate questions from a file (PDF, DOCX, or TXT)."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    api_key = load_api_key()
    
    # Determine file type based on extension
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == '.pdf':
        mime_type = 'application/pdf'
    elif file_extension == '.docx':
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif file_extension == '.txt':
        mime_type = 'text/plain'
    else:
        print(f"Unsupported file type: {file_extension}")
        return
    
    # Read file content
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    # Encode file content to base64
    encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    # Create question generator
    generator = GeminiQuestionGenerator(api_key)
    
    # Generate questions
    print(f"\n=== GENERATING QUESTIONS FROM {file_extension.upper()} FILE ===")
    result = generator.generate_questions_from_file(
        file_content=encoded_content,
        file_type=mime_type,
        num_questions=3,
        difficulty="medium",
        question_types=["mcq_single", "mcq_multiple", "true_false"]
    )
    
    # Display results
    if result["success"]:
        print(f"Successfully generated {len(result['questions'])} questions from {file_path}!\n")
        for i, q in enumerate(result["questions"]):
            print(f"Question {i+1}: {q['text']}")
            print(f"Type: {q['type']}")
            if q['type'] in ["mcq_single", "mcq_multiple", "true_false"]:
                for choice in q["choices"]:
                    correct_mark = "✓" if choice["is_correct"] else " "
                    print(f"  [{correct_mark}] {choice['text']}")
            print()
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

def customize_question_types():
    """Generate specific types of questions."""
    api_key = load_api_key()
    
    # Sample text content
    content = """
    Photosynthesis is the process used by plants, algae and certain bacteria to harness energy from sunlight
    and turn it into chemical energy. During photosynthesis in green plants, light energy is captured and used
    to convert water, carbon dioxide, and minerals into oxygen and energy-rich organic compounds. The process
    primarily takes place in plant leaves and has several steps.
    
    The overall chemical reaction of photosynthesis is:
    6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂
    
    The process has two main phases: the light-dependent reactions and the Calvin cycle. In the light-dependent
    reactions, which occur in the thylakoid membrane, chlorophyll absorbs light energy, which excites electrons
    that are then transferred through a series of electron carriers, producing ATP and NADPH. In the Calvin cycle,
    which takes place in the stroma, the ATP and NADPH from the light-dependent reactions are used to produce
    organic compounds from carbon dioxide.
    """
    
    # Create question generator
    generator = GeminiQuestionGenerator(api_key)
    
    # Example 1: Generate only multiple choice questions
    print("\n=== GENERATING MULTIPLE CHOICE QUESTIONS ===")
    result1 = generator.generate_questions(
        content=content,
        num_questions=2,
        difficulty="medium",
        question_types=["mcq_single"]
    )
    
    # Example 2: Generate only true/false questions
    print("\n=== GENERATING TRUE/FALSE QUESTIONS ===")
    result2 = generator.generate_questions(
        content=content,
        num_questions=2,
        difficulty="easy",
        question_types=["true_false"]
    )
    
    # Display results
    for result, title in [(result1, "MULTIPLE CHOICE QUESTIONS"), (result2, "TRUE/FALSE QUESTIONS")]:
        print(f"\n=== {title} ===")
        if result["success"]:
            print(f"Successfully generated {len(result['questions'])} questions!\n")
            for i, q in enumerate(result["questions"]):
                print(f"Question {i+1}: {q['text']}")
                for choice in q["choices"]:
                    correct_mark = "✓" if choice["is_correct"] else " "
                    print(f"  [{correct_mark}] {choice['text']}")
                print()
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("Gemini API Examples for Classroom Connect")
    print("=" * 50)
    
    # Run examples
    example_text_content()
    
    # To test with a file, uncomment and update the path
    # example_from_file("path/to/your/document.pdf")
    # example_from_file("path/to/your/document.docx")
    # example_from_file("path/to/your/document.txt")
    
    customize_question_types()
    
    print("=" * 50)
    print("Examples completed!")
    input("\nPress Enter to exit...")