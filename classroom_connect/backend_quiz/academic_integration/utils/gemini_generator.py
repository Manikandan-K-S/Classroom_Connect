import os
import re
import io
import base64
import json
import requests
from typing import Dict, List, Any, Optional
import logging
from dotenv import load_dotenv
import google.generativeai as genai
try:
    import PyPDF2
    from docx import Document
    PDF_DOCX_AVAILABLE = True
except ImportError:
    PDF_DOCX_AVAILABLE = False

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configure the Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {str(e)}")

def extract_text_from_file(file_content: str, file_type: str) -> str:
    """
    Extract text from various file formats.
    
    Args:
        file_content: Base64 encoded file content
        file_type: MIME type of the file
        
    Returns:
        Extracted text from the file
    """
    try:
        # Remove the base64 header (e.g., "data:application/pdf;base64,")
        if ';base64,' in file_content:
            file_content = file_content.split(';base64,')[1]
            
        # Decode base64 content
        decoded_content = base64.b64decode(file_content)
        
        # Extract text based on file type
        if PDF_DOCX_AVAILABLE:
            if 'pdf' in file_type.lower():
                # Extract text from PDF
                pdf_file = io.BytesIO(decoded_content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
                return text
                
            elif 'word' in file_type.lower() or 'docx' in file_type.lower():
                # Extract text from DOCX
                docx_file = io.BytesIO(decoded_content)
                doc = Document(docx_file)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
        
        if 'text' in file_type.lower() or 'txt' in file_type.lower():
            # Plain text
            return decoded_content.decode('utf-8')
            
        else:
            # Unsupported file type
            raise ValueError(f"Unsupported file type: {file_type}")
            
    except Exception as e:
        logger.error(f"Error extracting text from file: {str(e)}")
        raise ValueError(f"Failed to process file: {str(e)}")

class GeminiQuestionGenerator:
    """
    A utility class to generate quiz questions using the Google Gemini API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        logger.debug(f"Initializing GeminiQuestionGenerator, API key available: {bool(self.api_key)}")
        
        if not self.api_key:
            logger.error("Gemini API key not provided and not found in environment variables")
            raise ValueError("Gemini API key not configured. Please add GEMINI_API_KEY to your environment variables.")
            
        # Validate API key format
        if not self._validate_api_key():
            logger.error("Provided Gemini API key appears to be invalid")
            raise ValueError("Invalid API key format. Gemini API keys should begin with 'AI' and be approximately 39 characters long.")
            
        # Determine available models and endpoints
        self._setup_model_info()
    
    def generate_questions_from_file(
        self,
        file_content: str,
        file_type: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate quiz questions from a file using Google Gemini API.
        
        Args:
            file_content: Base64 encoded file content
            file_type: MIME type of the file
            num_questions: Number of questions to generate
            difficulty: Difficulty level of questions ("easy", "medium", "hard")
            question_types: Types of questions to generate ("mcq_single", "mcq_multiple", "true_false", "text")
            
        Returns:
            Dict with success status and generated questions
        """
        try:
            # Extract text from file
            extracted_text = extract_text_from_file(file_content, file_type)
            
            # Generate questions from the extracted text
            return self.generate_questions(
                content=extracted_text,
                num_questions=num_questions,
                difficulty=difficulty,
                question_types=question_types
            )
        except Exception as e:
            logger.error(f"Error generating questions from file: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_questions(self, 
                          content: str, 
                          num_questions: int = 5, 
                          difficulty: str = "medium",
                          question_types: List[str] = None) -> Dict[str, Any]:
        """
        Generate quiz questions based on the provided content.
        
        Args:
            content: The text content to generate questions from
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy, medium, hard)
            question_types: List of question types to generate (mcq_single, mcq_multiple, true_false, text)
                           If None, generates a mix of question types
        
        Returns:
            A dictionary containing generated questions in the format needed by the quiz app
        """
        if question_types is None:
            question_types = ["mcq_single", "mcq_multiple", "true_false"]
        
        # Prepare the prompt for Gemini
        prompt = self._build_prompt(content, num_questions, difficulty, question_types)
        
        try:
            # Try using the SDK first (preferred method)
            if not self.use_direct_api:
                try:
                    model = genai.GenerativeModel(self.model_name)
                    response = model.generate_content(prompt)
                    
                    if not response.text:
                        raise ValueError("Empty response from Gemini API")
                        
                    generated_text = response.text
                    
                except Exception as sdk_error:
                    logger.warning(f"SDK method failed, falling back to direct API: {str(sdk_error)}")
                    self.use_direct_api = True
            
            # Fall back to direct API request if SDK fails or is not available
            if self.use_direct_api:
                url = f"{self.api_endpoint}?key={self.api_key}"
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.4,
                        "topK": 32,
                        "topP": 0.95,
                        "maxOutputTokens": 8192,
                    }
                }
                
                response = requests.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                # Extract the generated text
                generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Parse the generated text into structured questions
            questions = self._parse_generated_questions(generated_text, question_types)
            
            return {
                "success": True,
                "questions": questions
            }
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_prompt(self, content: str, num_questions: int, difficulty: str, question_types: List[str]) -> str:
        """Build a prompt for the Gemini API to generate questions."""
        type_descriptions = {
            "mcq_single": "multiple-choice questions with a single correct answer",
            "mcq_multiple": "multiple-choice questions with multiple correct answers",
            "true_false": "true/false questions",
            "text": "short answer questions"
        }
        
        # Create a list of requested question types
        requested_types = [type_descriptions.get(qt, qt) for qt in question_types]
        type_list = ", ".join(requested_types[:-1]) + " and " + requested_types[-1] if len(requested_types) > 1 else requested_types[0]
        
        prompt = f"""
You are an expert educational content creator who specializes in creating high-quality quiz questions.

Please analyze the following material and create {num_questions} {difficulty}-level quiz questions. 
Generate {type_list} based on the material below.

For each question:
1. Create a clear, concise question text
2. For multiple choice questions, provide 4 options with at least one correct answer
3. Clearly mark which answer(s) are correct
4. Ensure questions test understanding and comprehension appropriate for the specified difficulty level

MATERIAL TO ANALYZE:
{content}

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:

QUESTION 1:
Type: [question_type]
Question: [question_text]
Options:
A. [option_text]
B. [option_text]
C. [option_text]
D. [option_text]
Correct: [correct_option_letters]

QUESTION 2:
...and so on

For true/false questions, use only A and B options where A is True and B is False.
For text questions, provide a sample answer after the question.
"""
        return prompt
    
    def _validate_api_key(self):
        """Perform basic validation on the API key format"""
        # Google API keys typically start with "AI" for Gemini
        # and are about 39 characters long
        if not self.api_key or len(self.api_key) < 20:
            return False
        
        if not self.api_key.startswith("AI"):
            logger.warning(f"API key doesn't start with 'AI' prefix: {self.api_key[:2]}...")
            # We'll allow it, but log a warning
        
        return True
    
    def _setup_model_info(self):
        """Determine the best available Gemini model and API endpoint to use."""
        try:
            # Configure Gemini with the API key
            logger.info(f"Configuring Gemini with API key: {self.api_key[:4]}...{self.api_key[-4:]}")
            genai.configure(api_key=self.api_key)
            
            # Try to list available models
            logger.info("Fetching available Gemini models...")
            models = genai.list_models()
            model_names = [model.name for model in models]
            logger.info(f"Found {len(model_names)} available models")
            
            # Find suitable Gemini models for question generation
            # Prefer models optimized for text generation tasks
            preferred_models = [
                "models/gemini-2.5-flash",        # Stable flash model (as of Oct 2025)
                "models/gemini-flash-latest",      # Latest flash model
                "models/gemini-pro-latest",        # Latest pro model
                "models/gemini-2.5-pro",          # Stable pro model with better reasoning
            ]
            
            # Try to find one of our preferred models first
            selected_model = None
            for model in preferred_models:
                if model in model_names:
                    selected_model = model
                    logger.info(f"Using preferred model: {selected_model}")
                    break
            
            # If none of our preferred models are available, try any Gemini model
            if not selected_model:
                gemini_models = [m for m in model_names if 'gemini' in m]
                if gemini_models:
                    # Prefer models with "pro" or "flash" in the name
                    pro_models = [m for m in gemini_models if 'pro' in m]
                    flash_models = [m for m in gemini_models if 'flash' in m]
                    
                    if pro_models:
                        selected_model = pro_models[0]  # Pro models often have better reasoning
                    elif flash_models:
                        selected_model = flash_models[0]  # Flash models are faster
                    else:
                        selected_model = gemini_models[0]  # Any Gemini model as fallback
                        
                    logger.info(f"Using available Gemini model: {selected_model}")
            
            # Set the selected model or use a fallback
            if selected_model:
                self.model_name = selected_model
                self.use_direct_api = False  # Use the SDK instead of direct REST API
            else:
                # Fall back to a known model name if we couldn't find any
                self.model_name = "models/gemini-flash-latest"  # As of Oct 2025
                logger.warning(f"No suitable Gemini models found, defaulting to: {self.model_name}")
                self.use_direct_api = True
                
            # Set the appropriate API endpoint if using direct API
            if self.use_direct_api:
                model_id = self.model_name.split('/')[-1] if '/' in self.model_name else self.model_name
                # Use v1 API endpoint (not v1beta)
                self.api_endpoint = f"https://generativelanguage.googleapis.com/v1/models/{model_id}:generateContent"
            
        except Exception as e:
            # If we can't get the model list, default to the latest known model
            logger.warning(f"Failed to get available models: {str(e)}")
            self.model_name = "models/gemini-flash-latest"  # As of Oct 2025
            self.use_direct_api = True
            # Use v1 API endpoint (not v1beta)
            self.api_endpoint = f"https://generativelanguage.googleapis.com/v1/models/{model_id}:generateContent"
    
    def _parse_generated_questions(self, generated_text: str, question_types: List[str]) -> List[Dict[str, Any]]:
        """Parse the generated text into structured question objects."""
        questions = []
        raw_questions = generated_text.split("QUESTION ")[1:]  # Split by "QUESTION " and remove first empty item
        
        for i, raw_q in enumerate(raw_questions):
            try:
                # Extract question components
                lines = raw_q.strip().split('\n')
                q_num = i + 1
                
                # Find type line
                type_line = next((l for l in lines if l.startswith("Type:")), "")
                q_type = type_line.replace("Type:", "").strip().lower()
                
                # Map to our question types
                if "single" in q_type or "one correct" in q_type:
                    q_type = "mcq_single"
                elif "multiple" in q_type:
                    q_type = "mcq_multiple"
                elif "true" in q_type or "false" in q_type:
                    q_type = "true_false"
                elif "text" in q_type or "short answer" in q_type:
                    q_type = "text"
                else:
                    # Default to the first question type if we can't determine
                    q_type = question_types[0]
                
                # Find question text
                question_line = next((l for l in lines if l.startswith("Question:") or l.strip().endswith("?")), "")
                if question_line.startswith("Question:"):
                    question_text = question_line.replace("Question:", "").strip()
                else:
                    question_text = question_line.strip()
                
                # Find options and correct answer(s)
                options_start = None
                options_end = None
                correct_line = None
                
                for j, line in enumerate(lines):
                    if line.startswith("Options:"):
                        options_start = j + 1
                    elif line.startswith("Correct:"):
                        options_end = j
                        correct_line = line
                
                # Prepare question data
                question_data = {
                    "text": question_text,
                    "type": q_type,
                    "order": q_num - 1,
                    "choices": []
                }
                
                # Handle different question types
                if q_type in ["mcq_single", "mcq_multiple"]:
                    if options_start and options_end and correct_line:
                        options = lines[options_start:options_end]
                        correct_answers = correct_line.replace("Correct:", "").strip().split(",")
                        correct_letters = [c.strip() for c in correct_answers]
                        
                        for j, option in enumerate(options):
                            if option.strip():
                                # Extract option letter and text
                                parts = option.strip().split(".", 1)
                                if len(parts) > 1:
                                    letter = parts[0].strip()
                                    text = parts[1].strip()
                                    
                                    # Check if this option is marked as correct
                                    is_correct = letter in correct_letters
                                    
                                    question_data["choices"].append({
                                        "text": text,
                                        "is_correct": is_correct,
                                        "order": j
                                    })
                
                elif q_type == "true_false":
                    # For true/false, we need to determine if the answer is True or False
                    correct = "A" in correct_line.upper()  # A is True, B is False
                    
                    question_data["choices"] = [
                        {"text": "True", "is_correct": correct, "order": 0},
                        {"text": "False", "is_correct": not correct, "order": 1}
                    ]
                
                elif q_type == "text":
                    # For text questions, no choices needed
                    pass
                
                questions.append(question_data)
            except Exception as e:
                logger.error(f"Error parsing question {i+1}: {str(e)}")
                continue
        
        return questions