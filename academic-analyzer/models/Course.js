// academic-analyzer/models/Course.js
const mongoose = require('mongoose');

const courseSchema = mongoose.Schema({
    batch: { 
        type: String, 
        required: true 
    },
    courseName: { 
        type: String, 
        required: true 
    },
    courseCode: { 
        type: String, 
        required: true 
    },
    // Custom course ID (e.g., 'CS101-24MXG1'), useful for lookups
    courseId: { 
        type: String, 
        required: true, 
        unique: true 
    }, 
    // Roster of students
    enrolledStudents: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Student',
    }],
    // Assigned teachers (can be more than one)
    assignedTeachers: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Teacher',
    }]
}, {
    timestamps: true,
});

const Course = mongoose.model('Course', courseSchema);
module.exports = Course;