const Teacher = require('../models/Teacher');
const Student = require('../models/Student');
const Course = require('../models/Course');
const Performance = require('../models/Performance');
const ArchivedCourse = require('../models/ArchivedCourse');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');
const { Readable } = require('stream');

// Helper function to find teacher and course by unique identifiers
const findTeacherAndCourse = async (email, courseId) => {
    const teacher = await Teacher.findOne({ email });
    const course = await Course.findOne({ courseId });
    return { teacher, course };
};

// @route POST /staff/auth
// @desc Authenticate teacher
// @input email, password
exports.staffAuth = async (req, res) => {
    const { email, password } = req.body;
    try {
        const teacher = await Teacher.findOne({ email });
        // NOTE: Simple password check. In a real app, hash this!
        if (teacher && teacher.password === password) {
            res.json({ success: true, message: 'Authentication successful', teacherId: teacher._id, email: teacher.email });
        } else {
            res.status(401).json({ success: false, message: 'Invalid Email or Password' });
        }
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error' });
    }
};

// @route GET /staff/dashboard
// @desc Get courses handled by teacher
// @input teacher mail (query param)
exports.getStaffDashboard = async (req, res) => {
    const { email } = req.query;
    try {
        // Find teacher and populate the courses they handle with basic details
        const teacher = await Teacher.findOne({ email }).populate('coursesHandled', 'courseName courseId courseCode batch');
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        res.json({ success: true, name: teacher.name, courses: teacher.coursesHandled });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error' });
    }
};

// @route GET /staff/course-detail (Roster)
// @desc Get all students enrolled in a course (Roster)
// @input course id (query param)
exports.getCourseRoster = async (req, res) => {
    // Teacher email is typically used for authentication but is not strictly needed for the roster query
    const { courseId } = req.query; 
    try {
        // Fetch course and populate all enrolled student details
        const course = await Course.findOne({ courseId }).populate('enrolledStudents', 'name rollno email');
        if (!course) {
            return res.status(404).json({ success: false, message: 'Course not found' });
        }
        res.json({ success: true, courseName: course.courseName, students: course.enrolledStudents });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error' });
    }
};

// @route POST /staff/add-student
// @desc Enroll a student into a course
// @input teacher email, course id, student email OR rollno
exports.addStudentToCourse = async (req, res) => {
    const { teacherEmail, courseId, studentEmail, rollno } = req.body;
    
    const { teacher, course } = await findTeacherAndCourse(teacherEmail, courseId);
    if (!teacher || !course) {
        return res.status(404).json({ success: false, message: 'Teacher or Course not found' });
    }
    
    // Find student by email or rollno (case-insensitive for rollno)
    let student;
    if (rollno) {
        // Search by rollno (case-insensitive)
        student = await Student.findOne({ rollno: { $regex: new RegExp(`^${rollno}$`, 'i') } });
    } else if (studentEmail) {
        student = await Student.findOne({ email: studentEmail });
    }
    
    if (!student) {
        return res.status(404).json({ 
            success: false, 
            message: `Student not found${rollno ? ` with roll number: ${rollno}` : studentEmail ? ` with email: ${studentEmail}` : ''}`
        });
    }

    if (course.enrolledStudents.includes(student._id)) {
        return res.status(400).json({ success: false, message: 'Student already enrolled in this course' });
    }

    try {
        // 1. Update Course roster and Student course list atomically
        await Promise.all([
            Course.updateOne({ _id: course._id }, { $addToSet: { enrolledStudents: student._id } }),
            Student.updateOne({ _id: student._id }, { $addToSet: { enrolledCourses: course._id } })
        ]);

        // 2. Create initial Performance document
        await Performance.create({
            studentId: student._id,
            courseId: course._id,
            marks: {} // Schema defaults will apply (all to 0)
        });

        res.json({ success: true, message: `Student ${student.name} added to ${course.courseName}` });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
};

// @route POST /staff/create-course
// @desc Create a new course
// @input teacher email, course details
exports.createCourse = async (req, res) => {
    const { teacherEmail, courseName, courseCode, batch } = req.body;
    
    try {
        // Find teacher
        const teacher = await Teacher.findOne({ email: teacherEmail });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        // Generate a unique courseId
        const courseId = `${courseCode}-${batch}`;
        
        // Check if course already exists
        const existingCourse = await Course.findOne({ courseId });
        if (existingCourse) {
            return res.status(400).json({ success: false, message: 'Course with this code and batch already exists' });
        }
        
        // Create course
        const newCourse = await Course.create({
            batch,
            courseName,
            courseCode,
            courseId,
            assignedTeachers: [teacher._id]
        });
        
        // Update teacher's coursesHandled
        await Teacher.updateOne(
            { _id: teacher._id },
            { $addToSet: { coursesHandled: newCourse._id } }
        );
        
        res.json({ 
            success: true, 
            message: `Course ${courseName} created successfully`,
            courseId: newCourse.courseId,
            course: newCourse
        });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
};

// @route POST /staff/add-batch-to-course
// @desc Add all students from a specific batch to a course
// @input teacher email, course id, batch
exports.addBatchToCourse = async (req, res) => {
    const { teacherEmail, courseId, batch } = req.body;
    
    try {
        // Find teacher and course
        const { teacher, course } = await findTeacherAndCourse(teacherEmail, courseId);
        if (!teacher || !course) {
            return res.status(404).json({ success: false, message: 'Teacher or Course not found' });
        }
        
        // Find all students in the batch
        const batchStudents = await Student.find({ batch });
        if (batchStudents.length === 0) {
            return res.status(404).json({ success: false, message: 'No students found in this batch' });
        }
        
        // Track success and failures
        const results = {
            total: batchStudents.length,
            added: 0,
            alreadyEnrolled: 0,
            failed: 0
        };
        
        // Process each student
        for (const student of batchStudents) {
            try {
                // Check if student is already enrolled
                if (course.enrolledStudents.includes(student._id)) {
                    results.alreadyEnrolled++;
                    continue;
                }
                
                // Update course roster and student's enrolled courses
                await Promise.all([
                    Course.updateOne(
                        { _id: course._id }, 
                        { $addToSet: { enrolledStudents: student._id } }
                    ),
                    Student.updateOne(
                        { _id: student._id }, 
                        { $addToSet: { enrolledCourses: course._id } }
                    )
                ]);
                
                // Create performance record
                await Performance.create({
                    studentId: student._id,
                    courseId: course._id,
                    marks: {} // Default marks (all zero)
                });
                
                results.added++;
            } catch (error) {
                console.error(`Error adding student ${student.rollno}:`, error);
                results.failed++;
            }
        }
        
        res.json({
            success: true,
            message: `Added ${results.added} students from batch ${batch} to ${course.courseName}`,
            results
        });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
};

// @route POST /staff/add-students-csv
// @desc Add students to course from CSV file containing roll numbers
// @input teacher email, course id, CSV data
exports.addStudentsFromCSV = async (req, res) => {
    const { teacherEmail, courseId, csvData } = req.body;
    
    try {
        // Find teacher and course
        const { teacher, course } = await findTeacherAndCourse(teacherEmail, courseId);
        if (!teacher || !course) {
            return res.status(404).json({ success: false, message: 'Teacher or Course not found' });
        }
        
        // Parse CSV data
        const results = {
            total: 0,
            added: 0,
            notFound: 0,
            alreadyEnrolled: 0,
            failed: 0
        };
        
        const rollNumbers = [];
        
        // Create a readable stream from the CSV string
        const stream = Readable.from([csvData]);
        
        // Process the CSV stream
        await new Promise((resolve, reject) => {
            stream
                .pipe(csv())
                .on('data', (row) => {
                    // Extract roll number from the CSV row
                    const rollno = row.rollno || row.roll_number || row.roll || Object.values(row)[0];
                    if (rollno) {
                        rollNumbers.push(rollno.trim());
                        results.total++;
                    }
                })
                .on('end', resolve)
                .on('error', reject);
        });
        
        // Process each roll number
        for (const rollno of rollNumbers) {
            try {
                // Find the student (case-insensitive)
                const student = await Student.findOne({ rollno: { $regex: new RegExp(`^${rollno}$`, 'i') } });
                if (!student) {
                    results.notFound++;
                    continue;
                }
                
                // Check if already enrolled
                if (course.enrolledStudents.includes(student._id)) {
                    results.alreadyEnrolled++;
                    continue;
                }
                
                // Update course roster and student's enrolled courses
                await Promise.all([
                    Course.updateOne(
                        { _id: course._id }, 
                        { $addToSet: { enrolledStudents: student._id } }
                    ),
                    Student.updateOne(
                        { _id: student._id }, 
                        { $addToSet: { enrolledCourses: course._id } }
                    )
                ]);
                
                // Create performance record
                await Performance.create({
                    studentId: student._id,
                    courseId: course._id,
                    marks: {} // Default marks
                });
                
                results.added++;
            } catch (error) {
                console.error(`Error adding student ${rollno}:`, error);
                results.failed++;
            }
        }
        
        res.json({
            success: true,
            message: `Added ${results.added} students to ${course.courseName}`,
            results
        });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
};

// @route POST /staff/create-student
// @desc Create a new student in the system
// @input teacher email (for auth), student details
exports.createStudent = async (req, res) => {
    const { teacherEmail, studentName, rollno, batch, studentEmail, password } = req.body;
    
    try {
        // Verify teacher exists (for authorization)
        const teacher = await Teacher.findOne({ email: teacherEmail });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        // Check if student already exists
        const existingStudent = await Student.findOne({ 
            $or: [{ rollno }, { email: studentEmail }] 
        });
        
        if (existingStudent) {
            return res.status(400).json({ 
                success: false, 
                message: 'Student with this roll number or email already exists' 
            });
        }
        
        // Create new student
        const newStudent = await Student.create({
            name: studentName,
            rollno,
            batch,
            email: studentEmail,
            password: password || rollno, // Default password to roll number if not provided
            enrolledCourses: []
        });
        
        res.json({
            success: true,
            message: 'Student created successfully',
            student: {
                id: newStudent._id,
                name: newStudent.name,
                rollno: newStudent.rollno,
                email: newStudent.email,
                batch: newStudent.batch
            }
        });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
};

// @route POST /staff/create-students-csv
// @desc Create multiple students from CSV data
// @input teacher email (for auth), CSV data
exports.createStudentsFromCSV = async (req, res) => {
    const { teacherEmail, csvData } = req.body;
    
    try {
        // Verify teacher exists (for authorization)
        const teacher = await Teacher.findOne({ email: teacherEmail });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        const results = {
            total: 0,
            created: 0,
            alreadyExists: 0,
            failed: 0
        };
        
        const students = [];
        
        // Create a readable stream from the CSV string
        const stream = Readable.from([csvData]);
        
        // Process the CSV stream
        await new Promise((resolve, reject) => {
            stream
                .pipe(csv())
                .on('data', (row) => {
                    // Extract student details from CSV row
                    students.push({
                        name: row.name || row.student_name,
                        rollno: row.rollno || row.roll_number,
                        batch: row.batch || row.section,
                        email: row.email || `${row.rollno || row.roll_number}@psgtech.ac.in`,
                        password: row.password || row.rollno || row.roll_number
                    });
                    results.total++;
                })
                .on('end', resolve)
                .on('error', reject);
        });
        
        // Process each student
        for (const studentData of students) {
            try {
                // Validate required fields
                if (!studentData.name || !studentData.rollno || !studentData.batch) {
                    results.failed++;
                    continue;
                }
                
                // Check if student already exists
                const existingStudent = await Student.findOne({ 
                    $or: [{ rollno: studentData.rollno }, { email: studentData.email }] 
                });
                
                if (existingStudent) {
                    results.alreadyExists++;
                    continue;
                }
                
                // Create new student
                await Student.create(studentData);
                results.created++;
            } catch (error) {
                console.error(`Error creating student ${studentData.rollno}:`, error);
                results.failed++;
            }
        }
        
        res.json({
            success: true,
            message: `Created ${results.created} new students`,
            results
        });
    } catch (error) {
        console.error('Enrollment Error:', error);
        res.status(500).json({ success: false, message: 'Server error during enrollment' });
    }
};

// @route POST /staff/delete-student
// @desc Remove student from course
// @input teacher email, course id, student email
exports.deleteStudentFromCourse = async (req, res) => {
    const { teacherEmail, courseId, studentEmail } = req.body;
    
    const { teacher, course } = await findTeacherAndCourse(teacherEmail, courseId);
    if (!teacher || !course) {
        return res.status(404).json({ success: false, message: 'Teacher or Course not found' });
    }
    
    const student = await Student.findOne({ email: studentEmail });
    if (!student) {
        return res.status(404).json({ success: false, message: 'Student not found' });
    }

    try {
        // 1. Remove student from Course roster and Student course list
        await Promise.all([
            Course.updateOne({ _id: course._id }, { $pull: { enrolledStudents: student._id } }),
            Student.updateOne({ _id: student._id }, { $pull: { enrolledCourses: course._id } })
        ]);

        // 2. Delete the Performance document
        await Performance.deleteOne({
            studentId: student._id,
            courseId: course._id,
        });

        res.json({ success: true, message: `Student ${student.name} removed from ${course.courseName}` });
    } catch (error) {
        console.error('Deletion Error:', error);
        res.status(500).json({ success: false, message: 'Server error during deletion' });
    }
};

// @route POST /staff/student-detail
// @desc Get a single student's performance detail in a specific course
// @input teacher email, student email, course id
exports.getStudentPerformanceDetail = async (req, res) => {
    const { teacherEmail, studentEmail, courseId } = req.body;

    const { teacher, course } = await findTeacherAndCourse(teacherEmail, courseId);
    if (!teacher || !course) {
        return res.status(404).json({ success: false, message: 'Teacher or Course not found' });
    }

    const student = await Student.findOne({ email: studentEmail });
    if (!student) {
        return res.status(404).json({ success: false, message: 'Student not found' });
    }
    
    try {
        const performance = await Performance.findOne({ studentId: student._id, courseId: course._id });
        
        if (!performance) {
            return res.status(404).json({ success: false, message: 'Performance record not found for this student in this course.' });
        }

        res.json({ 
            success: true, 
            studentName: student.name,
            rollno: student.rollno,
            courseName: course.courseName,
            marks: performance.marks 
        });

    } catch (error) {
        console.error('Student Detail Error:', error);
        res.status(500).json({ success: false, message: 'Server error retrieving student detail' });
    }
}


// ----------------- MARK UPDATING ENDPOINTS (General function for bulk/single update) -----------------

/**
 * Creates a generic handler for mark updates (supporting single or bulk input).
 * This function is reused for all 7 assessment components (Tut 1-4, CA 1-2, Assignment).
 * @param {string} markField - The key in the Performance.marks object (e.g., 'tutorial1', 'CA1').
 */
const createMarkUpdateHandler = (markField) => async (req, res) => {
    const { teacherEmail, courseId, studentInput } = req.body; 
    
    try {
        const { teacher, course } = await findTeacherAndCourse(teacherEmail, courseId);
        if (!teacher || !course) {
            return res.status(404).json({ success: false, message: 'Teacher or Course not found' });
        }

        let studentsToUpdate = [];

        // Determine if it's a bulk (array) or single (object) update
        if (Array.isArray(studentInput)) {
            // Bulk update format: [{ email: 's1@a.com', mark: 10 }, ...]
            studentsToUpdate = studentInput;
        } else if (studentInput && studentInput.email && studentInput.mark !== undefined) {
            // Single update format: { email: 's1@a.com', mark: 10 }
            studentsToUpdate = [studentInput];
        } else {
            return res.status(400).json({ success: false, message: 'Invalid or missing studentInput format. Expected single { email, mark } or array of objects.' });
        }

        let updateResults = [];
        const updateKey = `marks.${markField}`;

        for (const input of studentsToUpdate) {
            const { email, rollno, mark } = input;
            
            // Find student by email or rollno
            let student;
            if (email) {
                student = await Student.findOne({ email });
            }
            if (!student && rollno) {
                student = await Student.findOne({ rollno });
            }
            
            if (!student) {
                updateResults.push({ email: email || rollno, status: 'failed', message: 'Student not found' });
                continue;
            }

            // Find the correct performance document and update the specific mark field
            const performance = await Performance.findOneAndUpdate(
                { studentId: student._id, courseId: course._id },
                { $set: { [updateKey]: mark } },
                { new: true, upsert: false } 
            );

            if (performance) {
                updateResults.push({ email: email || student.email, status: 'success', message: `${markField} updated to ${mark}` });
            } else {
                updateResults.push({ email: email || student.email, status: 'failed', message: 'Performance record not found. Ensure student is enrolled via /add-student.' });
            }
        }

        res.json({ success: true, message: `${markField} update process complete.`, results: updateResults });

    } catch (error) {
        console.error(`Mark Update Error (${markField}):`, error);
        res.status(500).json({ success: false, message: `Server error during ${markField} update` });
    }
};

// Exporting the mark handlers linked to the generic function
// These correspond to the Post add-tutX-mark/, Post add-caX-mark/, Post add-assignent-mark/ routes
exports.addTut1Mark = createMarkUpdateHandler('tutorial1');
exports.addTut2Mark = createMarkUpdateHandler('tutorial2');
exports.addTut3Mark = createMarkUpdateHandler('tutorial3');
exports.addTut4Mark = createMarkUpdateHandler('tutorial4');
exports.addCA1Mark = createMarkUpdateHandler('CA1');
exports.addCA2Mark = createMarkUpdateHandler('CA2');
exports.addAssignmentMark = createMarkUpdateHandler('assignmentPresentation');

// @route GET /staff/course-analytics
// @desc Get detailed analytics for a specific course
// @input course id (query param)
exports.getCourseAnalytics = async (req, res) => {
    const { courseId } = req.query;
    
    try {
        // Fetch course with enrolled students
        const course = await Course.findOne({ courseId }).populate('enrolledStudents');
        
        if (!course) {
            return res.status(404).json({ success: false, message: 'Course not found' });
        }
        
        // Get performance data for all students in the course
        const performances = await Performance.find({
            courseId: course._id
        }).populate('studentId', 'name rollno email');
        
        // Calculate overall statistics
        const overallStats = calculateCourseStatistics(performances);
        
        // Format student-specific performance data
        const studentPerformances = {};
        performances.forEach(performance => {
            const student = performance.studentId;
            if (student) {
                // Skip if student reference is null (shouldn't happen, but just in case)
                studentPerformances[student.rollno] = {
                    tutorial1: performance.marks.tutorial1,
                    tutorial2: performance.marks.tutorial2,
                    tutorial3: performance.marks.tutorial3,
                    tutorial4: performance.marks.tutorial4,
                    CA1: performance.marks.CA1,
                    CA2: performance.marks.CA2,
                    assignmentPresentation: performance.marks.assignmentPresentation,
                    
                    // Calculate component-wise subtotals
                    tutorialScore: (
                        performance.marks.tutorial1 + 
                        performance.marks.tutorial2 + 
                        performance.marks.tutorial3 + 
                        performance.marks.tutorial4
                    ),
                    caScore: (performance.marks.CA1 + performance.marks.CA2),
                    assignmentScore: performance.marks.assignmentPresentation,
                    
                    // Calculate final internal marks (out of 50)
                    finalInternal: calculateFinalInternal(performance.marks),
                    
                    // Calculate grade based on final internal
                    grade: calculateGrade(calculateFinalInternal(performance.marks))
                };
            }
        });
        
        res.json({ 
            success: true, 
            overallStats,
            studentPerformances
        });
    } catch (error) {
        console.error('Course Analytics Error:', error);
        res.status(500).json({ success: false, message: 'Server error retrieving course analytics' });
    }
};

// @route GET /staff/student-performance
// @desc Get detailed performance data for a specific student in a course
// @input student id, course id (query params)
exports.getStudentPerformance = async (req, res) => {
    const { studentId, courseId } = req.query;
    
    try {
        const student = await Student.findById(studentId);
        const course = await Course.findById(courseId);
        
        if (!student || !course) {
            return res.status(404).json({ 
                success: false, 
                message: !student ? 'Student not found' : 'Course not found' 
            });
        }
        
        const performance = await Performance.findOne({
            studentId: student._id,
            courseId: course._id
        });
        
        if (!performance) {
            return res.status(404).json({ 
                success: false, 
                message: 'No performance record found for this student in this course' 
            });
        }
        
        // Calculate component scores and final internal
        const tutorialScore = (
            performance.marks.tutorial1 + 
            performance.marks.tutorial2 + 
            performance.marks.tutorial3 + 
            performance.marks.tutorial4
        );
        
        const caScore = (performance.marks.CA1 + performance.marks.CA2);
        const assignmentScore = performance.marks.assignmentPresentation;
        const finalInternal = calculateFinalInternal(performance.marks);
        
        res.json({
            success: true,
            student: {
                id: student._id,
                name: student.name,
                rollno: student.rollno,
                email: student.email
            },
            course: {
                id: course._id,
                name: course.courseName,
                courseId: course.courseId
            },
            performance: {
                tutorial1: performance.marks.tutorial1,
                tutorial2: performance.marks.tutorial2,
                tutorial3: performance.marks.tutorial3,
                tutorial4: performance.marks.tutorial4,
                CA1: performance.marks.CA1,
                CA2: performance.marks.CA2,
                assignmentPresentation: performance.marks.assignmentPresentation,
                tutorialScore,
                caScore,
                assignmentScore,
                finalInternal,
                grade: calculateGrade(finalInternal)
            },
            tutorialMaxMarks: 10  // Default, could be made configurable
        });
        
    } catch (error) {
        console.error('Student Performance Error:', error);
        res.status(500).json({ success: false, message: 'Server error retrieving student performance' });
    }
};

// @route POST /staff/update-student-marks
// @desc Update performance marks for a specific student
// @input student id, course id, teacher email, marks object
exports.updateStudentMarks = async (req, res) => {
    const { studentId, courseId, teacherEmail, marks } = req.body;
    
    try {
        const student = await Student.findById(studentId);
        const course = await Course.findById(courseId);
        const teacher = await Teacher.findOne({ email: teacherEmail });
        
        if (!student || !course || !teacher) {
            return res.status(404).json({ 
                success: false, 
                message: 'Student, course, or teacher not found' 
            });
        }
        
        // Ensure teacher is assigned to this course
        if (!course.assignedTeachers.includes(teacher._id)) {
            return res.status(403).json({
                success: false,
                message: 'Teacher is not authorized for this course'
            });
        }
        
        // Find and update the performance record
        const performance = await Performance.findOne({
            studentId: student._id,
            courseId: course._id
        });
        
        if (!performance) {
            return res.status(404).json({
                success: false,
                message: 'No performance record found for this student in this course'
            });
        }
        
        // Update only the marks that were provided in the request
        Object.keys(marks).forEach(key => {
            if (performance.marks[key] !== undefined) {
                performance.marks[key] = marks[key];
            }
        });
        
        await performance.save();
        
        res.json({
            success: true,
            message: 'Student marks updated successfully',
            studentName: student.name,
            courseName: course.courseName
        });
        
    } catch (error) {
        console.error('Update Marks Error:', error);
        res.status(500).json({ success: false, message: 'Server error updating student marks' });
    }
};

// Helper function to calculate grade based on internal marks
const calculateGrade = (internalMarks) => {
    // Based on a 50-point internal assessment
    if (internalMarks >= 45) return 'A';  // 90%+
    if (internalMarks >= 40) return 'B';  // 80%+
    if (internalMarks >= 35) return 'C';  // 70%+
    if (internalMarks >= 30) return 'D';  // 60%+
    if (internalMarks >= 25) return 'E';  // 50%+
    return 'F';                           // Below 50%
};

// Helper function to calculate final internal marks out of 50
const calculateFinalInternal = (marks) => {
    // Calculate tutorial total (max 15 points - weighted average of best 3 out of 4)
    const tutorials = [
        marks.tutorial1 || 0,
        marks.tutorial2 || 0, 
        marks.tutorial3 || 0,
        marks.tutorial4 || 0
    ];
    
    // Sort tutorials in descending order and take top 3
    tutorials.sort((a, b) => b - a);
    const tutorialTotal = (tutorials[0] + tutorials[1] + tutorials[2]) * (15 / 30);
    
    // Calculate CA total (max 20 points)
    const caTotal = (marks.CA1 || 0) + (marks.CA2 || 0);
    
    // Calculate assignment/presentation (max 15 points)
    const assignmentTotal = marks.assignmentPresentation || 0;
    
    // Calculate final internal (out of 50)
    return tutorialTotal + caTotal + assignmentTotal;
};

// Helper function to calculate course-wide statistics
const calculateCourseStatistics = (performances) => {
    if (!performances.length) {
        return {
            averageScore: 0,
            highestScore: 0,
            lowestScore: 0,
            gradeDistribution: { A: 0, B: 0, C: 0, D: 0, E: 0, F: 0 },
            componentAverages: {
                tutorial1: 0,
                tutorial2: 0,
                tutorial3: 0,
                tutorial4: 0,
                CA1: 0,
                CA2: 0,
                assignmentPresentation: 0
            }
        };
    }
    
    // Calculate totals for each component
    let totalScores = {
        tutorial1: 0,
        tutorial2: 0,
        tutorial3: 0,
        tutorial4: 0,
        CA1: 0,
        CA2: 0,
        assignmentPresentation: 0,
        finalInternal: 0
    };
    
    // Track grade distribution
    let gradeDistribution = {
        A: 0, B: 0, C: 0, D: 0, E: 0, F: 0
    };
    
    // Keep track of min/max scores
    let highestScore = 0;
    let lowestScore = 50;  // Max possible internal marks
    
    // Process each student's performance
    performances.forEach(performance => {
        // Calculate final internal for this student
        const finalInternal = calculateFinalInternal(performance.marks);
        
        // Update totals
        totalScores.tutorial1 += performance.marks.tutorial1 || 0;
        totalScores.tutorial2 += performance.marks.tutorial2 || 0;
        totalScores.tutorial3 += performance.marks.tutorial3 || 0;
        totalScores.tutorial4 += performance.marks.tutorial4 || 0;
        totalScores.CA1 += performance.marks.CA1 || 0;
        totalScores.CA2 += performance.marks.CA2 || 0;
        totalScores.assignmentPresentation += performance.marks.assignmentPresentation || 0;
        totalScores.finalInternal += finalInternal;
        
        // Update grade distribution
        const grade = calculateGrade(finalInternal);
        gradeDistribution[grade]++;
        
        // Update highest/lowest scores
        if (finalInternal > highestScore) highestScore = finalInternal;
        if (finalInternal < lowestScore) lowestScore = finalInternal;
    });
    
    // Calculate averages
    const studentCount = performances.length;
    const averages = {
        tutorial1: totalScores.tutorial1 / studentCount,
        tutorial2: totalScores.tutorial2 / studentCount,
        tutorial3: totalScores.tutorial3 / studentCount,
        tutorial4: totalScores.tutorial4 / studentCount,
        CA1: totalScores.CA1 / studentCount,
        CA2: totalScores.CA2 / studentCount,
        assignmentPresentation: totalScores.assignmentPresentation / studentCount
    };
    
    return {
        averageScore: totalScores.finalInternal / studentCount,
        highestScore,
        lowestScore: lowestScore === 50 ? 0 : lowestScore,  // Reset to 0 if no records found
        gradeDistribution,
        componentAverages: averages
    };
};

/**
 * @route GET /staff/course-analytics
 * @desc Get analytics data for a specific course
 * @input courseId (query param)
 * @returns Course analytics with performance metrics
 */
const getCourseAnalytics = async (req, res) => {
    const { courseId } = req.query;
    
    try {
        // Find the course
        const course = await Course.findOne({ courseId }).populate('enrolledStudents');
        if (!course) {
            return res.status(404).json({ success: false, message: 'Course not found' });
        }

        // Get all performances for this course
        const performances = await Performance.find({
            courseId: course._id
        }).populate('studentId', 'name rollno email');

        // Calculate overall statistics
        const overallStats = {
            avgScore: 0,
            tutorialCompletionRate: 0,
            assignmentCompletionRate: 0,
            gradeDistribution: {
                'A': 0, // 90-100%
                'B': 0, // 80-89%
                'C': 0, // 70-79%
                'D': 0, // 60-69%
                'F': 0, // <60%
            }
        };

        // Map for storing individual student performances
        const studentPerformances = {};
        
        // Process each performance record
        let totalInternalMarks = 0;
        let totalTutorialScore = 0;
        let totalCAScore = 0;
        let totalAssignmentScore = 0;
        let tutorialSubmissions = 0;
        let assignmentSubmissions = 0;
        
        performances.forEach(perf => {
            const studentRollno = perf.studentId.rollno;
            
            // Calculate tutorial score (average of tutorials 1-4, scaled to 15 marks)
            const tut1 = perf.marks.tutorial1 || 0;
            const tut2 = perf.marks.tutorial2 || 0;
            const tut3 = perf.marks.tutorial3 || 0;
            const tut4 = perf.marks.tutorial4 || 0;
            const tutAvg = (tut1 + tut2 + tut3 + tut4) / 4;
            const tutorialScore = tutAvg * 1.5; // Scale to 15 marks (assuming tutorials are out of 10)
            
            // Calculate CA score (average of CA1 & CA2)
            const ca1 = perf.marks.CA1 || 0;
            const ca2 = perf.marks.CA2 || 0;
            const caScore = (ca1 + ca2) / 2;
            
            // Calculate assignment score
            const assignmentScore = perf.marks.assignmentPresentation || 0;
            
            // Calculate internal marks (total of tutorial, CA, and assignment scores)
            const internalTotal = tutorialScore + caScore + assignmentScore;
            
            // Calculate final internal marks (scaled to 40)
            const finalInternal = (internalTotal / 50) * 40;
            
            // Determine grade
            let grade = 'F';
            if (finalInternal >= 36) grade = 'A';      // 90%+
            else if (finalInternal >= 32) grade = 'B'; // 80%+
            else if (finalInternal >= 28) grade = 'C'; // 70%+
            else if (finalInternal >= 24) grade = 'D'; // 60%+
            
            // Increment grade distribution
            overallStats.gradeDistribution[grade]++;
            
            // Track if tutorial/assignment were submitted
            if (tut1 > 0 || tut2 > 0 || tut3 > 0 || tut4 > 0) tutorialSubmissions++;
            if (assignmentScore > 0) assignmentSubmissions++;
            
            // Add to totals for averages
            totalInternalMarks += finalInternal;
            totalTutorialScore += tutorialScore;
            totalCAScore += caScore;
            totalAssignmentScore += assignmentScore;
            
            // Store student performance data
            studentPerformances[studentRollno] = {
                tutorial1_score: tut1,
                tutorial2_score: tut2,
                tutorial3_score: tut3,
                tutorial4_score: tut4,
                tutorial_average: tutAvg,
                tutorialScore: tutorialScore,
                ca1_original: ca1 * 2.5, // Convert from 20 scale to original 50 scale
                ca1_scaled: ca1,
                ca2_original: ca2 * 2.5, // Convert from 20 scale to original 50 scale
                ca2_scaled: ca2,
                caScore: caScore,
                assignment_score: assignmentScore > 10 ? assignmentScore - 10 : 0, // Assuming assignment is 10 marks
                presentation_score: assignmentScore > 10 ? 10 : assignmentScore, // Assuming presentation is remaining marks
                assignmentScore: assignmentScore,
                internalTotal: internalTotal,
                finalInternal: finalInternal,
                grade: grade
            };
        });
        
        // Calculate averages and rates
        const studentCount = performances.length > 0 ? performances.length : 1; // Avoid division by zero
        overallStats.avgScore = totalInternalMarks / studentCount;
        overallStats.tutorialCompletionRate = (tutorialSubmissions / studentCount) * 100;
        overallStats.assignmentCompletionRate = (assignmentSubmissions / studentCount) * 100;
        
        return res.json({
            success: true,
            courseName: course.courseName,
            batch: course.batch,
            studentCount: studentCount,
            overallStats,
            studentPerformances
        });
        
    } catch (error) {
        console.error('Course Analytics Error:', error);
        res.status(500).json({ success: false, message: 'Server error during analytics generation' });
    }
};

/**
 * @route GET /staff/student-performance
 * @desc Get performance data for a specific student in a course
 * @input studentId (query param), courseId (query param)
 * @returns Detailed performance data for the student
 */
const getStudentPerformance = async (req, res) => {
    const { studentId, courseId } = req.query;
    
    try {
        // Find student and course
        const student = await Student.findOne({ rollno: studentId });
        const course = await Course.findOne({ courseId });
        
        if (!student || !course) {
            return res.status(404).json({ 
                success: false, 
                message: !student ? 'Student not found' : 'Course not found' 
            });
        }
        
        // Get performance data
        const performance = await Performance.findOne({
            studentId: student._id,
            courseId: course._id
        });
        
        if (!performance) {
            return res.status(404).json({
                success: false,
                message: 'No performance record found for this student in this course'
            });
        }
        
        // Calculate scores
        const tut1 = performance.marks.tutorial1 || 0;
        const tut2 = performance.marks.tutorial2 || 0;
        const tut3 = performance.marks.tutorial3 || 0;
        const tut4 = performance.marks.tutorial4 || 0;
        
        const tutAvg = (tut1 + tut2 + tut3 + tut4) / 4;
        const tutorialScore = tutAvg * 1.5; // Scale to 15 marks
        
        const ca1 = performance.marks.CA1 || 0;
        const ca2 = performance.marks.CA2 || 0;
        const caScore = (ca1 + ca2) / 2;
        
        const assignmentScore = performance.marks.assignmentPresentation || 0;
        
        // Calculate internal marks (total of tutorial, CA, and assignment scores)
        const internalTotal = tutorialScore + caScore + assignmentScore;
        
        // Calculate final internal marks (scaled to 40)
        const finalInternal = (internalTotal / 50) * 40;
        
        // Determine grade
        let grade = 'F';
        if (finalInternal >= 36) grade = 'A';      // 90%+
        else if (finalInternal >= 32) grade = 'B'; // 80%+
        else if (finalInternal >= 28) grade = 'C'; // 70%+
        else if (finalInternal >= 24) grade = 'D'; // 60%+
        
        res.json({
            success: true,
            student: {
                name: student.name,
                rollno: student.rollno,
                email: student.email
            },
            performance: {
                tutorial1_score: tut1,
                tutorial2_score: tut2,
                tutorial3_score: tut3,
                tutorial4_score: tut4,
                tutorial_average: tutAvg,
                tutorialScore,
                ca1_original: ca1 * 2.5, // Convert from 20 scale to original 50 scale
                ca1_scaled: ca1,
                ca2_original: ca2 * 2.5,
                ca2_scaled: ca2,
                caScore,
                assignment_score: assignmentScore > 10 ? assignmentScore - 10 : 0,
                presentation_score: assignmentScore > 10 ? 10 : assignmentScore,
                assignmentScore,
                internalTotal,
                finalInternal,
                grade
            },
            tutorialMaxMarks: 10
        });
        
    } catch (error) {
        console.error('Student Performance Error:', error);
        res.status(500).json({ success: false, message: 'Server error retrieving student performance' });
    }
};

/**
 * @route POST /staff/update-student-marks
 * @desc Update marks for a specific student in a course
 * @input studentId, courseId, marks (object with mark fields)
 * @returns Success message
 */
const updateStudentMarks = async (req, res) => {
    const { studentId, courseId, teacherEmail, marks } = req.body;
    
    try {
        // Find teacher for authorization
        const teacher = await Teacher.findOne({ email: teacherEmail });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        // Find student and course
        const student = await Student.findOne({ rollno: studentId });
        const course = await Course.findOne({ courseId });
        
        if (!student || !course) {
            return res.status(404).json({ 
                success: false, 
                message: !student ? 'Student not found' : 'Course not found' 
            });
        }
        
        // Ensure student is enrolled in the course
        if (!course.enrolledStudents.includes(student._id)) {
            return res.status(400).json({ 
                success: false, 
                message: 'Student is not enrolled in this course' 
            });
        }
        
        // Find performance record
        const performance = await Performance.findOne({
            studentId: student._id,
            courseId: course._id
        });
        
        if (!performance) {
            return res.status(404).json({
                success: false,
                message: 'No performance record found for this student'
            });
        }
        
        // Update mark fields
        const updateFields = {};
        
        if (marks.tutorial1 !== undefined) updateFields['marks.tutorial1'] = marks.tutorial1;
        if (marks.tutorial2 !== undefined) updateFields['marks.tutorial2'] = marks.tutorial2;
        if (marks.tutorial3 !== undefined) updateFields['marks.tutorial3'] = marks.tutorial3;
        if (marks.tutorial4 !== undefined) updateFields['marks.tutorial4'] = marks.tutorial4;
        if (marks.ca1 !== undefined) updateFields['marks.CA1'] = marks.ca1;
        if (marks.ca2 !== undefined) updateFields['marks.CA2'] = marks.ca2;
        if (marks.assignment !== undefined) updateFields['marks.assignmentPresentation'] = marks.assignment;
        
        // Apply updates
        await Performance.updateOne(
            { _id: performance._id },
            { $set: updateFields }
        );
        
        res.json({
            success: true,
            message: `Marks updated successfully for student ${student.name}`
        });
        
    } catch (error) {
        console.error('Mark Update Error:', error);
        res.status(500).json({ success: false, message: 'Server error updating marks' });
    }
};

// Export the analytics endpoints
exports.getCourseAnalytics = getCourseAnalytics;
exports.getStudentPerformance = getStudentPerformance;
exports.updateStudentMarks = updateStudentMarks;

/**
 * @route GET /staff/all-students
 * @desc Get all students in the system for a staff member with optional filtering
 * @input email (query param) - staff email for verification
 * @input name (query param, optional) - filter students by name (partial match)
 * @input batch (query param, optional) - filter students by batch (exact match)
 * @input rollno (query param, optional) - filter students by roll number (partial match)
 * @input student_email (query param, optional) - filter students by email (partial match)
 * @returns List of filtered students in the system
 */
exports.getAllStudents = async (req, res) => {
    const { email, name, batch, rollno, student_email } = req.query;
    
    try {
        // Verify the staff member exists
        const teacher = await Teacher.findOne({ email });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        // Build filter query based on provided parameters
        const filterQuery = {};
        
        // Add name filter if provided (case-insensitive partial match)
        if (name) {
            filterQuery.name = { $regex: name, $options: 'i' };
        }
        
        // Add batch filter if provided (exact match)
        if (batch) {
            filterQuery.batch = batch;
        }
        
        // Add roll number filter if provided (case-insensitive partial match)
        if (rollno) {
            filterQuery.rollno = { $regex: rollno, $options: 'i' };
        }
        
        // Add email filter if provided (case-insensitive partial match)
        if (student_email) {
            filterQuery.email = { $regex: student_email, $options: 'i' };
        }
        
        // Get students matching the filters
        const students = await Student.find(filterQuery).select('name rollno batch email');
        
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
        console.error('Error fetching filtered students:', error);
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

// @route POST /staff/archive-course
// @desc Archive a course - move it to ArchivedCourse collection
// @input email (teacher email), courseId
exports.archiveCourse = async (req, res) => {
    const { email, courseId } = req.body;
    
    try {
        // Find teacher and course
        const teacher = await Teacher.findOne({ email });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        const course = await Course.findOne({ courseId }).populate('enrolledStudents');
        if (!course) {
            return res.status(404).json({ success: false, message: 'Course not found' });
        }
        
        // Verify teacher handles this course
        if (!teacher.coursesHandled.includes(course._id)) {
            return res.status(403).json({ success: false, message: 'Unauthorized to archive this course' });
        }
        
        // Fetch all performance data for students in this course
        const performanceData = await Performance.find({ 
            courseId: course._id,
            studentId: { $in: course.enrolledStudents.map(s => s._id) }
        }).populate('studentId');
        
        console.log(`📊 Found ${performanceData.length} performance records for course ${courseId}`);
        
        // Create performance snapshot with correct field access
        const performanceSnapshot = performanceData.map(perf => {
            console.log(`Student ${perf.studentId.rollno} marks:`, perf.marks);
            
            // Calculate total marks from all components
            const totalMarks = (perf.marks.tutorial1 || 0) + 
                             (perf.marks.tutorial2 || 0) + 
                             (perf.marks.tutorial3 || 0) + 
                             (perf.marks.tutorial4 || 0) + 
                             (perf.marks.CA1 || 0) + 
                             (perf.marks.CA2 || 0) + 
                             (perf.marks.assignmentPresentation || 0);
            
            console.log(`  Total calculated: ${totalMarks}`);
            
            return {
                studentId: perf.studentId._id,
                marks: {
                    tutorial1: perf.marks.tutorial1 || 0,
                    tutorial2: perf.marks.tutorial2 || 0,
                    tutorial3: perf.marks.tutorial3 || 0,
                    tutorial4: perf.marks.tutorial4 || 0,
                    CA1: perf.marks.CA1 || 0,
                    CA2: perf.marks.CA2 || 0,
                    assignmentPresentation: perf.marks.assignmentPresentation || 0
                },
                totalMarks: totalMarks
            };
        });
        
        console.log(`✅ Created performance snapshot with ${performanceSnapshot.length} entries`);
        
        // Create archived course document
        const archivedCourse = new ArchivedCourse({
            courseId: course.courseId,
            courseName: course.courseName,
            courseCode: course.courseCode,
            batch: course.batch,
            teacherId: teacher._id,
            teacherEmail: teacher.email,
            enrolledStudents: course.enrolledStudents.map(s => s._id),
            archivedBy: email,
            originalCreatedAt: course.createdAt,
            performanceSnapshot: performanceSnapshot
        });
        
        await archivedCourse.save();
        console.log(`💾 Archived course saved with ID: ${archivedCourse._id}`);
        console.log(`   Performance snapshot contains ${archivedCourse.performanceSnapshot.length} student records`);
        
        // Remove course from teacher's coursesHandled
        teacher.coursesHandled = teacher.coursesHandled.filter(c => !c.equals(course._id));
        await teacher.save();
        console.log(`👤 Removed course from teacher's coursesHandled`);
        
        // CRITICAL FIX: Remove course from all students' enrolledCourses arrays
        // This prevents broken references when the course is deleted
        const studentIds = course.enrolledStudents.map(s => s._id);
        const updateResult = await Student.updateMany(
            { _id: { $in: studentIds } },
            { $pull: { enrolledCourses: course._id } }
        );
        console.log(`👥 Removed course from ${updateResult.modifiedCount} students' enrolledCourses arrays`);
        
        // Delete performance records for this course
        const deletedPerf = await Performance.deleteMany({ courseId: course._id });
        console.log(`🗑️ Deleted ${deletedPerf.deletedCount} performance records`);
        
        // Delete the original course
        await Course.deleteOne({ _id: course._id });
        console.log(`🗑️ Deleted original course: ${course.courseId}`);
        
        res.json({ 
            success: true, 
            message: 'Course archived successfully',
            archivedCourseId: archivedCourse._id
        });
        
    } catch (error) {
        console.error('❌ Error archiving course:', error);
        res.status(500).json({ success: false, message: 'Server error while archiving course' });
    }
};

// @route POST /staff/restore-course
// @desc Restore an archived course back to active courses
// @input email (teacher email), archivedCourseId
exports.restoreCourse = async (req, res) => {
    const { email, archivedCourseId } = req.body;
    
    try {
        // Find teacher
        const teacher = await Teacher.findOne({ email });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        // Find archived course
        const archivedCourse = await ArchivedCourse.findById(archivedCourseId).populate('enrolledStudents');
        if (!archivedCourse) {
            return res.status(404).json({ success: false, message: 'Archived course not found' });
        }
        
        // Verify teacher is authorized to restore
        if (archivedCourse.teacherEmail !== email) {
            return res.status(403).json({ success: false, message: 'Unauthorized to restore this course' });
        }
        
        // Check if course with same courseId already exists
        const existingCourse = await Course.findOne({ courseId: archivedCourse.courseId });
        if (existingCourse) {
            return res.status(400).json({ 
                success: false, 
                message: 'A course with this ID already exists in active courses' 
            });
        }
        
        // Recreate the course
        const restoredCourse = new Course({
            courseName: archivedCourse.courseName,
            courseId: archivedCourse.courseId,
            courseCode: archivedCourse.courseCode,
            batch: archivedCourse.batch,
            enrolledStudents: archivedCourse.enrolledStudents.map(s => s._id),
            createdAt: archivedCourse.originalCreatedAt || new Date()
        });
        
        await restoredCourse.save();
        console.log(`📚 Restored course: ${restoredCourse.courseId} with ID: ${restoredCourse._id}`);
        
        // Restore performance data with correct nested structure
        console.log(`📊 Restoring ${archivedCourse.performanceSnapshot.length} performance records`);
        
        const performanceRecords = archivedCourse.performanceSnapshot.map(snapshot => {
            console.log(`  Restoring marks for student ${snapshot.studentId}:`, snapshot.marks);
            return {
                studentId: snapshot.studentId,
                courseId: restoredCourse._id,
                marks: {
                    tutorial1: snapshot.marks.tutorial1,
                    tutorial2: snapshot.marks.tutorial2,
                    tutorial3: snapshot.marks.tutorial3,
                    tutorial4: snapshot.marks.tutorial4,
                    CA1: snapshot.marks.CA1,
                    CA2: snapshot.marks.CA2,
                    assignmentPresentation: snapshot.marks.assignmentPresentation
                }
            };
        });
        
        const insertedPerf = await Performance.insertMany(performanceRecords);
        console.log(`✅ Inserted ${insertedPerf.length} performance records`);
        
        // Add course back to teacher's coursesHandled
        teacher.coursesHandled.push(restoredCourse._id);
        await teacher.save();
        console.log(`👤 Added course back to teacher's coursesHandled`);
        
        // CRITICAL FIX: Update all students' enrolledCourses arrays with the new course ObjectId
        // This is necessary because when we archived the course, the old Course document was deleted,
        // and now we've created a new one with a different ObjectId
        const studentIds = archivedCourse.enrolledStudents.map(s => s._id);
        const updateResult = await Student.updateMany(
            { _id: { $in: studentIds } },
            { $addToSet: { enrolledCourses: restoredCourse._id } }
        );
        console.log(`👥 Updated ${updateResult.modifiedCount} students' enrolledCourses arrays`);
        
        // Delete the archived course
        await ArchivedCourse.deleteOne({ _id: archivedCourse._id });
        console.log(`🗑️ Deleted archived course record`);
        
        res.json({ 
            success: true, 
            message: 'Course restored successfully',
            courseId: restoredCourse.courseId
        });
        
    } catch (error) {
        console.error('❌ Error restoring course:', error);
        res.status(500).json({ success: false, message: 'Server error while restoring course' });
    }
};

// @route GET /staff/archived-courses
// @desc Get all archived courses for a teacher
// @input email (query param)
exports.getArchivedCourses = async (req, res) => {
    const { email } = req.query;
    
    try {
        const teacher = await Teacher.findOne({ email });
        if (!teacher) {
            return res.status(404).json({ success: false, message: 'Teacher not found' });
        }
        
        // Find all archived courses for this teacher
        const archivedCourses = await ArchivedCourse.find({ teacherEmail: email })
            .populate('enrolledStudents', 'name rollno email')
            .sort({ archivedAt: -1 });
        
        res.json({ 
            success: true, 
            archivedCourses: archivedCourses.map(course => ({
                id: course._id,
                courseId: course.courseId,
                courseName: course.courseName,
                courseCode: course.courseCode,
                batch: course.batch,
                archivedAt: course.archivedAt,
                studentCount: course.enrolledStudents.length
            }))
        });
        
    } catch (error) {
        console.error('Error fetching archived courses:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
};

// @route GET /staff/all-batches
// @desc Get all available batches from students
exports.getAllBatches = async (req, res) => {
    try {
        // Get distinct batches from students collection
        const batches = await Student.distinct('batch');
        
        // Filter out empty values and sort
        const validBatches = batches.filter(batch => batch && batch.trim() !== '').sort();
        
        res.json({
            success: true,
            batches: validBatches
        });
    } catch (error) {
        console.error('Error fetching batches:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
};

// @route POST /staff/remove-student
// @desc Remove a student from a course
// @input teacherEmail, courseId, studentRollno or studentEmail
exports.removeStudentFromCourse = async (req, res) => {
    const { teacherEmail, courseId, studentRollno, studentEmail } = req.body;
    
    try {
        // Find teacher and course
        const { teacher, course } = await findTeacherAndCourse(teacherEmail, courseId);
        if (!teacher || !course) {
            return res.status(404).json({ success: false, message: 'Teacher or Course not found' });
        }
        
        // Find student by rollno (case-insensitive) or email
        let student;
        if (studentRollno) {
            student = await Student.findOne({ rollno: { $regex: new RegExp(`^${studentRollno}$`, 'i') } });
        } else if (studentEmail) {
            student = await Student.findOne({ email: studentEmail });
        }
        
        if (!student) {
            return res.status(404).json({ 
                success: false, 
                message: `Student not found${studentRollno ? ` with roll number: ${studentRollno}` : studentEmail ? ` with email: ${studentEmail}` : ''}`
            });
        }
        
        // Check if student is enrolled in the course
        if (!course.enrolledStudents.includes(student._id)) {
            return res.status(400).json({ 
                success: false, 
                message: 'Student is not enrolled in this course' 
            });
        }
        
        // Remove student from course and course from student's enrolledCourses
        await Promise.all([
            Course.updateOne(
                { _id: course._id },
                { $pull: { enrolledStudents: student._id } }
            ),
            Student.updateOne(
                { _id: student._id },
                { $pull: { enrolledCourses: course._id } }
            ),
            // Remove performance record
            Performance.deleteOne({
                studentId: student._id,
                courseId: course._id
            })
        ]);
        
        console.log(`✅ Removed student ${student.rollno} (${student.name}) from course ${course.courseCode}`);
        
        res.json({ 
            success: true, 
            message: `Successfully removed ${student.name} (${student.rollno}) from ${course.courseName}`,
            student: {
                name: student.name,
                rollno: student.rollno,
                email: student.email
            }
        });
    } catch (error) {
        console.error('Error removing student from course:', error);
        res.status(500).json({ success: false, message: 'Server error', error: error.message });
    }
};

// @route GET /staff/archived-course-detail
// @desc Get detailed information about an archived course
// @input archivedCourseId (query param)
exports.getArchivedCourseDetail = async (req, res) => {
    const { archivedCourseId } = req.query;
    
    try {
        const archivedCourse = await ArchivedCourse.findById(archivedCourseId)
            .populate('enrolledStudents', 'name rollno email batch')
            .populate('teacherId', 'name email');
        
        if (!archivedCourse) {
            return res.status(404).json({ success: false, message: 'Archived course not found' });
        }
        
        // Combine student info with their performance snapshot
        const studentsWithMarks = archivedCourse.enrolledStudents.map(student => {
            const perfSnapshot = archivedCourse.performanceSnapshot.find(
                p => p.studentId.toString() === student._id.toString()
            );
            
            return {
                _id: student._id,
                name: student.name,
                rollno: student.rollno,
                email: student.email,
                batch: student.batch,
                marks: perfSnapshot ? perfSnapshot.marks : {},
                totalMarks: perfSnapshot ? perfSnapshot.totalMarks : 0
            };
        });
        
        res.json({
            success: true,
            course: {
                id: archivedCourse._id,
                courseId: archivedCourse.courseId,
                courseName: archivedCourse.courseName,
                courseCode: archivedCourse.courseCode,
                batch: archivedCourse.batch,
                teacherName: archivedCourse.teacherId.name,
                teacherEmail: archivedCourse.teacherId.email,
                archivedAt: archivedCourse.archivedAt,
                archivedBy: archivedCourse.archivedBy,
                originalCreatedAt: archivedCourse.originalCreatedAt,
                students: studentsWithMarks
            }
        });
        
    } catch (error) {
        console.error('Error fetching archived course detail:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
};
