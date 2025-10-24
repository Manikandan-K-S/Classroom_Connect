/**
 * @route GET /staff/all-students
 * @desc Get all students in the system for a staff member
 * @input email (query param)
 * @returns List of all students in the system
 */
exports.getAllStudents = async (req, res) => {
    const { email } = req.query;
    
    try {
        // Verify the staff member exists
        const teacher = await Teacher.findOne({ email });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        // Get all students in the system
        const students = await Student.find({}).select('name rollno batch email');
        
        return res.json({
            success: true,
            students: students.map(student => ({
                name: student.name,
                rollno: student.rollno,
                batch: student.batch,
                email: student.email
            }))
        });
    } catch (error) {
        console.error('Error fetching all students:', error);
        return res.status(500).json({ success: false, message: 'Server error' });
    }
};

/**
 * @route GET /staff/student-detail
 * @desc Get detailed information about a specific student
 * @input email (staff email), rollno (student roll number) as query params
 * @returns Student details and enrolled courses
 */
exports.getStudentDetail = async (req, res) => {
    const { email, rollno } = req.query;
    
    try {
        // Verify the staff member exists
        const teacher = await Teacher.findOne({ email });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        // Get the student
        const student = await Student.findOne({ rollno });
        if (!student) {
            return res.status(404).json({ success: false, message: 'Student not found' });
        }
        
        // Get courses this student is enrolled in
        const courses = await Course.find({ enrolledStudents: student._id })
                                   .select('courseName courseId courseCode batch');
        
        return res.json({
            success: true,
            student: {
                name: student.name,
                rollno: student.rollno,
                batch: student.batch,
                email: student.email
            },
            courses: courses.map(course => ({
                courseName: course.courseName,
                courseId: course.courseId,
                courseCode: course.courseCode,
                batch: course.batch
            }))
        });
    } catch (error) {
        console.error('Error fetching student detail:', error);
        return res.status(500).json({ success: false, message: 'Server error' });
    }
};