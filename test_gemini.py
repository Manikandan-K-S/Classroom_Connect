"""
Test script for Gemini API integration with Classroom Connect.
This script tests if the Gemini API is correctly configured by generating some simple quiz questions.
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Add classroom_connect to Python path
sys.path.append("classroom_connect")

def test_gemini_api():
    """Test the Gemini API connection and question generation capabilities."""
    print("Testing Gemini API Integration...")
    
    # Load environment variables
    load_dotenv("classroom_connect/.env")
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n❌ ERROR: No valid Gemini API key found in .env file")
        print("Please add your Gemini API key to classroom_connect/.env")
        print("You can get a key from: https://ai.google.dev/")
        return False
    
    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"\n❌ ERROR: Failed to configure Gemini API: {str(e)}")
        return False
    
    # Test content for question generation
    test_content = """
    Python is a high-level, interpreted programming language known for its readability and versatility.
    It was created by Guido van Rossum and first released in 1991. Python supports multiple programming
    paradigms, including procedural, object-oriented, and functional programming. Key features of Python
    include dynamic typing, automatic memory management, and a comprehensive standard library.
    """
    
    # Create Gemini model
    try:
        # Get available models
        print("Checking available Gemini models...")
        try:
            models = genai.list_models()
            model_names = [model.name for model in models]
            
            # Preferred models for question generation
            preferred_models = [
                "models/gemini-2.5-flash",        # Stable flash model (as of Oct 2025)
                "models/gemini-flash-latest",      # Latest flash model
                "models/gemini-pro-latest",        # Latest pro model
                "models/gemini-2.5-pro",          # Stable pro model with better reasoning
            ]
            
            # Check if any preferred models are available
            model_name = None
            for preferred in preferred_models:
                if preferred in model_names:
                    model_name = preferred
                    print(f"Using preferred model: {model_name}")
                    break
                    
            # If no preferred models found, try any Gemini model
            if not model_name:
                gemini_models = [m for m in model_names if 'gemini' in m]
                if gemini_models:
                    model_name = gemini_models[0]
                    print(f"Using available model: {model_name}")
                else:
                    model_name = 'models/gemini-flash-latest'  # Default to newest model as of Oct 2025
                    print(f"No Gemini models found, defaulting to: {model_name}")
        except Exception as e:
            print(f"Could not retrieve model list: {str(e)}")
            model_name = 'models/gemini-flash-latest'  # Default to newest model as of Oct 2025
            print(f"Defaulting to model: {model_name}")
            
        model = genai.GenerativeModel(model_name)
        
        # Generate a simple prompt for quiz questions
        prompt = f"""
        Create 2 multiple-choice quiz questions about the following text:
        {test_content}
        
        Format your response as JSON with the following structure:
        {{
            "questions": [
                {{
                    "text": "Question text goes here?",
                    "type": "mcq_single",
                    "choices": [
                        {{"text": "Choice 1", "is_correct": false}},
                        {{"text": "Choice 2", "is_correct": true}},
                        {{"text": "Choice 3", "is_correct": false}},
                        {{"text": "Choice 4", "is_correct": false}}
                    ]
                }}
            ]
        }}
        """
        
        # Generate response
        response = model.generate_content(prompt)
        
        if not response.text:
            print("\n❌ ERROR: Gemini API returned an empty response")
            return False
            
        print("\n✅ Successfully connected to Gemini API!")
        print("\nSample response from Gemini API (preview):")
        print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to generate content with Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    
    if success:
        print("\n✅ Gemini API integration test successful!")
        print("You're ready to use AI question generation in Classroom Connect.")
    else:
        print("\n❌ Gemini API integration test failed.")
        print("Please check your API key and internet connection.")
    
    input("\nPress Enter to exit...")