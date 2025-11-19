const mongoose = require('mongoose');

const ArchivedCourseSchema = new mongoose.Schema({
    // Original course data
    courseId: { type: String, required: true, unique: true },
    courseName: { type: String, required: true },
    courseCode: { type: String, required: true },
    batch: { type: String, required: true },
    
    // Teacher who handled the course
    teacherId: { type: mongoose.Schema.Types.ObjectId, ref: 'Teacher', required: true },
    teacherEmail: { type: String, required: true },
    
    // Students who were enrolled
    enrolledStudents: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Student' }],
    
    // Archive metadata
    archivedAt: { type: Date, default: Date.now },
    archivedBy: { type: String, required: true }, // Email of staff who archived
    
    // Original creation date
    originalCreatedAt: { type: Date },
    
    // Store performance data snapshot at time of archiving
    performanceSnapshot: [{
        studentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Student' },
        marks: {
            tutorial1: { type: Number, default: 0 },
            tutorial2: { type: Number, default: 0 },
            tutorial3: { type: Number, default: 0 },
            tutorial4: { type: Number, default: 0 },
            CA1: { type: Number, default: 0 },
            CA2: { type: Number, default: 0 },
            assignmentPresentation: { type: Number, default: 0 }
        },
        totalMarks: { type: Number, default: 0 }
    }]
}, { timestamps: true });

module.exports = mongoose.model('ArchivedCourse', ArchivedCourseSchema);
