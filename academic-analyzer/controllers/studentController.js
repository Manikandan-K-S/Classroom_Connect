// academic-analyzer/controllers/studentController.js
const Student = require('../models/Student');
const Course = require('../models/Course');
const Performance = require('../models/Performance');

// @route POST /student/auth
// @desc Authenticate student
exports.studentAuth = async (req, res) => {
    const { rollno, password } = req.body;
    try {
        const student = await Student.findOne({ rollno });
        // NOTE: Simple password check. In a real app, use bcrypt for security!
        if (student && student.password === password) {
            // Returning student details (rollno/ID) upon successful authentication
            res.json({ success: true, message: 'Authentication successful', studentId: student._id, rollno: student.rollno });
        } else {
            res.status(401).json({ success: false, message: 'Invalid Roll No or Password' });
        } 
    } catch (error) {
        console.error('Auth Error:', error);
        res.status(500).json({ success: false, message: 'Server error during authentication' });
    }
};

// @route GET /student/dashboard
// @desc Get all enrolled courses for a student
exports.getStudentDashboard = async (req, res) => {
    // Uses query parameter for GET requests
    const { rollno } = req.query; 
    try {
        // Find student and populate the courses they are enrolled in
        const student = await Student.findOne({ rollno }).populate('enrolledCourses', 'courseName courseCode courseId batch');
        if (!student) {
            return res.status(404).json({ success: false, message: 'Student not found' });
        }
        // Returns the list of enrolled courses with details
        res.json({ success: true, name: student.name, courses: student.enrolledCourses });
    } catch (error) {
        console.error('Dashboard Error:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
};

// @route GET /student/course-detail
// @desc Get performance for a specific course
exports.getCourseDetail = async (req, res) => {
    const { courseId, rollno } = req.query;
    try {
        const student = await Student.findOne({ rollno });
        const course = await Course.findOne({ courseId });

        if (!student || !course) {
            return res.status(404).json({ success: false, message: 'Student or Course not found' });
        }
        
        // Find the performance document using the linked IDs
        const performance = await Performance.findOne({
            studentId: student._id,
            courseId: course._id,
        });

        // Structure the response clearly, handling cases where a performance record might be missing
        const responseData = {
            courseName: course.courseName,
            courseCode: course.courseCode,
            studentName: student.name,
            rollno: student.rollno,
            marks: performance ? performance.marks : {},
            message: performance ? 'Performance data retrieved.' : 'Performance record is empty or missing.'
        };

        res.json({ success: true, data: responseData });
    } catch (error) {
        console.error('Course Detail Error:', error);
        res.status(500).json({ success: false, message: 'Server error retrieving course details' });
    }
};

// @route GET /student/profile
// @desc Get student profile information
exports.getStudentProfile = async (req, res) => {
    const { rollno } = req.query;
    try {
        const student = await Student.findOne({ rollno });
        if (!student) {
            return res.status(404).json({ success: false, message: 'Student not found' });
        }
        
        // Return student profile data
        res.json({ 
            success: true, 
            student: {
                name: student.name,
                rollno: student.rollno,
                email: student.email,
                batch: student.batch,
                allow_name_edit: false, // Name changes require admin approval
                email_notifications: true // Default to true
            }
        });
    } catch (error) {
        console.error('Get Profile Error:', error);
        res.status(500).json({ success: false, message: 'Server error retrieving profile' });
    }
};

// @route POST /student/update-profile
// @desc Update student profile information
exports.updateStudentProfile = async (req, res) => {
    const { rollno, email, password } = req.body;
    
    try {
        const student = await Student.findOne({ rollno });
        if (!student) {
            return res.status(404).json({ success: false, message: 'Student not found' });
        }
        
        // Update allowed fields
        if (email && email !== student.email) {
            // Check if email is already in use by another student
            const existingStudent = await Student.findOne({ email, rollno: { $ne: rollno } });
            if (existingStudent) {
                return res.status(400).json({ success: false, message: 'Email is already in use by another student' });
            }
            student.email = email;
        }
        
        // Update password if provided
        // NOTE: In production, use bcrypt to hash passwords!
        if (password && password.trim() !== '') {
            student.password = password;
        }
        
        await student.save();
        
        res.json({ 
            success: true, 
            message: 'Profile updated successfully',
            student: {
                name: student.name,
                rollno: student.rollno,
                email: student.email,
                batch: student.batch
            }
        });
    } catch (error) {
        console.error('Update Profile Error:', error);
        res.status(500).json({ success: false, message: 'Server error updating profile' });
    }
};

// @route GET /student/course-marks
// @desc Get detailed marks with components for a specific course
exports.getCourseMarks = async (req, res) => {
    const { courseId, rollno } = req.query;
    try {
        const student = await Student.findOne({ rollno });
        const course = await Course.findOne({ courseId });

        if (!student || !course) {
            return res.status(404).json({ success: false, message: 'Student or Course not found' });
        }
        
        // Find the performance document using the linked IDs
        const performance = await Performance.findOne({
            studentId: student._id,
            courseId: course._id,
        }).populate('studentId', 'name rollno')
          .populate('courseId', 'courseName courseCode courseId');

        if (!performance) {
            return res.json({ 
                success: true, 
                marks: {}, 
                components: [],
                overallPercentage: 0,
                message: 'No performance record found for this student in this course.'
            });
        }

        // Define component weights and details
        const componentDefinitions = [
            { name: 'Tutorial 1', type: 'tutorial', field: 'tutorial1', maxScore: 10, weight: 10 },
            { name: 'Tutorial 2', type: 'tutorial', field: 'tutorial2', maxScore: 10, weight: 10 },
            { name: 'Tutorial 3', type: 'tutorial', field: 'tutorial3', maxScore: 10, weight: 10 },
            { name: 'Tutorial 4', type: 'tutorial', field: 'tutorial4', maxScore: 10, weight: 10 },
            { name: 'Continuous Assessment 1', type: 'exam', field: 'CA1', maxScore: 50, weight: 20 },
            { name: 'Continuous Assessment 2', type: 'exam', field: 'CA2', maxScore: 50, weight: 20 },
            { name: 'Assignment/Presentation', type: 'assignment', field: 'assignmentPresentation', maxScore: 20, weight: 20 }
        ];

        // Process each component with score and percentage
        const components = componentDefinitions.map(component => {
            const score = performance.marks[component.field] || 0;
            const percentage = (score / component.maxScore) * 100;
            
            return {
                name: component.name,
                type: component.type,
                score: score,
                maxScore: component.maxScore,
                percentage: percentage,
                weight: component.weight
            };
        });

        // Calculate overall percentage
        let totalWeightedScore = 0;
        let totalWeight = 0;

        components.forEach(component => {
            totalWeightedScore += (component.percentage * component.weight);
            totalWeight += component.weight;
        });

        const overallPercentage = totalWeight > 0 ? totalWeightedScore / totalWeight : 0;

        res.json({ 
            success: true,
            studentName: performance.studentId.name,
            studentRollno: performance.studentId.rollno,
            courseName: performance.courseId.courseName,
            courseCode: performance.courseId.courseCode,
            courseId: performance.courseId.courseId,
            marks: performance.marks,
            components: components,
            overallPercentage: overallPercentage,
            message: 'Performance data retrieved.'
        });
    } catch (error) {
        console.error('Course Marks Detail Error:', error);
        res.status(500).json({ success: false, message: 'Server error retrieving course marks details' });
    }
};