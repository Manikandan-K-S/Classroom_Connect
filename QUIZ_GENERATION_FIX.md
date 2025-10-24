# Quiz Generation from Uploaded Materials Fix

## Issue Summary
The issue with generating quizzes from uploaded educational materials has been fixed. The problem was in the file content extraction and processing in the `generate_questions_from_content` function in `academic_integration/views.py`.

## Changes Made

1. **Updated the question generation endpoint**
   - Modified `generate_questions_from_content` in `academic_integration/views.py` to properly handle uploaded files
   - Improved error handling and logging to make debugging easier
   - Now using the dedicated `generate_questions_from_file` method from `GeminiQuestionGenerator` class

2. **Created diagnostic tools**
   - `file_upload_test.py` - Tests file uploading and question generation via the web API
   - `gemini_test_comprehensive.py` - A comprehensive test suite for the Gemini integration
   - `gemini_api_tester.py` - Simple API testing tool

## How to Test the Fix

### Option 1: Test with the Web Interface
1. Start the Django development server:
   ```
   cd classroom_connect
   python manage.py runserver
   ```
2. Log in as a staff member
3. Go to the quiz creation page and try uploading educational materials
4. The system should now successfully generate questions from your uploaded files

### Option 2: Test with the File Upload Test Script
1. Run the file upload test script with a sample file:
   ```
   python file_upload_test.py path/to/your/document.pdf --cookie "sessionid=your_session_cookie_value"
   ```
   - Replace `path/to/your/document.pdf` with the path to a PDF, DOCX, or TXT file
   - You'll need a valid session cookie value, which you can get from your browser after logging in

### Option 3: Test the Gemini API Directly
1. Run the comprehensive test:
   ```
   python gemini_test_comprehensive.py
   ```
   This will test both question generation and file content extraction

## Troubleshooting

If you encounter any issues:

1. **API Key Problems**
   - Make sure your `GEMINI_API_KEY` is correctly set in `classroom_connect/.env`
   - Use `gemini_debug.py` to verify API key validity and available models

2. **File Upload Issues**
   - Check the file format (PDF, DOCX, and plain text are supported)
   - Ensure the file size is reasonable (under 10MB recommended)
   - Use `file_upload_test.py` to debug specific files

3. **Content Extraction Issues**
   - Make sure PyPDF2 and python-docx are installed:
     ```
     pip install PyPDF2 python-docx
     ```
   - Some complex PDFs may not extract correctly (especially if they contain images or special formatting)

## Dependencies

The following dependencies are required for full functionality:

- python-dotenv
- google-generativeai
- PyPDF2 (for PDF extraction)
- python-docx (for DOCX extraction)
- requests

## Next Steps

- Consider implementing caching for generated questions to improve performance
- Add support for more file types (PowerPoint, Excel, etc.)
- Implement fallback models if the preferred Gemini models are unavailable