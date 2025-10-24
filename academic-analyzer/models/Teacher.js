// academic-analyzer/models/Teacher.js
const mongoose = require('mongoose');

const teacherSchema = mongoose.Schema({
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
    // References to courses the teacher is assigned to handle
    coursesHandled: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Course',
    }],
}, {
    timestamps: true,
});

const Teacher = mongoose.model('Teacher', teacherSchema);
module.exports = Teacher;