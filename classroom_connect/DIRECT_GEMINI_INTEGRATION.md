# Direct Gemini Integration for Quiz Generation

This document explains how to use the direct Gemini API integration for generating quiz questions and creating quizzes in the Classroom Connect application.

## Overview

The direct Gemini integration provides a simplified approach to generating quiz questions from educational material. Instead of requiring complex authentication flows, it directly uses the Gemini API with your API key to extract content from files and generate questions.

## Features

- Simple file upload and processing
- Direct communication with Gemini API
- Automatic quiz creation with generated questions
- Support for PDF, DOCX, and TXT files
- Customizable question generation parameters

## How to Use

### 1. Simple Quiz Generation Interface

The application provides a user-friendly interface for generating quizzes:

1. Navigate to "Staff Dashboard" > "Quiz Management"
2. Click on "Simple Quiz Generation (AI)" button
3. Upload your educational material (PDF, DOCX, or TXT)
4. Configure quiz details (title, description, etc.)
5. Set question generation options (number, difficulty, types)
6. Submit the form to generate questions and create a quiz

### 2. API Endpoint

For programmatic access, you can use the direct question generation API endpoint:

**Endpoint:** `/academic_integration/api/direct-generate-questions/`

**Method:** POST

**Authentication:** Staff session required

**Request Body:**
```json
{
  "fileContent": "base64-encoded-file-content",
  "fileType": "application/pdf",
  "quizTitle": "Generated Quiz",
  "quizDescription": "Automatically generated from uploaded content",
  "courseId": "optional-course-id",
  "tutorialNumber": null,
  "numQuestions": 5,
  "difficulty": "medium",
  "questionTypes": ["mcq_single", "mcq_multiple", "true_false"],
  "durationMinutes": 30,
  "quizType": "tutorial",
  "isActive": true,
  "showResults": true,
  "allowReview": true,
  "startDate": null,
  "completeByDate": null
}
```

**Response:**
```json
{
  "success": true,
  "quiz_id": 123,
  "question_count": 5,
  "message": "Successfully created quiz with 5 questions"
}
```

### 3. JavaScript Library

For frontend integration, you can use the provided JavaScript utility:

```javascript
// Import the library
// <script src="/static/academic_integration/js/directGeminiQuizGenerator.js"></script>

// Create a quiz from a file
const file = document.getElementById('fileInput').files[0];
const options = {
  quizTitle: "My Generated Quiz",
  numQuestions: 5,
  difficulty: "medium",
  questionTypes: ["mcq_single", "mcq_multiple", "true_false"]
};

try {
  const result = await DirectGeminiQuizGenerator.createQuizFromFile(file, options);
  console.log("Quiz created successfully:", result);
} catch (error) {
  console.error("Error creating quiz:", error);
}
```

## Configuration

The integration requires a Gemini API key to be set in your environment variables or `.env` file:

```
GEMINI_API_KEY=your-gemini-api-key-here
```

## Supported File Types

- **PDF** (.pdf)
- **Word Documents** (.docx)
- **Plain Text** (.txt)

## Question Types

- `mcq_single`: Multiple choice questions with a single correct answer
- `mcq_multiple`: Multiple choice questions with multiple correct answers
- `true_false`: True/False questions

## Difficulty Levels

- `easy`: Basic recall questions
- `medium`: Application questions (default)
- `hard`: Analysis and synthesis questions