// academic-analyzer/routes/studentRoutes.js
const express = require('express');
const router = express.Router();
// Import the controller logic
const student = require('../controllers/studentController'); 

// Authentication & Dashboard
router.post('/auth', student.studentAuth);
router.get('/dashboard', student.getStudentDashboard);
router.get('/course-detail', student.getCourseDetail);
router.get('/course-marks', student.getCourseMarks);

// Profile Management
router.get('/profile', student.getStudentProfile);
router.post('/update-profile', student.updateStudentProfile);

module.exports = router;