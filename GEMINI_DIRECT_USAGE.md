# Simplified Gemini Question Generation

This guide explains how to use the simplified Gemini question generation script that bypasses the Django backend and directly uses the Gemini API.

## Prerequisites

1. Python 3.8 or higher
2. A valid Google Gemini API key (get one from [Google AI Studio](https://ai.google.dev/))
3. Required packages installed:
   - google-generativeai
   - python-dotenv
   - PyPDF2 (for PDF files)
   - python-docx (for DOCX files)

## Setup

1. Make sure your API key is set in the `.env` file in the `classroom_connect` directory:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

2. Install the required packages if not already installed:
   ```
   pip install google-generativeai python-dotenv PyPDF2 python-docx
   ```

## Usage

Run the script with a file path as an argument:

```
python gemini_file_upload_test.py "path/to/your/file.pdf"
```

### Additional Options

- `--questions`: Number of questions to generate (default: 3)
  ```
  python gemini_file_upload_test.py "path/to/your/file.pdf" --questions 5
  ```

- `--difficulty`: Set question difficulty to "easy", "medium", or "hard" (default: "medium")
  ```
  python gemini_file_upload_test.py "path/to/your/file.pdf" --difficulty easy
  ```

- `--types`: Specify question types to generate (default: mcq_single, mcq_multiple, true_false)
  ```
  python gemini_file_upload_test.py "path/to/your/file.pdf" --types mcq_single true_false
  ```

## Supported File Types

- PDF (`.pdf`) - Requires PyPDF2
- Word Documents (`.docx`) - Requires python-docx
- Plain Text (`.txt`, `.md`)

## Troubleshooting

- **API Key Issues**: Make sure your Gemini API key is correctly set in the `.env` file
- **File Format Issues**: Ensure your files are properly formatted and not corrupted
- **Question Generation Errors**: Some content may not generate good questions; try using different sections of text or adjusting the difficulty
- **Package Issues**: Make sure all required packages are installed based on the file types you're using

## Examples

1. Generate 3 medium difficulty questions from a PDF file:
   ```
   python gemini_file_upload_test.py "C:\Users\username\Documents\lecture.pdf"
   ```

2. Generate 5 easy questions from a text file with specific question types:
   ```
   python gemini_file_upload_test.py "notes.txt" --questions 5 --difficulty easy --types mcq_single true_false
   ```

3. Generate 2 hard questions from a Word document:
   ```
   python gemini_file_upload_test.py "assignment.docx" --questions 2 --difficulty hard
   ```