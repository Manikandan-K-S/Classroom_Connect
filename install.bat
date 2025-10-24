@echo off
echo ===============================
echo Classroom Connect Setup Wizard
echo ===============================
echo.

echo Step 1: Creating Python virtual environment...
python -m venv env
call env\Scripts\activate.bat

echo Step 2: Installing Classroom Connect dependencies...
pip install --upgrade pip
pip install --upgrade -r classroom_connect\requirements.txt

echo Step 3: Setting up Node.js dependencies for Academic Analyzer...
cd academic-analyzer
npm install
cd ..

echo Step 4: Creating .env file with Gemini API key placeholder...
echo # Environment variables for Classroom Connect > classroom_connect\.env
echo GEMINI_API_KEY=your_gemini_api_key_here >> classroom_connect\.env
echo ACADEMIC_ANALYZER_BASE_URL=http://localhost:5000 >> classroom_connect\.env

echo.
echo ===============================
echo Installation complete!
echo ===============================
echo.
echo IMPORTANT: Gemini API Configuration
echo.
echo To use the AI Question Generation feature:
echo.
echo 1. Get a Gemini API key from: https://ai.google.dev/
echo    - Create a Google Cloud project
echo    - Enable the Gemini API
echo    - Create an API key
echo.
echo 2. Edit classroom_connect\.env file with your API key:
echo    GEMINI_API_KEY=your_actual_api_key_here
echo.
echo 3. Verify your API setup:
echo    python gemini_debug.py
echo.
echo 4. Test question generation:
echo    python test_gemini.py
echo.
echo 5. Run the application:
echo    - Start the Django server:
echo      cd classroom_connect
echo      python backend_quiz\manage.py runserver
echo.
echo    - In a separate terminal, start the Academic Analyzer:
echo      cd academic-analyzer
echo      node server.js
echo.
echo If you encounter API issues, run gemini_debug.py for diagnostics.
echo.
pause