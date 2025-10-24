# Classroom Connect with AI Question Generation

This project enhances the Classroom Connect application with AI-powered quiz question generation using the Google Gemini API.

## Features

- Generate quiz questions automatically from educational materials
- Support for multiple document formats (PDF, DOCX, TXT)
- Customizable question difficulty and types
- Integration with existing quiz system

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16.0 or higher
- Google Gemini API key (get one from [Google AI Studio](https://ai.google.dev/))

### Installation

1. Run the `install.bat` script to install dependencies:
   ```
   install.bat
   ```

2. Edit the `.env` file in the `classroom_connect` directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ACADEMIC_ANALYZER_BASE_URL=http://localhost:5000
   ```

3. Verify your API setup with the debug script:
   ```
   python gemini_debug.py
   ```

4. Test the question generation functionality:
   ```
   python test_gemini.py
   ```

5. Explore advanced examples:
   ```
   python gemini_examples.py
   ```

4. Activate the virtual environment (if not already activated):
   ```
   call env\Scripts\activate.bat
   ```

5. Start the Django development server:
   ```
   cd classroom_connect
   python backend_quiz/manage.py runserver
   ```

6. In a separate terminal, start the academic analyzer API:
   ```
   cd academic-analyzer
   node server.js
   ```

## Using AI Question Generation

1. Log in as a staff member
2. Go to "Create Quiz" page
3. Click the "AI Generate Questions" button
4. Upload an educational document (PDF, DOCX, or TXT)
5. Set the number of questions, difficulty level, and question types
6. Click "Generate Questions" to create questions based on the content
7. Review the generated questions and click "Add to Quiz" to include them

## Supported File Types

- PDF (`.pdf`) - Requires PyPDF2
- Word Documents (`.docx`) - Requires python-docx
- Plain Text (`.txt`)

## Troubleshooting

- **API Key Issues**: Make sure your Gemini API key is correctly set in the `.env` file
- **File Format Issues**: Ensure your files are properly formatted and not corrupted
- **Question Generation Errors**: Some content may not generate good questions; try using different sections of text or adjusting the difficulty

## License

This project is for educational use only.