# Academic Analyzer Backend API Documentation

This API serves as the centralized academic records system for managing student and staff data, course enrollment, and detailed internal performance tracking.

## Tech Stack
- **Node.js**
- **Express.js**
- **MongoDB (Mongoose)**

---

## I. Data Model Schemas

### 1. Student Schema
| Field           | Type     | Description                          | Constraints         |
|-----------------|----------|--------------------------------------|---------------------|
| `name`          | String   | Student's full name.                | Required            |
| `rollno`        | String   | Unique university roll number.      | Required, Unique    |
| `batch`         | String   | Academic batch (e.g., '24MXG1').    | Required            |
| `email`         | String   | Student's email address.            | Required, Unique    |
| `password`      | String   | Student's account password.         | Required            |
| `enrolledCourses` | [ObjectId] | List of references to Course documents. |                     |

### 2. Teacher Schema
| Field           | Type     | Description                          | Constraints         |
|-----------------|----------|--------------------------------------|---------------------|
| `name`          | String   | Teacher's full name.                | Required            |
| `email`         | String   | Teacher's professional email.       | Required, Unique    |
| `password`      | String   | Teacher's account password.         | Required            |
| `coursesHandled` | [ObjectId] | List of references to Course documents. |                     |

### 3. Course Schema
| Field           | Type     | Description                          | Constraints         |
|-----------------|----------|--------------------------------------|---------------------|
| `batch`         | String   | The batch this course is offered to.| Required            |
| `courseName`    | String   | Full name of the course.            | Required            |
| `courseCode`    | String   | Short course code (e.g., 'CS101').  | Required            |
| `courseId`      | String   | Unique ID (courseCode + batch).     | Required, Unique    |
| `enrolledStudents` | [ObjectId] | Roster of references to Student documents. |                     |
| `assignedTeachers` | [ObjectId] | List of references to Teacher documents. |                     |

### 4. Performance Schema
| Field           | Type     | Description                          | Default             |
|-----------------|----------|--------------------------------------|---------------------|
| `studentId`     | ObjectId | Reference to the Student record.    | Required            |
| `courseId`      | ObjectId | Reference to the Course record.     | Required            |
| `marks.tutorial[1-4]` | Number   | Marks for Tutorial 1 through 4.     | 0                   |
| `marks.CA[1-2]` | Number   | Marks for Continuous Assessment 1 and 2. | 0                   |
| `marks.assignmentPresentation` | Number | Mark for the assignment/package. | 0                   |

---

## II. API Endpoints

### 1. Student Routes (`/student/`)

#### Authentication & Dashboard
- **POST `/auth`**: Authenticate a student.
  - **Input**: `rollno`, `password`
  - **Output**: `{ success: true, studentId, rollno }`

- **GET `/dashboard`**: Retrieve all enrolled courses for a student.
  - **Input**: Query parameter `rollno`
  - **Output**: List of enrolled courses with details.

- **GET `/course-detail`**: Retrieve performance details for a specific course.
  - **Input**: Query parameters `courseId`, `rollno`
  - **Output**: Student name, course name, and marks object.

### 2. Staff Routes (`/staff/`)

#### Authentication & General View
- **POST `/auth`**: Authenticate a teacher.
  - **Input**: `email`, `password`
  - **Output**: `{ success: true, teacherId, email }`

- **GET `/dashboard`**: Retrieve courses handled by the teacher.
  - **Input**: Query parameter `email`
  - **Output**: List of courses handled by the teacher.

- **GET `/course-detail`**: Retrieve the roster of students enrolled in a course.
  - **Input**: Query parameter `courseId`
  - **Output**: List of enrolled students (name, rollno, email).

#### Student & Roster Management
- **POST `/add-student`**: Enroll a student in a course.
  - **Input**: `teacherEmail`, `courseId`, `studentEmail`

- **POST `/delete-student`**: Remove a student from a course.
  - **Input**: `teacherEmail`, `courseId`, `studentEmail`

- **POST `/student-detail`**: Retrieve detailed marks for a specific student in a course.
  - **Input**: `teacherEmail`, `studentEmail`, `courseId`

#### Mark Entry Endpoints
- **POST `/add-tut1-mark` to `/add-assignment-mark`**: Update marks for tutorials, continuous assessments, or assignments.
  - **Input**:
    ```json
    {
      "teacherEmail": "tutor@example.com",
      "courseId": "CS101-24MXG1",
      "studentInput": [
        { "email": "student1@example.com", "mark": 9 },
        { "email": "student2@example.com", "mark": 7 }
      ]
    }
    ```

---

## III. Configuration

### Database Connection
- **Environment Variables**:
  - `MONGO_URI`: MongoDB connection string.
  - `DB_USERNAME`, `DB_PASSWORD`, `DB_CLUSTER_URL`, `DB_NAME`: Used to construct `MONGO_URI` if not provided.

### Dependencies
- **Production**:
  - `dotenv`: Manage environment variables.
  - `express`: Web framework.
  - `mongoose`: MongoDB object modeling.
- **Development**:
  - `nodemon`: Automatic server restarts during development.

---

## IV. Notes
- **Authentication**: Passwords are stored as plain text. Consider using `bcrypt` for hashing in production.
- **Error Handling**: Ensure robust error handling for all endpoints.

---

## V. Future Enhancements
- Add external marks to the `Performance` schema.
- Implement role-based access control (RBAC) for better security.
- Add unit tests for all endpoints.