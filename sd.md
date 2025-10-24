# Comprehensive System Design: Academic Analyzer & Classroom Connect

## 1. System Overview

The system consists of two main applications that work together to provide a comprehensive educational management platform:

1. **Academic Analyzer** - A Node.js/Express.js API backend for managing academic data, performance tracking, and analytics
2. **Classroom Connect** - A Django-based web application with a quiz system that integrates with Academic Analyzer

### Integration Architecture Diagram

```
┌───────────────────────┐           ┌──────────────────────────┐
│                       │           │                          │
│   Classroom Connect   │◄─────────►│    Academic Analyzer     │
│   (Django Web App)    │    API    │    (Node.js/Express)     │
│                       │   Calls   │                          │
└───────────┬───────────┘           └──────────────┬───────────┘
            │                                      │
            │                                      │
      ┌─────▼──────┐                        ┌──────▼─────┐
      │            │                        │            │
      │  SQLite/   │                        │  MongoDB   │
      │ PostgreSQL │                        │   Atlas    │
      │            │                        │            │
      └────────────┘                        └────────────┘
```

The applications use a REST API-based integration pattern where Classroom Connect calls Academic Analyzer APIs to retrieve and manipulate academic data. This allows each system to focus on its core functionality while still providing a unified experience for users.

## 2. Academic Analyzer (Node.js/Express.js)

### 2.1 Technology Stack
- **Backend**: Node.js with Express.js
- **Database**: MongoDB (cloud-based via MongoDB Atlas)
- **Authentication**: Basic authentication (email/password)
- **Middleware**: Express middleware for request processing, error handling, and logging
- **API Documentation**: Documented in API_DOCUMENTATION.md

### 2.2 Project Structure

```
academic-analyzer/
├── config/
│   └── db.js             # MongoDB connection configuration
├── controllers/
│   ├── staffController.js # Staff-related API logic
│   └── studentController.js # Student-related API logic
├── models/
│   ├── Course.js          # Course data model
│   ├── Performance.js     # Student performance data model
│   ├── Student.js         # Student data model
│   └── Teacher.js         # Teacher data model
├── routes/
│   ├── staffRoutes.js     # Staff API endpoint definitions
│   └── studentRoutes.js   # Student API endpoint definitions
├── server.js              # Entry point, Express setup
├── package.json           # Dependencies and scripts
└── API_DOCUMENTATION.md   # API documentation
```

### 2.3 Database Schema

#### Teacher Model
```javascript
// models/Teacher.js
const mongoose = require('mongoose');

const TeacherSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  password: {
    type: String,
    required: true
  },
  department: {
    type: String,
    required: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Teacher', TeacherSchema);
```

#### Student Model
```javascript
// models/Student.js
const mongoose = require('mongoose');

const StudentSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  rollno: {
    type: String,
    required: true,
    unique: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  batch: {
    type: String,
    required: true
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Student', StudentSchema);
```

#### Course Model
```javascript
// models/Course.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const CourseSchema = new mongoose.Schema({
  courseId: {
    type: String,
    required: true,
    unique: true
  },
  courseName: {
    type: String,
    required: true
  },
  courseCode: {
    type: String,
    required: true
  },
  batch: {
    type: String,
    required: true
  },
  teacherId: {
    type: Schema.Types.ObjectId,
    ref: 'Teacher',
    required: true
  },
  enrolledStudents: [{
    type: Schema.Types.ObjectId,
    ref: 'Student'
  }],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Course', CourseSchema);
```

#### Performance Model
```javascript
// models/Performance.js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const PerformanceSchema = new mongoose.Schema({
  studentId: {
    type: Schema.Types.ObjectId,
    ref: 'Student',
    required: true
  },
  courseId: {
    type: Schema.Types.ObjectId,
    ref: 'Course',
    required: true
  },
  marks: {
    tutorial1: {
      type: Number,
      min: 0,
      max: 10,
      default: 0
    },
    tutorial2: {
      type: Number,
      min: 0,
      max: 10,
      default: 0
    },
    tutorial3: {
      type: Number,
      min: 0,
      max: 10,
      default: 0
    },
    tutorial4: {
      type: Number,
      min: 0,
      max: 10,
      default: 0
    },
    CA1: {
      type: Number,
      min: 0,
      max: 20,
      default: 0
    },
    CA2: {
      type: Number,
      min: 0,
      max: 20,
      default: 0
    },
    assignmentPresentation: {
      type: Number,
      min: 0,
      max: 15,
      default: 0
    }
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Unique index to ensure one performance record per student per course
PerformanceSchema.index({ studentId: 1, courseId: 1 }, { unique: true });

module.exports = mongoose.model('Performance', PerformanceSchema);
```

### 2.4 API Endpoints

#### Route Configuration
```javascript
// routes/staffRoutes.js
const express = require('express');
const router = express.Router();
const staff = require('../controllers/staffController');

// Authentication & Dashboard
router.post('/auth', staff.staffAuth);
router.get('/dashboard', staff.getStaffDashboard);
router.get('/course-detail', staff.getCourseRoster);

// Course Management
router.post('/create-course', staff.createCourse);
router.post('/add-batch-to-course', staff.addBatchToCourse);
router.post('/add-students-csv', staff.addStudentsFromCSV);

// Student Management
router.post('/add-student', staff.addStudentToCourse);
router.post('/delete-student', staff.deleteStudentFromCourse);
router.post('/student-detail', staff.getStudentPerformanceDetail);
router.post('/create-student', staff.createStudent);
router.post('/create-students-csv', staff.createStudentsFromCSV);

// Mark Entry Endpoints
router.post('/add-tut1-mark', staff.addTut1Mark);
router.post('/add-tut2-mark', staff.addTut2Mark);
router.post('/add-tut3-mark', staff.addTut3Mark);
router.post('/add-tut4-mark', staff.addTut4Mark);
router.post('/add-ca1-mark', staff.addCA1Mark);
router.post('/add-ca2-mark', staff.addCA2Mark);
router.post('/add-assignment-mark', staff.addAssignmentMark);

// Analytics Endpoints
router.get('/course-analytics', staff.getCourseAnalytics);
router.get('/student-performance', staff.getStudentPerformance);
router.post('/update-student-marks', staff.updateStudentMarks);

module.exports = router;
```

### 2.5 Business Logic Components

#### Analytics Implementation
```javascript
// Part of staffController.js
/**
 * @route GET /staff/course-analytics
 * @desc Get analytics data for a specific course
 * @input courseId (query param)
 * @returns Course analytics with performance metrics
 */
const getCourseAnalytics = async (req, res) => {
    const { courseId } = req.query;
    
    try {
        // Find the course
        const course = await Course.findOne({ courseId }).populate('enrolledStudents');
        if (!course) {
            return res.status(404).json({ success: false, message: 'Course not found' });
        }

        // Get all performances for this course
        const performances = await Performance.find({
            courseId: course._id
        }).populate('studentId', 'name rollno email');

        // Calculate overall statistics
        const overallStats = {
            avgScore: 0,
            tutorialCompletionRate: 0,
            assignmentCompletionRate: 0,
            gradeDistribution: {
                'A': 0, // 90-100%
                'B': 0, // 80-89%
                'C': 0, // 70-79%
                'D': 0, // 60-69%
                'F': 0, // <60%
            }
        };

        // Map for storing individual student performances
        const studentPerformances = {};
        
        // Process each performance record
        let totalInternalMarks = 0;
        let totalTutorialScore = 0;
        let totalCAScore = 0;
        let totalAssignmentScore = 0;
        let tutorialSubmissions = 0;
        let assignmentSubmissions = 0;
        
        performances.forEach(perf => {
            const studentRollno = perf.studentId.rollno;
            
            // Calculate tutorial score (average of tutorials 1-4, scaled to 15 marks)
            const tut1 = perf.marks.tutorial1 || 0;
            const tut2 = perf.marks.tutorial2 || 0;
            const tut3 = perf.marks.tutorial3 || 0;
            const tut4 = perf.marks.tutorial4 || 0;
            const tutAvg = (tut1 + tut2 + tut3 + tut4) / 4;
            const tutorialScore = tutAvg * 1.5; // Scale to 15 marks (assuming tutorials are out of 10)
            
            // Calculate CA score (average of CA1 & CA2)
            const ca1 = perf.marks.CA1 || 0;
            const ca2 = perf.marks.CA2 || 0;
            const caScore = (ca1 + ca2) / 2;
            
            // Calculate assignment score
            const assignmentScore = perf.marks.assignmentPresentation || 0;
            
            // Calculate internal marks (total of tutorial, CA, and assignment scores)
            const internalTotal = tutorialScore + caScore + assignmentScore;
            
            // Calculate final internal marks (scaled to 40)
            const finalInternal = (internalTotal / 50) * 40;
            
            // Determine grade
            let grade = 'F';
            if (finalInternal >= 36) grade = 'A';      // 90%+
            else if (finalInternal >= 32) grade = 'B'; // 80%+
            else if (finalInternal >= 28) grade = 'C'; // 70%+
            else if (finalInternal >= 24) grade = 'D'; // 60%+
            
            // Increment grade distribution
            overallStats.gradeDistribution[grade]++;
            
            // Track if tutorial/assignment were submitted
            if (tut1 > 0 || tut2 > 0 || tut3 > 0 || tut4 > 0) tutorialSubmissions++;
            if (assignmentScore > 0) assignmentSubmissions++;
            
            // Add to totals for averages
            totalInternalMarks += finalInternal;
            totalTutorialScore += tutorialScore;
            totalCAScore += caScore;
            totalAssignmentScore += assignmentScore;
            
            // Store student performance data
            studentPerformances[studentRollno] = {
                tutorial1_score: tut1,
                tutorial2_score: tut2,
                tutorial3_score: tut3,
                tutorial4_score: tut4,
                tutorial_average: tutAvg,
                tutorialScore: tutorialScore,
                ca1_original: ca1 * 2.5, // Convert from 20 scale to original 50 scale
                ca1_scaled: ca1,
                ca2_original: ca2 * 2.5, // Convert from 20 scale to original 50 scale
                ca2_scaled: ca2,
                caScore: caScore,
                assignment_score: assignmentScore > 10 ? assignmentScore - 10 : 0,
                presentation_score: assignmentScore > 10 ? 10 : assignmentScore,
                assignmentScore: assignmentScore,
                internalTotal: internalTotal,
                finalInternal: finalInternal,
                grade: grade
            };
        });
        
        // Calculate averages and rates
        const studentCount = performances.length > 0 ? performances.length : 1; // Avoid division by zero
        overallStats.avgScore = totalInternalMarks / studentCount;
        overallStats.tutorialCompletionRate = (tutorialSubmissions / studentCount) * 100;
        overallStats.assignmentCompletionRate = (assignmentSubmissions / studentCount) * 100;
        
        return res.json({
            success: true,
            courseName: course.courseName,
            batch: course.batch,
            studentCount: studentCount,
            overallStats,
            studentPerformances
        });
        
    } catch (error) {
        console.error('Course Analytics Error:', error);
        res.status(500).json({ success: false, message: 'Server error during analytics generation' });
    }
};
```

#### Mark Entry Implementation
```javascript
// Part of staffController.js
// Generic handler factory for all mark update operations
const createMarkUpdateHandler = (markField) => {
    return async (req, res) => {
        const { teacherEmail, courseId, studentId, mark } = req.body;

        try {
            // Find teacher (for authorization)
            const teacher = await Teacher.findOne({ email: teacherEmail });
            if (!teacher) {
                return res.status(404).json({ success: false, message: 'Teacher not found' });
            }

            // Find course
            const course = await Course.findOne({ courseId });
            if (!course) {
                return res.status(404).json({ success: false, message: 'Course not found' });
            }

            // Only allow if teacher owns course
            if (course.teacherId.toString() !== teacher._id.toString()) {
                return res.status(403).json({ 
                    success: false, 
                    message: 'Not authorized to update marks for this course' 
                });
            }

            // Find student
            const student = await Student.findOne({ rollno: studentId });
            if (!student) {
                return res.status(404).json({ success: false, message: 'Student not found' });
            }

            // Validate student is enrolled in course
            if (!course.enrolledStudents.includes(student._id)) {
                return res.status(400).json({
                    success: false,
                    message: 'Student is not enrolled in this course'
                });
            }

            // Find or create performance record
            let performance = await Performance.findOne({
                studentId: student._id,
                courseId: course._id
            });

            if (!performance) {
                // Create new performance record
                performance = new Performance({
                    studentId: student._id,
                    courseId: course._id,
                    marks: {}
                });
            }

            // Update the specific mark field
            performance.marks[markField] = mark;
            performance.updatedAt = Date.now();

            await performance.save();

            res.json({
                success: true,
                message: `${markField} updated successfully for ${student.name}`
            });

        } catch (error) {
            console.error(`Error updating ${markField}:`, error);
            res.status(500).json({ success: false, message: 'Server error updating mark' });
        }
    };
};

// Create handlers for each mark type
exports.addTut1Mark = createMarkUpdateHandler('tutorial1');
exports.addTut2Mark = createMarkUpdateHandler('tutorial2');
exports.addTut3Mark = createMarkUpdateHandler('tutorial3');
exports.addTut4Mark = createMarkUpdateHandler('tutorial4');
exports.addCA1Mark = createMarkUpdateHandler('CA1');
exports.addCA2Mark = createMarkUpdateHandler('CA2');
exports.addAssignmentMark = createMarkUpdateHandler('assignmentPresentation');
```

#### Server Configuration
```javascript
// server.js
const express = require('express');
const dotenv = require('dotenv');
const connectDB = require('./config/db');

// Load environment variables
dotenv.config();

// Connect to database
connectDB();

const app = express();

// Middleware to parse JSON bodies
app.use(express.json());

// CORS middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  if (req.method === 'OPTIONS') {
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    return res.status(200).json({});
  }
  next();
});

// Define Routes
const studentRoutes = require('./routes/studentRoutes');
const staffRoutes = require('./routes/staffRoutes');

// Mount Routes
app.use('/student', studentRoutes);
app.use('/staff', staffRoutes);

// Simple welcome route
app.get('/', (req, res) => {
    res.send('Academic Analyzer API is running...');
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => console.log(`Server running on port ${PORT} in ${process.env.NODE_ENV || 'development'} mode 🌟`));
```

## 3. Classroom Connect (Django)

### 3.1 Technology Stack
- **Backend**: Python with Django
- **Frontend**: HTML, CSS, Bootstrap, JavaScript, Chart.js
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Django authentication system
- **Real-time**: Django Channels for WebSockets (quiz functionality)
- **Third-party Integration**: Requests library for API calls

### 3.2 Project Structure

```
classroom_connect/
├── requirements.txt
├── backend_quiz/
│   ├── manage.py
│   ├── academic_integration/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── academic_integration/
│   │   │       ├── base.html
│   │   │       ├── staff_dashboard.html
│   │   │       ├── manage_course.html
│   │   │       └── ...
│   ├── backend_quiz/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── quiz/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── consumers.py
│       ├── models.py
│       ├── routing.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       ├── views.py
│       ├── migrations/
│       └── templates/
│           └── quiz/
│               ├── admin_dashboard.html
│               ├── create_quiz.html
│               ├── quiz_detail.html
│               └── ...
```

### 3.3 Database Models

#### User Model (extends Django AbstractUser)
```python
# quiz/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Fix related_name conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='quiz_user_set',
        related_query_name='quiz_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='quiz_user_set',
        related_query_name='quiz_user',
    )
    
    def is_student(self):
        return self.role == 'student'
    
    def is_admin(self):
        return self.role == 'admin'
```

#### Student Model (academic_integration)
```python
# academic_integration/models.py
from django.db import models
from quiz.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, blank=True, null=True)  # Academic analyzer ID
    
    def __str__(self):
        return self.user.username or self.student_id
```

#### Quiz and Related Models
```python
# quiz/models.py (continued)
class Quiz(models.Model):
    """
    Represents a quiz that can be assigned to courses from Academic Analyzer
    """
    QUIZ_TYPES = [
        ('tutorial', 'Tutorial Quiz'),
        ('mock', 'Mock Test'),
        ('exam', 'Examination'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Optional description of the quiz")
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, blank=True, help_text="Start date and time of the quiz")
    complete_by_date = models.DateTimeField(null=True, blank=True, help_text="Optional deadline for quiz completion")
    course_id = models.CharField(max_length=100, null=True, blank=True, help_text="Academic Analyzer Course ID")
    tutorial_number = models.IntegerField(null=True, blank=True, help_text="Tutorial number (1-4) in Academic Analyzer")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_quizzes", null=True, blank=True)
    quiz_type = models.CharField(max_length=10, choices=QUIZ_TYPES, default='tutorial')
    duration_minutes = models.IntegerField(default=30, help_text="Duration of the quiz in minutes")
    is_active = models.BooleanField(default=True, help_text="Whether the quiz is currently active")
    show_results = models.BooleanField(default=True, help_text="Whether to show results immediately after submission")
    allow_review = models.BooleanField(default=True, help_text="Whether students can review their answers after completion")
    is_ended = models.BooleanField(default=False, help_text="Whether the quiz has been ended by the teacher")
    
    @property
    def is_mock_test(self):
        return self.quiz_type == 'mock' or not self.tutorial_number
        
    @property
    def is_available(self):
        """Check if the quiz is available to take based on dates and active status"""
        now = timezone.now()
        # If quiz has been manually ended by teacher
        if self.is_ended:
            return False
        # If quiz is not active
        if not self.is_active:
            return False
        # If start date is set and it's in the future
        if self.start_date and now < self.start_date:
            return False
        # If deadline is set and it's in the past
        if self.complete_by_date and now > self.complete_by_date:
            return False
        return True

class Question(models.Model):
    """
    Represents a question in a quiz
    """
    QUESTION_TYPES = [
        ('mcq_single', 'Multiple Choice (Single Answer)'),
        ('mcq_multiple', 'Multiple Choice (Multiple Answers)'),
        ('text', 'Text Input'),
        ('true_false', 'True or False'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq_single')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Choice(models.Model):
    """
    Represents an answer choice for a question
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class QuizAttempt(models.Model):
    """
    Records a student's attempt at a quiz
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    feedback = models.TextField(blank=True, null=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="graded_attempts", null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'quiz']  # One attempt per user per quiz
```

### 3.4 API Integration Layer

```python
# academic_integration/views.py (utility functions)
import logging
import json
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def _api_base_url() -> str:
    """
    Get the base URL for the Academic Analyzer API from settings
    with improved error handling and logging.
    """
    base_url = getattr(settings, "ACADEMIC_ANALYZER_BASE_URL", None)
    
    if not base_url:
        # Log a warning if no URL is configured
        logger.warning("ACADEMIC_ANALYZER_BASE_URL not configured in settings, using default")
        base_url = "http://localhost:5000"
    
    # Log the API base URL being used
    logger.debug(f"Using Academic Analyzer API base URL: {base_url}")
    return base_url.rstrip("/")


def _safe_json(response: requests.Response) -> dict:
    """
    Safely parse JSON from API response with enhanced error handling.
    """
    try:
        result = response.json()
        # Log response status for debugging
        if not response.ok or not result.get("success", False):
            logger.warning(f"API request failed: Status {response.status_code}, "
                        f"Response: {result.get('message', 'No message')}")
        return result
    except ValueError:
        logger.error(f"Failed to parse JSON from Academic Analyzer response (Status: {response.status_code}). "
                    f"Content: {response.text[:200]}...", exc_info=True)
        return {"success": False, "message": "Invalid API response"}
```

### 3.5 Key Views

#### Staff Dashboard View
```python
# academic_integration/views.py
def staff_dashboard(request):
    """
    Main dashboard view for staff members
    """
    staff_email = request.session.get("staff_email")
    if not staff_email:
        messages.info(request, "Please log in to continue.")
        return redirect("academic_integration:staff_login")
    
    # Get courses taught by this staff
    courses = []
    api_error = None
    
    try:
        response = requests.get(
            f"{_api_base_url()}/staff/dashboard",
            params={"teacherEmail": staff_email},
            timeout=5
        )
    except requests.RequestException:
        logger.exception("Failed to connect to Academic Analyzer API")
        api_error = "Could not connect to Academic Analyzer. Please try again later."
    else:
        body = _safe_json(response)
        if response.ok and body.get("success"):
            courses = body.get("courses", [])
        else:
            api_error = body.get("message", "Failed to load dashboard data")
    
    context = {
        "staff_email": staff_email,
        "staff_name": request.session.get("staff_name", ""),
        "courses": courses,
        "api_error": api_error
    }
    
    return render(request, "academic_integration/staff_dashboard.html", context)
```

#### Course Management View
```python
# academic_integration/views.py
def manage_course(request, course_id):
    """
    View for staff to manage a specific course - view roster, add students, analytics, etc.
    """
    staff_email = request.session.get("staff_email")
    if not staff_email:
        messages.info(request, "Please log in to continue.")
        return redirect("academic_integration:staff_login")

    # Get course details
    api_error = None
    course = {}
    students = []

    try:
        response = requests.get(
            f"{_api_base_url()}/staff/course-detail",
            params={"courseId": course_id},
            timeout=5,
        )
    except requests.RequestException:
        logger.exception("Failed to load course details")
        api_error = "Could not reach Academic Analyzer API. Please try again later."
    else:
        body = _safe_json(response)
        if response.ok and body.get("success"):
            course = {
                "id": course_id, 
                "courseId": course_id,
                "name": body.get("courseName", "Unknown Course"),
                "courseName": body.get("courseName", "Unknown Course"),
                "courseCode": body.get("courseCode", ""),
                "batch": body.get("batch", "")
            }
            students = body.get("students", [])
        else:
            api_error = body.get("message", "Failed to load course details.")

    # Forms for adding students
    single_student_form = StudentAddForm()
    batch_form = BatchEnrollmentForm()
    csv_form = CSVUploadForm()
    
    # Process forms (code omitted for brevity)
    
    # Get analytics data
    overall_stats = {}
    if not api_error and students:
        try:
            response = requests.get(
                f"{_api_base_url()}/staff/course-analytics",
                params={"courseId": course_id},
                timeout=15,
            )
            if response.ok:
                data = _safe_json(response)
                if data.get("success"):
                    overall_stats = data.get("overallStats", {})
                    
                    # Process analytics data (code omitted for brevity)
                    
                    # Add detailed performance data to each student
                    student_performances = data.get("studentPerformances", {})
                    for student in students:
                        roll_number = student.get("rollno")
                        if roll_number in student_performances:
                            student.update(student_performances[roll_number])
        except requests.RequestException:
            logger.exception("Failed to load analytics data")
            api_error = api_error or "Could not load analytics data"
    
    context = {
        "staff_email": staff_email,
        "staff_name": request.session.get("staff_name", staff_email),
        "course": course,
        "students": students,
        "api_error": api_error,
        "single_student_form": single_student_form,
        "batch_form": batch_form,
        "csv_form": csv_form,
        "overall_stats": overall_stats,
        "tutorial_max_marks": 10,
    }
    return render(request, "academic_integration/manage_course.html", context)
```

### 3.6 Template Examples

#### Staff Dashboard Template
```html
<!-- academic_integration/templates/academic_integration/staff_dashboard.html -->
{% extends "academic_integration/base.html" %}

{% block title %}Staff Dashboard{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h1 class="h3 mb-0">
            {% if staff_name %}
                Welcome, {{ staff_name }}
            {% else %}
                Welcome
            {% endif %}
        </h1>
        <p class="text-muted mb-0">Academic Analyzer course overview</p>
    </div>
    <div class="text-end">
        {% if staff_email %}
            <span class="badge bg-light text-dark">{{ staff_email }}</span>
        {% endif %}
    </div>
</div>

{% if api_error %}
    <div class="alert alert-warning alert-dismissible fade show" role="alert">
        <div class="d-flex">
            <div class="me-3">
                <i class="bi bi-exclamation-triangle-fill fs-3"></i>
            </div>
            <div>
                <h5>Connection Issue</h5>
                <p>{{ api_error }}</p>
                <button type="button" class="btn btn-sm btn-warning" onclick="window.location.reload()">
                    <i class="bi bi-arrow-clockwise"></i> Refresh Page
                </button>
            </div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
{% endif %}

<!-- Quick Action Buttons -->
<div class="row mb-4">
    <div class="col-md-6 col-lg-3 mb-3">
        <a href="{% url 'academic_integration:create_course' %}" class="card h-100 text-decoration-none">
            <div class="card-body text-center">
                <i class="bi bi-journal-plus display-5 text-primary"></i>
                <h5 class="mt-3">Create Course</h5>
                <p class="text-muted">Create a new course for your students</p>
            </div>
        </a>
    </div>
    
    <div class="col-md-6 col-lg-3 mb-3">
        <a href="{% url 'academic_integration:manage_students' %}" class="card h-100 text-decoration-none">
            <div class="card-body text-center">
                <i class="bi bi-people display-5 text-success"></i>
                <h5 class="mt-3">Manage Students</h5>
                <p class="text-muted">Add or view student accounts</p>
            </div>
        </a>
    </div>
    
    <div class="col-md-6 col-lg-3 mb-3">
        <a href="{% url 'academic_integration:admin_quiz_dashboard' %}" class="card h-100 text-decoration-none">
            <div class="card-body text-center">
                <i class="bi bi-question-circle display-5 text-info"></i>
                <h5 class="mt-3">Manage Quizzes</h5>
                <p class="text-muted">Create and manage quizzes</p>
            </div>
        </a>
    </div>
    
    <!-- Analytics card removed - now integrated into course view -->
</div>

{% if courses %}
    <div class="card shadow-sm">
        <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <strong>Your Courses</strong>
            <a href="{% url 'academic_integration:create_course' %}" class="btn btn-sm btn-primary">
                <i class="bi bi-plus-circle"></i> New Course
            </a>
        </div>
        <div class="table-responsive">
            <table class="table mb-0 align-middle">
                <thead>
                    <tr>
                        <th scope="col">Course</th>
                        <th scope="col">Course Code</th>
                        <th scope="col">Batch</th>
                        <th scope="col">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for course in courses %}
                        <tr>
                            <td>{{ course.courseName }}</td>
                            <td>{{ course.courseCode|default:"-" }}</td>
                            <td>{{ course.batch }}</td>
                            <td>
                                <a href="{% url 'academic_integration:manage_course' course_id=course.courseId %}" class="btn btn-sm btn-outline-primary">
                                    <i class="bi bi-gear"></i> Manage
                                </a>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
{% else %}
    <div class="alert alert-info" role="alert">
        <i class="bi bi-info-circle"></i> No courses found for your account yet. 
        <a href="{% url 'academic_integration:create_course' %}" class="alert-link">Create your first course</a>
    </div>
{% endif %}
{% endblock %}
```

## 4. Integration Points and Data Flow

### 4.1 Authentication Flow

```
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│              │  Login   │              │  Auth    │              │
│    Staff     ├─────────►│  Classroom   ├─────────►│   Academic   │
│    User      │          │   Connect    │          │   Analyzer   │
│              │◄─────────┤              │◄─────────┤              │
└──────────────┘ Session  └──────────────┘  Token   └──────────────┘
```

1. Staff user logs into Classroom Connect using credentials
2. Classroom Connect sends authentication request to Academic Analyzer API
3. If authenticated, Academic Analyzer returns user information
4. Classroom Connect creates a session for the user
5. Staff session is maintained for subsequent requests

### 4.2 Course Analytics Flow

```
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│              │ Request  │              │  API     │              │
│    Course    │ Page     │  Classroom   │  Call    │   Academic   │
│   Management │◄─────────┤   Connect    ├─────────►│   Analyzer   │
│     View     │          │     View     │          │     API      │
│              ├─────────►│              │◄─────────┤              │
└──────────────┘ Render   └──────────────┘  Data    └──────────────┘
                           │              │
                           ▼              ▼
                    ┌─────────────┐  ┌─────────────┐
                    │  Course DB  │  │Performance DB│
                    └─────────────┘  └─────────────┘
```

1. User accesses course management page
2. Django view requests course details from Academic Analyzer API
3. Django view requests analytics data from Academic Analyzer API
4. Academic Analyzer processes data from its database
5. Data is returned to Classroom Connect
6. Django view renders the data in the course management template

### 4.3 Quiz Integration Flow

```
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│              │ Create   │              │          │              │
│    Staff     ├─────────►│    Quiz      │          │   Course     │
│    User      │          │   System     │          │  Analytics   │
│              │          │              │          │              │
└──────────────┘          └──────┬───────┘          └──────┬───────┘
                                 │                         │
                                 │     Link Quiz           │
                                 │     to Course           │
                                 ├─────────────────────────┤
                                 │                         │
                           ┌─────▼─────┐          ┌────────▼───┐
                           │            │  Take    │            │
                           │ Student    │◄─────────┤  Quiz      │
                           │ Dashboard  │  Results │  Results   │
                           │            ├─────────►│            │
                           └────────────┘          └────────────┘
```

1. Staff creates quizzes in Classroom Connect
2. Quizzes are linked to Academic Analyzer courses
3. Quiz results feed into analytics in the course view

## 5. Security Considerations

### 5.1 Authentication and Authorization
- Django session-based authentication for web interface
- Basic authentication for Academic Analyzer API
- Role-based access control (student vs. staff/admin)

### 5.2 API Security
```javascript
// Example middleware for API protection (Node.js)
const authMiddleware = (req, res, next) => {
  // Extract credentials
  const authHeader = req.headers.authorization;
  
  if (!authHeader) {
    return res.status(401).json({ 
      success: false, 
      message: 'Authentication required' 
    });
  }
  
  // Check credentials (in production, use a more secure method)
  // ...
  
  next();
};

// Apply middleware to protected routes
app.use('/staff', authMiddleware);
```

### 5.3 Data Validation
```python
# Example form validation (Django)
class StudentAddForm(forms.Form):
    rollno = forms.CharField(
        label="Student Roll Number",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter student roll number'
        })
    )
    
    def clean_rollno(self):
        rollno = self.cleaned_data['rollno']
        # Validate format (e.g., 24MX101)
        if not re.match(r'^[0-9]{2}[A-Z]{2}[0-9]{3}$', rollno):
            raise forms.ValidationError("Invalid roll number format. Expected format: 24MX101")
        return rollno
```

## 6. Performance Considerations

### 6.1 Caching Strategy
```python
# Example caching in Django views
from django.core.cache import cache

def get_course_analytics(course_id, refresh=False):
    """Get course analytics with caching"""
    cache_key = f"course_analytics_{course_id}"
    
    # Return cached data if available and not refreshing
    if not refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
    
    # Fetch fresh data from API
    try:
        response = requests.get(
            f"{_api_base_url()}/staff/course-analytics",
            params={"courseId": course_id},
            timeout=15
        )
        if response.ok:
            data = _safe_json(response)
            if data.get("success"):
                # Cache the data for 10 minutes
                cache.set(cache_key, data, 60 * 10)
                return data
    except Exception as e:
        logger.exception(f"Error fetching analytics: {e}")
    
    return None
```

### 6.2 Database Indexing
```javascript
// Example indexing in MongoDB
const CourseSchema = new mongoose.Schema({
  // ... fields
});

// Index for faster lookups by courseId
CourseSchema.index({ courseId: 1 }, { unique: true });

// Compound index for teacher's courses
CourseSchema.index({ teacherId: 1, createdAt: -1 });

// Compound index for student enrollments
CourseSchema.index({ enrolledStudents: 1 });
```

## 7. Deployment Architecture

### 7.1 Development Environment
- Local Node.js server for Academic Analyzer API
- Local Django development server for Classroom Connect
- MongoDB Atlas for database (shared across environments)
- SQLite for Django local development

### 7.2 Production Environment

```
┌─────────────────────────────────────────────────────────┐
│                     Client Browser                      │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                      Nginx Proxy                        │
└───────────┬───────────────────────────────┬─────────────┘
            │                               │
┌───────────▼────────────┐     ┌────────────▼────────────┐
│    Gunicorn (Django)   │     │    Node.js (Express)    │
│  Classroom Connect App │     │   Academic Analyzer API │
└───────────┬────────────┘     └────────────┬────────────┘
            │                               │
┌───────────▼────────────┐     ┌────────────▼────────────┐
│        PostgreSQL      │     │      MongoDB Atlas      │
│        Database        │     │        Database         │
└────────────────────────┘     └─────────────────────────┘
```

### 7.3 Containerization (Future Recommendation)
```yaml
# Example docker-compose.yml for containerized deployment
version: '3'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./static:/static
    depends_on:
      - django
      - node

  django:
    build: ./classroom_connect
    command: gunicorn backend_quiz.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./classroom_connect:/app
      - ./static:/app/static
    environment:
      - DATABASE_URL=postgres://postgres:postgres@postgres:5432/classroom_connect
      - ACADEMIC_ANALYZER_BASE_URL=http://node:5000
    depends_on:
      - postgres

  node:
    build: ./academic-analyzer
    command: node server.js
    volumes:
      - ./academic-analyzer:/app
    environment:
      - PORT=5000
      - MONGO_URI=mongodb://mongo:27017/academic_analyzer
    depends_on:
      - mongo

  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=classroom_connect

  mongo:
    image: mongo:latest
    volumes:
      - mongo_data:/data/db

volumes:
  postgres_data:
  mongo_data:
```

## 8. Future Enhancement Opportunities

### 8.1 Technical Improvements
- Implement OAuth/JWT for more secure authentication
- Real-time updates using WebSockets for collaborative features
- Mobile-responsive design improvements
- API versioning for better backwards compatibility
- Comprehensive test suite for both applications

### 8.2 Feature Enhancements
- Advanced analytics with predictive modeling
- Personalized learning paths based on performance
- Integration with video conferencing for virtual office hours
- Automated grading for more question types
- Plagiarism detection for assignments
- Gamification elements to increase student engagement

## 9. Conclusion

The Academic Analyzer and Classroom Connect system provides a comprehensive solution for educational management, combining the strengths of Node.js/MongoDB for data processing and Django for user-friendly web interfaces. The integration between these systems allows for seamless course management, performance tracking, and quiz administration, providing educators with powerful tools to enhance the learning experience.

By separating concerns between the systems yet maintaining tight integration, the architecture allows for independent scaling and evolution of components while preserving a cohesive user experience. This design provides a solid foundation for future enhancements to meet evolving educational needs.