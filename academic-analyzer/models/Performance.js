// academic-analyzer/models/Performance.js
const mongoose = require('mongoose');

const performanceSchema = mongoose.Schema({
    // Link to the specific student
    studentId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'Student', 
    },
    // Link to the specific course
    courseId: {
        type: mongoose.Schema.Types.ObjectId,
        required: true,
        ref: 'Course', 
    },
    // Detailed internal assessment marks
    marks: {
        tutorial1: { type: Number, default: 0 },
        tutorial2: { type: Number, default: 0 },
        tutorial3: { type: Number, default: 0 },
        tutorial4: { type: Number, default: 0 },
        CA1: { type: Number, default: 0 },
        CA2: { type: Number, default: 0 },
        assignmentPresentation: { type: Number, default: 0 },
        // Future addition: externalMark: { type: Number, default: 0 },
    }
}, {
    timestamps: true,
});

// To ensure a student can only have ONE performance record per course
performanceSchema.index({ studentId: 1, courseId: 1 }, { unique: true });

const Performance = mongoose.model('Performance', performanceSchema);
module.exports = Performance;