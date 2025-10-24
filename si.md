# System Implementation: Classroom Connect & Academic Analyzer

## Table of Contents

1. [Introduction](#introduction)
2. [Development Environment Setup](#development-environment-setup)
3. [Backend Implementation](#backend-implementation)
   - [Classroom Connect (Django)](#classroom-connect-django)
   - [Academic Analyzer (Node.js)](#academic-analyzer-nodejs)
4. [Database Implementation](#database-implementation)
   - [Django Models Implementation](#django-models-implementation)
   - [MongoDB Schema Implementation](#mongodb-schema-implementation)
5. [API Implementation](#api-implementation)
   - [RESTful API Endpoints](#restful-api-endpoints)
   - [API Integration Between Systems](#api-integration-between-systems)
6. [Authentication Implementation](#authentication-implementation)
7. [Frontend Implementation](#frontend-implementation)
   - [Templates and Views](#templates-and-views)
   - [JavaScript and AJAX](#javascript-and-ajax)
   - [Data Visualization Implementation](#data-visualization-implementation)
8. [Testing Implementation](#testing-implementation)
   - [Unit Testing](#unit-testing)
   - [Integration Testing](#integration-testing)
   - [API Testing](#api-testing)
9. [Deployment Process](#deployment-process)
10. [Maintenance and Monitoring](#maintenance-and-monitoring)
11. [Known Issues and Workarounds](#known-issues-and-workarounds)
12. [Future Implementation Roadmap](#future-implementation-roadmap)

## Introduction

This document details the practical implementation of the Classroom Connect and Academic Analyzer systems. While the System Design document (sd.md) outlines the architectural design and system interactions, this System Implementation document focuses on how these systems were actually built, configured, and deployed. The document provides implementation-specific details, code snippets, configuration settings, and practical considerations that were addressed during development.

## Development Environment Setup

### Prerequisites

```
# For Classroom Connect (Django)
Python 3.8+
pip
virtualenv
PostgreSQL (production) / SQLite (development)

# For Academic Analyzer (Node.js)
Node.js 14+
npm
MongoDB 4.4+
```

### Local Development Environment Setup

#### Classroom Connect Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
cd backend_quiz
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### Academic Analyzer Setup

```bash
# Install dependencies
cd academic-analyzer
npm install

# Configure MongoDB connection
# Edit config/db.js with your MongoDB URI

# Run database check
node db_check.js

# Start server
node server.js
```

## Backend Implementation

### Classroom Connect (Django)

#### Project Structure

The Django project follows a standard Django project structure with additional apps for specific functionality:

- `backend_quiz/`: Main project directory
  - `backend_quiz/`: Project settings and root URL configuration
  - `quiz/`: Main app for quiz functionality
  - `academic_integration/`: App for integration with Academic Analyzer

#### Key Django Settings

The following settings in `settings.py` were customized for the project:

```python
# backend_quiz/backend_quiz/settings.py
INSTALLED_APPS = [
    # Django default apps...
    'quiz',
    'academic_integration',
    'channels',  # For WebSocket support
    'rest_framework',  # For API endpoints
    'corsheaders',  # For cross-origin resource sharing
]

MIDDLEWARE = [
    # Django default middleware...
    'corsheaders.middleware.CorsMiddleware',  # Added for CORS
]

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # In development only; restrict in production

# Channels configuration
ASGI_APPLICATION = 'backend_quiz.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        # Use Redis in production
    },
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

#### URL Configuration

```python
# backend_quiz/backend_quiz/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('quiz/', include('quiz.urls')),
    path('academic/', include('academic_integration.urls')),
]
```

```python
# backend_quiz/quiz/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('quiz/create/', views.create_quiz, name='create_quiz'),
    path('quiz/edit/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('quiz/list/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    # API endpoints
    path('api/quizzes/', views.QuizListAPI.as_view(), name='quiz_list_api'),
    path('api/quizzes/<int:pk>/', views.QuizDetailAPI.as_view(), name='quiz_detail_api'),
]
```

```python
# backend_quiz/academic_integration/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('sync-performance/', views.sync_performance, name='sync_performance'),
    path('student-progress/<int:student_id>/', views.get_student_progress, name='student_progress'),
    path('course-analytics/<str:course_id>/', views.get_course_analytics, name='course_analytics'),
]
```

### Academic Analyzer (Node.js)

#### Project Structure

The Node.js application follows a modular structure:

- `academic-analyzer/`: Main project directory
  - `config/`: Configuration files
  - `controllers/`: Request handlers
  - `models/`: MongoDB schema definitions
  - `routes/`: API route definitions
  - `server.js`: Entry point

#### Express Server Configuration

```javascript
// server.js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const connectDB = require('./config/db');

// Load env variables
dotenv.config();

// Connect to MongoDB
connectDB();

const app = express();

// Middleware
app.use(express.json());
app.use(cors());

// Routes
app.use('/students', require('./routes/studentRoutes'));
app.use('/staff', require('./routes/staffRoutes'));

// Error handler middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Server error', error: process.env.NODE_ENV === 'development' ? err.message : undefined });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

#### MongoDB Connection

```javascript
// config/db.js
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/academic_analyzer', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log(`MongoDB connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`Error connecting to MongoDB: ${error.message}`);
    process.exit(1);
  }
};

module.exports = connectDB;
```

## Database Implementation

### Django Models Implementation

#### User and Quiz Models

```python
# backend_quiz/quiz/models.py
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    course_id = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.course_id} - {self.title}"

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    time_limit = models.IntegerField(default=30)  # in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    points = models.IntegerField(default=1)

    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"
```

#### Student Model in Academic Integration

```python
# backend_quiz/academic_integration/models.py
from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    course_ids = models.JSONField(default=list)  # List of course IDs the student is enrolled in

    def __str__(self):
        return f"{self.student_id} - {self.user.username}"
```

### MongoDB Schema Implementation

#### Student and Performance Models

```javascript
// models/Student.js
const mongoose = require('mongoose');

const StudentSchema = new mongoose.Schema({
  studentId: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  enrolledCourses: [{
    type: String,
    ref: 'Course'
  }],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Student', StudentSchema);
```

```javascript
// models/Course.js
const mongoose = require('mongoose');

const CourseSchema = new mongoose.Schema({
  courseId: {
    type: String,
    required: true,
    unique: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String
  },
  instructorId: {
    type: String,
    ref: 'Teacher'
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Course', CourseSchema);
```

```javascript
// models/Performance.js
const mongoose = require('mongoose');

const PerformanceSchema = new mongoose.Schema({
  studentId: {
    type: String,
    required: true,
    ref: 'Student'
  },
  courseId: {
    type: String,
    required: true,
    ref: 'Course'
  },
  assessmentType: {
    type: String,
    required: true,
    enum: ['quiz', 'assignment', 'exam', 'project']
  },
  assessmentId: {
    type: String,
    required: true
  },
  score: {
    type: Number,
    required: true
  },
  maxScore: {
    type: Number,
    required: true
  },
  completedAt: {
    type: Date,
    default: Date.now
  }
});

// Compound index for efficient querying
PerformanceSchema.index({ studentId: 1, courseId: 1, assessmentId: 1 }, { unique: true });

module.exports = mongoose.model('Performance', PerformanceSchema);
```

```javascript
// models/Teacher.js
const mongoose = require('mongoose');

const TeacherSchema = new mongoose.Schema({
  teacherId: {
    type: String,
    required: true,
    unique: true
  },
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  department: {
    type: String
  },
  courses: [{
    type: String,
    ref: 'Course'
  }],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Teacher', TeacherSchema);
```

## API Implementation

### RESTful API Endpoints

#### Academic Analyzer API Implementation

```javascript
// routes/staffRoutes.js
const express = require('express');
const router = express.Router();
const staffController = require('../controllers/staffController');

// Course routes
router.get('/courses', staffController.getAllCourses);
router.get('/course/:id', staffController.getCourseById);
router.post('/course', staffController.createCourse);
router.put('/course/:id', staffController.updateCourse);
router.delete('/course/:id', staffController.deleteCourse);

// Student routes
router.get('/students', staffController.getAllStudents);
router.get('/student/:id', staffController.getStudentById);
router.post('/student', staffController.createStudent);
router.put('/student/:id', staffController.updateStudent);
router.delete('/student/:id', staffController.deleteStudent);

// Analytics routes
router.get('/course-analytics', staffController.getCourseAnalytics);
router.get('/student-performance', staffController.getStudentPerformance);
router.put('/student-marks', staffController.updateStudentMarks);

module.exports = router;
```

```javascript
// controllers/staffController.js (getCourseAnalytics implementation)
exports.getCourseAnalytics = async (req, res) => {
  try {
    const { courseId } = req.query;
    
    if (!courseId) {
      return res.status(400).json({ message: 'Course ID is required' });
    }

    // Get all performance records for this course
    const performances = await Performance.find({ courseId });
    
    if (!performances || performances.length === 0) {
      return res.status(404).json({ message: 'No performance data found for this course' });
    }

    // Calculate statistics
    let totalStudents = new Set();
    let assessmentTypes = {};
    let totalScores = 0;
    let totalMaxScores = 0;
    
    performances.forEach(perf => {
      totalStudents.add(perf.studentId);
      
      // Group by assessment type
      if (!assessmentTypes[perf.assessmentType]) {
        assessmentTypes[perf.assessmentType] = {
          count: 0,
          totalScore: 0,
          totalMaxScore: 0
        };
      }
      
      assessmentTypes[perf.assessmentType].count++;
      assessmentTypes[perf.assessmentType].totalScore += perf.score;
      assessmentTypes[perf.assessmentType].totalMaxScore += perf.maxScore;
      
      totalScores += perf.score;
      totalMaxScores += perf.maxScore;
    });
    
    // Calculate averages
    const courseAverage = (totalMaxScores > 0) ? (totalScores / totalMaxScores * 100).toFixed(2) : 0;
    
    // Process assessment type statistics
    Object.keys(assessmentTypes).forEach(type => {
      const data = assessmentTypes[type];
      data.average = (data.totalMaxScore > 0) 
        ? (data.totalScore / data.totalMaxScore * 100).toFixed(2) 
        : 0;
    });
    
    // Return analytics data
    res.json({
      courseId,
      studentCount: totalStudents.size,
      assessmentCount: performances.length,
      courseAverage,
      assessmentBreakdown: assessmentTypes
    });
  } catch (error) {
    console.error('Error getting course analytics:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};
```

#### Classroom Connect API Implementation

```python
# backend_quiz/academic_integration/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators.http import require_http_methods
import json
import requests
from .models import Student
from quiz.models import QuizAttempt, Quiz, User

@csrf_exempt
@require_http_methods(["POST"])
def sync_performance(request):
    """
    Endpoint to sync quiz performance data with Academic Analyzer
    """
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        quiz_id = data.get('quiz_id')
        
        # Validate inputs
        if not student_id or not quiz_id:
            return JsonResponse({'error': 'student_id and quiz_id are required'}, status=400)
        
        # Get student and quiz attempt
        try:
            student = Student.objects.get(student_id=student_id)
            quiz = Quiz.objects.get(id=quiz_id)
            quiz_attempt = QuizAttempt.objects.filter(
                user=student.user,
                quiz=quiz
            ).order_by('-completed_at').first()
            
            if not quiz_attempt:
                return JsonResponse({'error': 'No quiz attempt found'}, status=404)
                
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
        except Quiz.DoesNotExist:
            return JsonResponse({'error': 'Quiz not found'}, status=404)
            
        # Prepare data for Academic Analyzer
        performance_data = {
            'studentId': student_id,
            'courseId': quiz.course.course_id,
            'assessmentType': 'quiz',
            'assessmentId': f'quiz_{quiz_id}',
            'score': quiz_attempt.score,
            'maxScore': sum(question.points for question in quiz.questions.all())
        }
        
        # Send data to Academic Analyzer
        response = requests.post(
            'http://localhost:5000/staff/student-marks',
            json=performance_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            return JsonResponse({'error': f'Academic Analyzer API error: {response.text}'}, status=500)
            
        return JsonResponse({'message': 'Performance data synced successfully'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
```

### API Integration Between Systems

#### Integration Implementation in Django

```python
# backend_quiz/academic_integration/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

@csrf_exempt
def get_student_progress(request, student_id):
    """
    Get student progress from Academic Analyzer
    """
    try:
        # Get student progress from Academic Analyzer
        response = requests.get(
            f'http://localhost:5000/staff/student-performance?studentId={student_id}'
        )
        
        if response.status_code != 200:
            return JsonResponse({'error': f'Academic Analyzer API error: {response.text}'}, status=500)
            
        # Return the data from Academic Analyzer
        return JsonResponse(response.json())
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
def get_course_analytics(request, course_id):
    """
    Get course analytics from Academic Analyzer
    """
    try:
        # Get course analytics from Academic Analyzer
        response = requests.get(
            f'http://localhost:5000/staff/course-analytics?courseId={course_id}'
        )
        
        if response.status_code != 200:
            return JsonResponse({'error': f'Academic Analyzer API error: {response.text}'}, status=500)
            
        # Return the data from Academic Analyzer
        return JsonResponse(response.json())
        
    except Exception as e:
        return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
```

## Authentication Implementation

### Django Authentication Implementation

```python
# backend_quiz/quiz/views.py (authentication implementation)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set user type (student/teacher)
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'student':
                # Create student profile
                from academic_integration.models import Student
                student_id = form.cleaned_data.get('id_number')
                Student.objects.create(
                    user=user,
                    student_id=student_id,
                    course_ids=[]
                )
            
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'quiz/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                # Redirect based on user type
                if hasattr(user, 'student'):
                    return redirect('student_dashboard')
                else:
                    return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'quiz/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')
```

### Academic Analyzer Authentication Implementation

```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');

module.exports = function(req, res, next) {
  // Get token from header
  const token = req.header('x-auth-token');

  // Check if no token
  if (!token) {
    return res.status(401).json({ msg: 'No token, authorization denied' });
  }

  // Verify token
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded.user;
    next();
  } catch (err) {
    res.status(401).json({ msg: 'Token is not valid' });
  }
};
```

```javascript
// controllers/authController.js
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const Teacher = require('../models/Teacher');

// Login for teachers/staff
exports.login = async (req, res) => {
  const { email, password } = req.body;

  try {
    // Check if user exists
    const teacher = await Teacher.findOne({ email });
    if (!teacher) {
      return res.status(400).json({ msg: 'Invalid credentials' });
    }

    // Verify password
    const isMatch = await bcrypt.compare(password, teacher.password);
    if (!isMatch) {
      return res.status(400).json({ msg: 'Invalid credentials' });
    }

    // Return JWT token
    const payload = {
      user: {
        id: teacher.id,
        role: 'teacher'
      }
    };

    jwt.sign(
      payload,
      process.env.JWT_SECRET,
      { expiresIn: '24h' },
      (err, token) => {
        if (err) throw err;
        res.json({ token });
      }
    );
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
};
```

## Frontend Implementation

### Templates and Views

#### Django Template Implementation

```html
<!-- backend_quiz/quiz/templates/quiz/quiz_detail.html -->
{% extends 'quiz/base.html' %}

{% block content %}
<div class="container mt-4">
  <div class="card">
    <div class="card-header bg-primary text-white">
      <h2>{{ quiz.title }}</h2>
    </div>
    <div class="card-body">
      <p><strong>Description:</strong> {{ quiz.description }}</p>
      <p><strong>Course:</strong> {{ quiz.course.title }} ({{ quiz.course.course_id }})</p>
      <p><strong>Time Limit:</strong> {{ quiz.time_limit }} minutes</p>
      <p><strong>Number of Questions:</strong> {{ quiz.questions.count }}</p>
      
      {% if is_teacher %}
        <a href="{% url 'edit_quiz' quiz.id %}" class="btn btn-warning">Edit Quiz</a>
        <button class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#deleteModal">Delete Quiz</button>
      {% else %}
        <a href="{% url 'take_quiz' quiz.id %}" class="btn btn-success">Take Quiz</a>
        
        {% if previous_attempts %}
          <h4 class="mt-4">Your Previous Attempts</h4>
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Date</th>
                <th>Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {% for attempt in previous_attempts %}
                <tr>
                  <td>{{ attempt.completed_at|date:"M d, Y H:i" }}</td>
                  <td>{{ attempt.score }}%</td>
                  <td>
                    <a href="{% url 'quiz_results' attempt.id %}" class="btn btn-sm btn-info">View Results</a>
                  </td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        {% endif %}
      {% endif %}
    </div>
  </div>
</div>

<!-- Delete Confirmation Modal -->
{% if is_teacher %}
<div class="modal fade" id="deleteModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header bg-danger text-white">
        <h5 class="modal-title">Confirm Delete</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        Are you sure you want to delete this quiz? This action cannot be undone.
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <form method="post" action="{% url 'delete_quiz' quiz.id %}">
          {% csrf_token %}
          <button type="submit" class="btn btn-danger">Delete</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endif %}
{% endblock %}
```

### JavaScript and AJAX

```javascript
// Static JavaScript for quiz taking functionality
document.addEventListener('DOMContentLoaded', function() {
  const quizForm = document.getElementById('quiz-form');
  const timerDisplay = document.getElementById('timer-display');
  const submitButton = document.getElementById('submit-quiz');
  
  if (!quizForm || !timerDisplay) return;
  
  // Initialize timer
  const timeLimit = parseInt(timerDisplay.dataset.timeLimit || '30');
  let timeRemaining = timeLimit * 60; // Convert to seconds
  
  // Timer function
  const timer = setInterval(function() {
    timeRemaining--;
    
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    
    // Format display
    timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    
    // Change color when less than 5 minutes remain
    if (timeRemaining <= 300) {
      timerDisplay.classList.add('text-danger');
    }
    
    // Auto-submit when time runs out
    if (timeRemaining <= 0) {
      clearInterval(timer);
      submitButton.click();
    }
  }, 1000);
  
  // Save answers periodically
  setInterval(function() {
    const formData = new FormData(quizForm);
    
    // Add current timestamp
    formData.append('autosave', 'true');
    
    // Send AJAX request
    fetch(quizForm.action, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('Answers autosaved');
      }
    })
    .catch(error => console.error('Error autosaving:', error));
  }, 30000); // Every 30 seconds
  
  // Helper function to get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
```

### Data Visualization Implementation

```javascript
// Chart.js implementation for analytics dashboard
document.addEventListener('DOMContentLoaded', function() {
  const courseAnalyticsElement = document.getElementById('course-analytics-chart');
  
  if (!courseAnalyticsElement) return;
  
  const courseId = courseAnalyticsElement.dataset.courseId;
  
  // Fetch course analytics data
  fetch(`/academic/course-analytics/${courseId}/`)
    .then(response => response.json())
    .then(data => {
      // Create chart for assessment breakdown
      const assessmentTypes = Object.keys(data.assessmentBreakdown || {});
      const assessmentAverages = assessmentTypes.map(type => 
        data.assessmentBreakdown[type].average);
      
      new Chart(courseAnalyticsElement, {
        type: 'bar',
        data: {
          labels: assessmentTypes.map(type => type.charAt(0).toUpperCase() + type.slice(1)),
          datasets: [{
            label: 'Average Score (%)',
            data: assessmentAverages,
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(54, 162, 235, 0.5)',
              'rgba(255, 206, 86, 0.5)',
              'rgba(75, 192, 192, 0.5)'
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          },
          plugins: {
            title: {
              display: true,
              text: `Course Performance: ${data.courseAverage}% Average`
            },
            subtitle: {
              display: true,
              text: `${data.studentCount} Students, ${data.assessmentCount} Assessments`
            }
          }
        }
      });
    })
    .catch(error => {
      console.error('Error fetching analytics:', error);
      courseAnalyticsElement.innerHTML = '<div class="alert alert-danger">Failed to load analytics</div>';
    });
});
```

## Testing Implementation

### Unit Testing

#### Django Unit Tests

```python
# backend_quiz/quiz/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Quiz, Question, Choice, Course, QuizAttempt

class QuizModelTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            course_id='TEST101',
            title='Test Course',
            description='A test course'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='A test quiz',
            course=self.course,
            time_limit=15
        )
        
    def test_quiz_creation(self):
        self.assertEqual(self.quiz.title, 'Test Quiz')
        self.assertEqual(self.quiz.course.course_id, 'TEST101')
        self.assertEqual(self.quiz.time_limit, 15)
        
    def test_quiz_str_representation(self):
        self.assertEqual(str(self.quiz), 'Test Quiz')

class QuizViewTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            course_id='TEST101',
            title='Test Course',
            description='A test course'
        )
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            description='A test quiz',
            course=self.course,
            time_limit=15
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
    def test_quiz_list_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('quiz_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Quiz')
        
    def test_quiz_detail_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('quiz_detail', args=[self.quiz.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Quiz')
        self.assertContains(response, 'Test Course')
```

#### Node.js Unit Tests

```javascript
// test/controllers/staffController.test.js
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const request = require('supertest');
const express = require('express');
const Course = require('../../models/Course');
const Student = require('../../models/Student');
const Performance = require('../../models/Performance');
const staffController = require('../../controllers/staffController');

let mongoServer;
const app = express();
app.use(express.json());

// Setup routes for testing
app.get('/course-analytics', staffController.getCourseAnalytics);
app.get('/student-performance', staffController.getStudentPerformance);
app.put('/student-marks', staffController.updateStudentMarks);

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  const uri = mongoServer.getUri();
  await mongoose.connect(uri);
});

afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});

describe('Staff Controller Tests', () => {
  beforeEach(async () => {
    // Clear collections
    await Course.deleteMany({});
    await Student.deleteMany({});
    await Performance.deleteMany({});
    
    // Create test data
    const course = await Course.create({
      courseId: 'TEST101',
      title: 'Test Course',
      description: 'A test course',
      instructorId: 'T12345'
    });
    
    const student = await Student.create({
      studentId: 'S12345',
      name: 'Test Student',
      email: 'test@example.com',
      enrolledCourses: ['TEST101']
    });
    
    await Performance.create({
      studentId: 'S12345',
      courseId: 'TEST101',
      assessmentType: 'quiz',
      assessmentId: 'quiz_1',
      score: 85,
      maxScore: 100
    });
    
    await Performance.create({
      studentId: 'S12345',
      courseId: 'TEST101',
      assessmentType: 'exam',
      assessmentId: 'exam_1',
      score: 75,
      maxScore: 100
    });
  });
  
  test('getCourseAnalytics should return course statistics', async () => {
    const response = await request(app)
      .get('/course-analytics')
      .query({ courseId: 'TEST101' });
      
    expect(response.statusCode).toBe(200);
    expect(response.body).toHaveProperty('courseId', 'TEST101');
    expect(response.body).toHaveProperty('studentCount', 1);
    expect(response.body).toHaveProperty('assessmentCount', 2);
    expect(response.body).toHaveProperty('courseAverage', '80.00');
    expect(response.body.assessmentBreakdown).toHaveProperty('quiz');
    expect(response.body.assessmentBreakdown).toHaveProperty('exam');
  });
  
  test('getStudentPerformance should return student performance data', async () => {
    const response = await request(app)
      .get('/student-performance')
      .query({ studentId: 'S12345', courseId: 'TEST101' });
      
    expect(response.statusCode).toBe(200);
    expect(response.body).toHaveProperty('studentId', 'S12345');
    expect(response.body).toHaveProperty('courseId', 'TEST101');
    expect(response.body).toHaveProperty('performances');
    expect(response.body.performances.length).toBe(2);
    expect(response.body).toHaveProperty('averageScore', '80.00');
  });
});
```

### Integration Testing

```python
# backend_quiz/academic_integration/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from .models import Student
from quiz.models import Quiz, Course, QuizAttempt

class AcademicIntegrationTests(TestCase):
    def setUp(self):
        # Create test user and student
        self.user = User.objects.create_user(
            username='teststudent',
            email='student@example.com',
            password='testpassword'
        )
        self.student = Student.objects.create(
            user=self.user,
            student_id='S12345',
            course_ids=['CS101']
        )
        
        # Create course and quiz
        self.course = Course.objects.create(
            course_id='CS101',
            title='Computer Science 101',
            description='Introduction to Computer Science'
        )
        self.quiz = Quiz.objects.create(
            title='Week 1 Quiz',
            description='Basic concepts quiz',
            course=self.course,
            time_limit=15
        )
        
        # Create quiz attempt
        self.quiz_attempt = QuizAttempt.objects.create(
            user=self.user,
            quiz=self.quiz,
            score=85.0
        )
        
        # Set up test client
        self.client = Client()
        
    @patch('academic_integration.views.requests.post')
    def test_sync_performance(self, mock_post):
        # Mock successful API response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'message': 'Performance data saved'}
        
        # Send request to sync performance
        data = {
            'student_id': 'S12345',
            'quiz_id': self.quiz.id
        }
        response = self.client.post(
            reverse('sync_performance'),
            data=data,
            content_type='application/json'
        )
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Performance data synced successfully'})
        
        # Assert API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], 'http://localhost:5000/staff/student-marks')
        
        # Check payload
        payload = kwargs['json']
        self.assertEqual(payload['studentId'], 'S12345')
        self.assertEqual(payload['courseId'], 'CS101')
        self.assertEqual(payload['assessmentType'], 'quiz')
        self.assertEqual(payload['score'], 85.0)
```

### API Testing

```javascript
// test/api/staffRoutes.test.js
const request = require('supertest');
const express = require('express');
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const staffRoutes = require('../../routes/staffRoutes');

// Create express app for testing
const app = express();
app.use(express.json());
app.use('/staff', staffRoutes);

let mongoServer;

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  const uri = mongoServer.getUri();
  await mongoose.connect(uri);
});

afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});

describe('Staff API Routes', () => {
  let courseId;
  let studentId;
  
  beforeEach(async () => {
    // Create test course
    const courseResponse = await request(app)
      .post('/staff/course')
      .send({
        courseId: 'API101',
        title: 'API Testing',
        description: 'Learning API testing',
        instructorId: 'T54321'
      });
    courseId = courseResponse.body._id;
    
    // Create test student
    const studentResponse = await request(app)
      .post('/staff/student')
      .send({
        studentId: 'S54321',
        name: 'API Test Student',
        email: 'apitest@example.com',
        enrolledCourses: ['API101']
      });
    studentId = studentResponse.body._id;
    
    // Create performance record
    await request(app)
      .put('/staff/student-marks')
      .send({
        studentId: 'S54321',
        courseId: 'API101',
        assessmentType: 'quiz',
        assessmentId: 'api_quiz_1',
        score: 90,
        maxScore: 100
      });
  });
  
  test('GET /staff/courses should return all courses', async () => {
    const response = await request(app).get('/staff/courses');
    expect(response.statusCode).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
    expect(response.body.length).toBeGreaterThan(0);
    expect(response.body[0]).toHaveProperty('courseId', 'API101');
  });
  
  test('GET /staff/course/:id should return a specific course', async () => {
    const response = await request(app).get(`/staff/course/${courseId}`);
    expect(response.statusCode).toBe(200);
    expect(response.body).toHaveProperty('courseId', 'API101');
    expect(response.body).toHaveProperty('title', 'API Testing');
  });
  
  test('GET /staff/course-analytics should return course analytics', async () => {
    const response = await request(app)
      .get('/staff/course-analytics')
      .query({ courseId: 'API101' });
      
    expect(response.statusCode).toBe(200);
    expect(response.body).toHaveProperty('courseId', 'API101');
    expect(response.body).toHaveProperty('studentCount', 1);
    expect(response.body).toHaveProperty('assessmentBreakdown');
    expect(response.body.assessmentBreakdown).toHaveProperty('quiz');
  });
});
```

## Deployment Process

### Development to Production Workflow

1. **Local Development**
   ```bash
   # For Django
   python manage.py runserver
   
   # For Node.js
   npm run dev
   ```

2. **Testing Before Deployment**
   ```bash
   # For Django
   python manage.py test
   
   # For Node.js
   npm test
   ```

3. **Production Build**
   ```bash
   # For Django - collect static files
   python manage.py collectstatic
   
   # For Node.js - create production build
   npm run build
   ```

4. **Deployment Steps**

   **Django Application Deployment:**

   ```bash
   # 1. Set up virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # 2. Install production dependencies
   pip install -r requirements.txt
   
   # 3. Set environment variables
   export DJANGO_SETTINGS_MODULE=backend_quiz.settings
   export DEBUG=False
   export SECRET_KEY='your-secret-key'
   export ALLOWED_HOSTS='yourdomain.com'
   
   # 4. Run migrations
   python manage.py migrate
   
   # 5. Collect static files
   python manage.py collectstatic --noinput
   
   # 6. Configure Gunicorn
   gunicorn backend_quiz.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```

   **Node.js Application Deployment:**

   ```bash
   # 1. Install production dependencies
   npm ci --production
   
   # 2. Set environment variables
   export NODE_ENV=production
   export PORT=5000
   export MONGO_URI='mongodb://username:password@host:port/database'
   export JWT_SECRET='your-jwt-secret'
   
   # 3. Start the application with PM2
   pm2 start server.js --name "academic-analyzer"
   ```

5. **Web Server Configuration (Nginx)**

   ```nginx
   # Classroom Connect (Django)
   server {
       listen 80;
       server_name classroom.example.com;
       
       location /static/ {
           alias /path/to/classroom_connect/backend_quiz/static/;
       }
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   
   # Academic Analyzer (Node.js)
   server {
       listen 80;
       server_name analyzer.example.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

### Continuous Integration/Continuous Deployment

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test-django:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        cd classroom_connect
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run Django Tests
      run: |
        cd classroom_connect/backend_quiz
        python manage.py test
  
  test-nodejs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '14'
    - name: Install dependencies
      run: |
        cd academic-analyzer
        npm ci
    - name: Run Node.js Tests
      run: |
        cd academic-analyzer
        npm test
  
  deploy:
    needs: [test-django, test-nodejs]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.SSH_HOST }}
        username: ${{ secrets.SSH_USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /path/to/deployment
          git pull origin main
          cd classroom_connect
          source venv/bin/activate
          pip install -r requirements.txt
          cd backend_quiz
          python manage.py migrate
          python manage.py collectstatic --noinput
          sudo supervisorctl restart classroom_connect
          cd ../../academic-analyzer
          npm ci --production
          pm2 reload academic-analyzer
```

## Maintenance and Monitoring

### Logging Implementation

#### Django Logging Configuration

```python
# backend_quiz/backend_quiz/settings.py (logging section)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'quiz': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'academic_integration': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

#### Node.js Logging Implementation

```javascript
// logger.js
const winston = require('winston');
const path = require('path');
const fs = require('fs');

// Create logs directory if it doesn't exist
const logDir = 'logs';
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir);
}

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 'academic-analyzer' },
  transports: [
    new winston.transports.File({
      filename: path.join(logDir, 'error.log'),
      level: 'error',
      maxsize: 10485760, // 10MB
      maxFiles: 10,
    }),
    new winston.transports.File({
      filename: path.join(logDir, 'combined.log'),
      maxsize: 10485760, // 10MB
      maxFiles: 10,
    })
  ],
});

// Add console transport in development
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    ),
  }));
}

module.exports = logger;
```

### Monitoring Implementation

```javascript
// app.js (Express monitoring middleware)
const promClient = require('prom-client');
const morgan = require('morgan');

// Create a Registry to register the metrics
const register = new promClient.Registry();

// Add a default label which is added to all metrics
register.setDefaultLabels({
  app: 'academic-analyzer'
});

// Enable the collection of default metrics
promClient.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDurationMicroseconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

register.registerMetric(httpRequestDurationMicroseconds);

// Morgan logging middleware
app.use(morgan('combined'));

// Metrics middleware
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// Response time tracking middleware
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    if (req.path !== '/metrics') {
      httpRequestDurationMicroseconds
        .labels(req.method, req.route?.path || req.path, res.statusCode.toString())
        .observe(duration);
    }
  });
  next();
});
```

## Known Issues and Workarounds

### Import Error in academic_integration/views.py

**Issue**: The `views.py` file was trying to import a `Student` model from `quiz.models` that didn't exist.

**Workaround**: Created the `Student` model in `academic_integration/models.py` and updated import statements in `views.py` to reference this model.

```python
# backend_quiz/academic_integration/models.py
from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    course_ids = models.JSONField(default=list)  # List of course IDs the student is enrolled in

    def __str__(self):
        return f"{self.student_id} - {self.user.username}"
```

### Missing Analytics Functions

**Issue**: The `staffController.js` file was missing implementation for several analytics functions referenced in routes.

**Workaround**: Added the missing functions to enable proper functionality.

```javascript
// controllers/staffController.js
exports.getCourseAnalytics = async (req, res) => {
  try {
    const { courseId } = req.query;
    
    if (!courseId) {
      return res.status(400).json({ message: 'Course ID is required' });
    }

    // Get all performance records for this course
    const performances = await Performance.find({ courseId });
    
    if (!performances || performances.length === 0) {
      return res.status(404).json({ message: 'No performance data found for this course' });
    }

    // Calculate statistics
    let totalStudents = new Set();
    let assessmentTypes = {};
    let totalScores = 0;
    let totalMaxScores = 0;
    
    performances.forEach(perf => {
      totalStudents.add(perf.studentId);
      
      // Group by assessment type
      if (!assessmentTypes[perf.assessmentType]) {
        assessmentTypes[perf.assessmentType] = {
          count: 0,
          totalScore: 0,
          totalMaxScore: 0
        };
      }
      
      assessmentTypes[perf.assessmentType].count++;
      assessmentTypes[perf.assessmentType].totalScore += perf.score;
      assessmentTypes[perf.assessmentType].totalMaxScore += perf.maxScore;
      
      totalScores += perf.score;
      totalMaxScores += perf.maxScore;
    });
    
    // Calculate averages
    const courseAverage = (totalMaxScores > 0) ? (totalScores / totalMaxScores * 100).toFixed(2) : 0;
    
    // Process assessment type statistics
    Object.keys(assessmentTypes).forEach(type => {
      const data = assessmentTypes[type];
      data.average = (data.totalMaxScore > 0) 
        ? (data.totalScore / data.totalMaxScore * 100).toFixed(2) 
        : 0;
    });
    
    // Return analytics data
    res.json({
      courseId,
      studentCount: totalStudents.size,
      assessmentCount: performances.length,
      courseAverage,
      assessmentBreakdown: assessmentTypes
    });
  } catch (error) {
    console.error('Error getting course analytics:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};
```

### CORS Issues Between Django and Node.js Applications

**Issue**: Cross-Origin Resource Sharing (CORS) issues when making requests between the two applications.

**Workaround**: Configured CORS in both applications:

```python
# Django CORS configuration in settings.py
INSTALLED_APPS = [
    # ...
    'corsheaders',
    # ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]

CORS_ALLOW_ALL_ORIGINS = True  # In development
# For production, use:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5000",
#     "https://analyzer.example.com",
# ]
```

```javascript
// Node.js CORS configuration in server.js
const cors = require('cors');
app.use(cors({
  origin: ['http://localhost:8000', 'https://classroom.example.com']
}));
```

## Future Implementation Roadmap

1. **Authentication Enhancements**
   - Implement JWT-based authentication between Django and Node.js
   - Add OAuth2 support for third-party login
   - Implement role-based access control

2. **Mobile Experience**
   - Develop responsive UI for mobile devices
   - Create Progressive Web App (PWA) version
   - Implement offline quiz taking capability

3. **Analytics Enhancements**
   - Add predictive analytics for student performance
   - Implement ML-based recommendations for struggling students
   - Create more detailed visualization dashboards

4. **Quiz Feature Enhancements**
   - Add support for multimedia questions (images, audio, video)
   - Implement timed sections within quizzes
   - Add question banks and randomized question selection

5. **Integration Enhancements**
   - Connect with Learning Management Systems via LTI
   - Implement integration with calendar systems
   - Add notification system for upcoming quizzes and deadlines

6. **Performance Optimizations**
   - Implement caching for frequently accessed data
   - Optimize database queries and indexing
   - Add load balancing for high-traffic instances