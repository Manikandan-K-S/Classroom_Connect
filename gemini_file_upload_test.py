#!/usr/bin/env python
"""
Direct Gemini API File Upload Test for Classroom Connect

This script bypasses the Django backend and directly uses the Gemini API 
to generate quiz questions from file content.
"""

import os
import sys
import json
import base64
import argparse
import mimetypes
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

def load_file(file_path):
    """Load file and encode it as base64."""
    try:
        # Make sure path is properly stripped of whitespace and quotes
        file_path = file_path.strip().strip('"\'')
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            return file_bytes
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

def get_mime_type(file_path):
    """Determine MIME type from file extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type
    
    # Fallback to common types if mimetypes fails
    ext = os.path.splitext(file_path)[1].lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".html": "text/html",
        ".htm": "text/html"
    }
    return mime_types.get(ext, "application/octet-stream")

def get_file_info(file_path):
    """Get file information."""
    try:
        # Trim any leading/trailing whitespace and quotes from the path
        file_path = file_path.strip().strip('"\'')
        
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}")
            return {
                "path": file_path,
                "name": "File not found",
                "error": "File does not exist"
            }
            
        size_bytes = os.path.getsize(file_path)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        if size_mb >= 1:
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = f"{size_kb:.2f} KB"
            
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size_bytes": size_bytes,
            "size_str": size_str,
            "mime_type": get_mime_type(file_path),
            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Error getting file info: {e}")
        return {"path": file_path, "name": "Unknown file", "error": str(e)}

def extract_text_from_file(file_content, file_type):
    """Extract text from file content."""
    try:
        if file_type == "application/pdf":
            import io
            from PyPDF2 import PdfReader
            
            pdf_stream = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_stream)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n\n"
            return text
            
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import io
            from docx import Document
            
            docx_stream = io.BytesIO(file_content)
            doc = Document(docx_stream)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
            
        elif file_type.startswith("text/"):
            return file_content.decode('utf-8')
            
        else:
            return f"Unsupported file type: {file_type}"
            
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def generate_questions_with_gemini(content, num_questions=3, difficulty="medium", question_types=None):
    """Generate questions directly using Gemini API."""
    if question_types is None:
        question_types = ["mcq_single", "mcq_multiple", "true_false"]
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "error": "GEMINI_API_KEY not found in environment variables"}
    
    try:
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Find the best available Gemini model
        models = genai.list_models()
        gemini_models = [m.name for m in models if "gemini" in m.name.lower()]
        if gemini_models:
            model_name = sorted(gemini_models, reverse=True)[0]
        else:
            model_name = "gemini-1.5-flash"  # Default to known model
            
        print(f"Using Gemini model: {model_name}")
        
        # Create model instance
        model = genai.GenerativeModel(model_name)
        
        # Build the prompt
        prompt = f"""
        Generate {num_questions} {difficulty} difficulty questions based on the following content:
        
        {content}
        
        Please include the following question types: {', '.join(question_types)}.
        
        Format each question with:
        1. The question text
        2. The type of question ({', '.join(question_types)})
        3. For multiple choice questions, provide 4 options with exactly one correct answer
        4. For true/false questions, provide the correct answer (true or false)
        
        Return the result as a JSON array of question objects with the following structure:
        {{
          "text": "question text",
          "type": "question type",
          "choices": [
            {{"text": "choice text", "is_correct": true or false}},
            ...
          ]
        }}
        
        Your response should be valid JSON and include ONLY the question array.
        """
        
        # Generate content
        response = model.generate_content(prompt)
        
        if not response.text:
            return {"success": False, "error": "Empty response from Gemini API"}
        
        # Extract JSON from response
        text = response.text
        json_start = text.find('[')
        json_end = text.rfind(']') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = text[json_start:json_end]
            try:
                questions = json.loads(json_text)
                return {"success": True, "questions": questions}
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"Failed to parse JSON response: {str(e)}", "raw_response": text}
        else:
            # Try to process non-JSON format
            return {"success": False, "error": "Response was not in JSON format", "raw_response": text}
            
    except Exception as e:
        return {"success": False, "error": f"Error generating questions: {str(e)}"}

def test_upload(file_path, num_questions=3, difficulty="medium", question_types=None):
    """Test uploading a file and generating questions directly with Gemini API."""
    if question_types is None:
        question_types = ["mcq_single", "mcq_multiple", "true_false"]
        
    file_info = get_file_info(file_path)
    
    print("=" * 60)
    print(f"FILE UPLOAD TEST: {file_info['name']}")
    print("=" * 60)
    print(f"File: {file_info['path']}")
    print(f"Size: {file_info['size_str']}")
    print(f"Type: {file_info['mime_type']}")
    print(f"Modified: {file_info['modified']}")
    
    # Check if file is too large
    if file_info['size_bytes'] > 10 * 1024 * 1024:  # 10 MB limit
        print("\nWARNING: File is larger than 10MB, which may be too large for API processing.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            print("Aborted.")
            sys.exit(0)
    
    # Load file content
    print("\nLoading file content...")
    file_content = load_file(file_path)
    
    # Extract text from file
    print("Extracting text from file...")
    text_content = extract_text_from_file(file_content, file_info['mime_type'])
    
    # Limit text content size to avoid API limits
    max_length = 30000  # Characters
    if len(text_content) > max_length:
        print(f"Content is too large ({len(text_content)} chars). Truncating to {max_length} chars.")
        text_content = text_content[:max_length]
    
    # Generate questions
    print("\nGenerating questions with Gemini API...")
    result = generate_questions_with_gemini(
        text_content, 
        num_questions=num_questions,
        difficulty=difficulty,
        question_types=question_types
    )
    
    if result.get("success"):
        questions = result.get("questions", [])
        print(f"\n✓ Success! Generated {len(questions)} questions.")
        
        print("\nGenerated Questions:")
        print("-" * 50)
        for i, question in enumerate(questions):
            print(f"\nQuestion {i+1}: {question['text']}")
            print(f"Type: {question['type']}")
            
            if question.get("choices"):
                print("Choices:")
                for j, choice in enumerate(question["choices"]):
                    correct = "✓" if choice.get("is_correct") else " "
                    print(f"  {j+1}. [{correct}] {choice['text']}")
    else:
        print(f"\n✗ Failed to generate questions: {result.get('error', 'Unknown error')}")
        
        if result.get("raw_response"):
            print("\nRaw response from API:")
            print("-" * 50)
            print(result["raw_response"][:500] + "..." if len(result["raw_response"]) > 500 else result["raw_response"])
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Load environment variables
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "classroom_connect", ".env")
    if os.path.exists(env_path):
        print(f"Loading environment from {env_path}")
        load_dotenv(env_path)
    else:
        print(f"Warning: .env file not found at {env_path}")
        print("Looking for .env in current directory")
        load_dotenv()
    
    parser = argparse.ArgumentParser(description="Test file upload and question generation directly with Gemini API")
    parser.add_argument("file", help="Path to the file to upload")
    parser.add_argument("--questions", type=int, default=3, help="Number of questions to generate (default: 3)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="medium",
                      help="Question difficulty (default: medium)")
    parser.add_argument("--types", nargs="+", choices=["mcq_single", "mcq_multiple", "true_false", "text"], 
                      default=["mcq_single", "mcq_multiple", "true_false"],
                      help="Question types to generate (default: mcq_single mcq_multiple true_false)")
    
    args = parser.parse_args()
    
    test_upload(
        file_path=args.file.strip(),  # Strip spaces, quotes are handled in get_file_info
        num_questions=args.questions,
        difficulty=args.difficulty,
        question_types=args.types
    )