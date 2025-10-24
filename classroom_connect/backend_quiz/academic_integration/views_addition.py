def generate_questions_from_content(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to generate quiz questions from uploaded content using Gemini API.
    Requires staff authentication.
    """
    from django.http import JsonResponse
    import json
    import base64
    import io
    from PyPDF2 import PdfReader
    import docx
    
    # Ensure staff is logged in
    if not request.session.get('staff_email'):
        return JsonResponse({'success': False, 'error': 'Not authenticated as staff'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Parse request data
        data = json.loads(request.body)
        file_content = data.get('fileContent')
        file_type = data.get('fileType')
        num_questions = int(data.get('numQuestions', 5))
        difficulty = data.get('difficulty', 'medium')
        question_types = data.get('questionTypes', ['mcq_single', 'mcq_multiple', 'true_false'])
        
        # Validate required fields
        if not file_content:
            return JsonResponse({'success': False, 'error': 'No file content provided'}, status=400)
        
        # Process the file content based on type
        text_content = ""
        
        # Decode base64 content
        try:
            file_bytes = base64.b64decode(file_content.split(',')[1] if ',' in file_content else file_content)
            
            # Extract text based on file type
            if file_type == 'application/pdf':
                # Extract text from PDF
                pdf_file = io.BytesIO(file_bytes)
                pdf_reader = PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n\n"
            
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                # Extract text from DOCX
                doc_file = io.BytesIO(file_bytes)
                doc = docx.Document(doc_file)
                for para in doc.paragraphs:
                    text_content += para.text + "\n"
            
            else:
                # Assume plain text
                text_content = file_bytes.decode('utf-8')
            
            # Trim content if it's too long (Gemini has token limits)
            if len(text_content) > 30000:
                text_content = text_content[:30000] + "..."
            
            # Check if we extracted content successfully
            if not text_content.strip():
                return JsonResponse({'success': False, 'error': 'Could not extract text from file'}, status=400)
            
            # Use Gemini API to generate questions
            from academic_integration.utils.gemini_generator import GeminiQuestionGenerator
            generator = GeminiQuestionGenerator()
            result = generator.generate_questions(
                content=text_content,
                num_questions=num_questions,
                difficulty=difficulty,
                question_types=question_types
            )
            
            return JsonResponse(result)
        
        except Exception as e:
            logger.exception("Error processing file content")
            return JsonResponse({'success': False, 'error': f'Error processing file: {str(e)}'}, status=400)
    
    except Exception as e:
        logger.exception("Error generating questions")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)