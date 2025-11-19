// academic-analyzer/routes/staffRoutes.js
const express = require('express');
const router = express.Router();
// Import the controller logic
const staff = require('../controllers/staffController'); 

// --- Authentication & Dashboard ---
router.post('/auth', staff.staffAuth);
router.get('/dashboard', staff.getStaffDashboard);
router.get('/course-detail', staff.getCourseRoster); 

// --- Course Management ---
router.post('/create-course', staff.createCourse);
router.post('/add-batch-to-course', staff.addBatchToCourse);
router.post('/add-students-csv', staff.addStudentsFromCSV);

// --- Student Management ---
router.post('/add-student', staff.addStudentToCourse);
router.post('/remove-student', staff.removeStudentFromCourse);
router.post('/delete-student', staff.deleteStudentFromCourse);
router.post('/student-detail', staff.getStudentPerformanceDetail);
router.get('/student-detail', staff.getStudentDetail);
router.get('/all-students', staff.getAllStudents);
router.get('/all-batches', staff.getAllBatches);
router.post('/create-student', staff.createStudent);
router.post('/create-students-csv', staff.createStudentsFromCSV);

// --- Mark Entry  Endpoints (Support single or bulk input) ---
router.post('/add-tut1-mark', staff.addTut1Mark);
router.post('/add-tut2-mark', staff.addTut2Mark);
router.post('/add-tut3-mark', staff.addTut3Mark);
router.post('/add-tut4-mark', staff.addTut4Mark);
router.post('/add-ca1-mark', staff.addCA1Mark);
router.post('/add-ca2-mark', staff.addCA2Mark);
router.post('/add-assignment-mark', staff.addAssignmentMark);

// --- Analytics & Performance Endpoints ---
router.get('/course-analytics', staff.getCourseAnalytics);
router.get('/student-performance', staff.getStudentPerformance);
router.post('/update-student-marks', staff.updateStudentMarks);

// --- Archive Management ---
router.post('/archive-course', staff.archiveCourse);
router.post('/restore-course', staff.restoreCourse);
router.get('/archived-courses', staff.getArchivedCourses);
router.get('/archived-course-detail', staff.getArchivedCourseDetail);

module.exports = router;