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

module.exports = router;