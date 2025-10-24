// academic-analyzer/models/Student.js
const mongoose = require('mongoose');

const studentSchema = mongoose.Schema({
    name: { 
        type: String, 
        required: true 
    },
    rollno: { 
        type: String, 
        required: true, 
        unique: true 
    },
    batch: { 
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
    // References to courses the student is enrolled in
    enrolledCourses: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Course',
    }],
}, {
    timestamps: true,
});

const Student = mongoose.model('Student', studentSchema);
module.exports = Student;