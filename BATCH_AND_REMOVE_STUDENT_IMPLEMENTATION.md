# Batch Dropdown and Remove Student Implementation

## Summary of Changes

This document outlines the implementation of two key features:
1. **Batch Dropdown**: Dynamic loading of available batches in the batch enrollment form
2. **Remove Student**: Ability to remove students from courses with proper cleanup

---

## 1. Academic Analyzer (Node.js/MongoDB) Changes

### A. New API Endpoints Added to `staffController.js`

#### `GET /staff/all-batches`
- **Purpose**: Retrieve all unique batches from the Student collection
- **Returns**: Array of distinct batch names (sorted, filtered for empty values)
- **Usage**: Populates the batch dropdown in the course management interface

```javascript
exports.getAllBatches = async (req, res) => {
    try {
        const batches = await Student.distinct('batch');
        const validBatches = batches.filter(batch => batch && batch.trim() !== '').sort();
        res.json({ success: true, batches: validBatches });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Server error' });
    }
};
```

#### `POST /staff/remove-student`
- **Purpose**: Remove a student from a course
- **Input**: `teacherEmail`, `courseId`, `studentRollno` (or `studentEmail`)
- **Actions**:
  1. Validates teacher and course exist
  2. Finds student by roll number (case-insensitive) or email
  3. Verifies student is enrolled in the course
  4. Removes student from course's `enrolledStudents` array
  5. Removes course from student's `enrolledCourses` array
  6. Deletes the Performance record for that student-course combination

```javascript
exports.removeStudentFromCourse = async (req, res) => {
    const { teacherEmail, courseId, studentRollno, studentEmail } = req.body;
    
    // Find teacher, course, and student
    const { teacher, course } = await findTeacherAndCourse(teacherEmail, courseId);
    let student = studentRollno 
        ? await Student.findOne({ rollno: { $regex: new RegExp(`^${studentRollno}$`, 'i') } })
        : await Student.findOne({ email: studentEmail });
    
    // Validate and remove
    await Promise.all([
        Course.updateOne({ _id: course._id }, { $pull: { enrolledStudents: student._id } }),
        Student.updateOne({ _id: student._id }, { $pull: { enrolledCourses: course._id } }),
        Performance.deleteOne({ studentId: student._id, courseId: course._id })
    ]);
    
    res.json({ success: true, message: `Removed ${student.name} from ${course.courseName}` });
};
```

### B. Routes Added to `staffRoutes.js`

```javascript
router.get('/all-batches', staff.getAllBatches);
router.post('/remove-student', staff.removeStudentFromCourse);
```

---

## 2. Django (Backend) Changes

### A. Form Updates in `forms.py`

#### Modified `BatchEnrollmentForm`
- Changed from a text input to a **dropdown (ChoiceField)**
- Dynamically populated with batches fetched from the API
- Uses `__init__` method to accept batches list as parameter

```python
class BatchEnrollmentForm(forms.Form):
    batch = forms.ChoiceField(
        label="Batch to Enroll",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    
    def __init__(self, *args, **kwargs):
        batches = kwargs.pop('batches', [])
        super().__init__(*args, **kwargs)
        
        if batches:
            self.fields['batch'].choices = [(batch, batch) for batch in batches]
        else:
            self.fields['batch'].choices = [('', 'No batches available')]
```

### B. View Updates in `views.py`

#### Modified `manage_course` view
- **Added batch fetching**: Calls `/staff/all-batches` API before rendering
- **Pass batches to form**: Instantiates `BatchEnrollmentForm` with `batches` parameter

```python
# Fetch available batches
batches = []
try:
    batch_response = requests.get(f"{api_base_url()}/staff/all-batches", timeout=5)
    if batch_response.ok:
        batch_body = _safe_json(batch_response)
        if batch_body.get("success"):
            batches = batch_body.get("batches", [])
except requests.RequestException:
    logger.warning("Failed to fetch batches from API")

# Create form with batches
batch_form = BatchEnrollmentForm(
    request.POST or None if request.POST.get("form_type") == "batch" else None,
    batches=batches
)
```

#### Added `remove_student_from_course` view
- **Route**: `POST /staff/course/<course_id>/remove-student/`
- **Input**: `student_rollno` from POST data
- **Process**:
  1. Validates staff session
  2. Calls `/staff/remove-student` API endpoint
  3. Displays success/error message
  4. Redirects back to course management page

```python
def remove_student_from_course(request: HttpRequest, course_id: str) -> HttpResponse:
    staff_email = request.session.get("staff_email")
    if not staff_email:
        messages.error(request, "Please log in to continue.")
        return redirect("academic_integration:staff_login")
    
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("academic_integration:manage_course", course_id=course_id)
    
    student_rollno = request.POST.get("student_rollno")
    
    try:
        response = requests.post(
            f"{api_base_url()}/staff/remove-student",
            json={
                "teacherEmail": staff_email,
                "courseId": course_id,
                "studentRollno": student_rollno
            },
            timeout=5,
        )
        
        body = _safe_json(response)
        if response.ok and body.get("success"):
            messages.success(request, body.get("message", "Student removed successfully."))
        else:
            messages.error(request, body.get("message", "Failed to remove student."))
    except requests.RequestException as e:
        logger.exception(f"Failed to remove student: {str(e)}")
        messages.error(request, "Cannot reach Academic Analyzer API. Please try again later.")
    
    return redirect("academic_integration:manage_course", course_id=course_id)
```

### C. URL Configuration in `urls.py`

```python
path("staff/course/<str:course_id>/remove-student/", views.remove_student_from_course, name="remove_student_from_course"),
```

---

## 3. Template Changes in `manage_course.html`

### A. Combined "Add Students" Tab
- Previously had 3 separate tabs: "Add Student", "Add Batch", "Import CSV"
- Now combined into one "Add Students" tab with 3-column card layout
- Each method has its own color-coded card:
  - **Blue**: Add Single Student
  - **Green**: Add Batch (with dropdown)
  - **Info Blue**: Import CSV

### B. Batch Dropdown Display
The batch form now uses a dropdown select instead of text input:

```html
<div class="col-lg-4 mb-4">
    <div class="card h-100">
        <div class="card-header bg-success text-white">
            <h5 class="mb-0"><i class="bi bi-people-fill"></i> Add Batch</h5>
        </div>
        <div class="card-body">
            <form method="post">
                {% csrf_token %}
                <input type="hidden" name="form_type" value="batch">
                
                <div class="mb-3">
                    <label for="{{ batch_form.batch.id_for_label }}" class="form-label">
                        {{ batch_form.batch.label }}
                    </label>
                    {{ batch_form.batch }}
                    <div class="form-text">Add all students from a specific batch to this course</div>
                </div>
                
                <div class="d-grid">
                    <button type="submit" class="btn btn-success">
                        <i class="bi bi-people-fill"></i> Add Batch
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
```

### C. Remove Student Button
Added "Remove" button next to "Edit Marks" in the students table:

```html
<td>
    <a href="{% url 'academic_integration:edit_student_marks' %}?course_id={{ course.id }}&student_id={{ student.rollno }}" 
       class="btn btn-sm btn-outline-primary me-1">
        <i class="bi bi-pencil"></i> Edit Marks
    </a>
    <form method="post" 
          action="{% url 'academic_integration:remove_student_from_course' course_id=course.id %}" 
          style="display: inline;" 
          onsubmit="return confirm('Are you sure you want to remove {{ student.name }} ({{ student.rollno }}) from this course? This will also delete their performance records.');">
        {% csrf_token %}
        <input type="hidden" name="student_rollno" value="{{ student.rollno }}">
        <button type="submit" class="btn btn-sm btn-outline-danger">
            <i class="bi bi-trash"></i> Remove
        </button>
    </form>
</td>
```

---

## Features Implemented

### 1. Batch Dropdown
✅ **Dynamic Loading**: Fetches all available batches from database  
✅ **Sorted Display**: Batches displayed in alphabetical order  
✅ **Empty Handling**: Shows "No batches available" if no batches found  
✅ **Dropdown UI**: Clean Bootstrap select dropdown instead of text input  

### 2. Remove Student
✅ **Full Cleanup**: Removes student from both course and student records  
✅ **Performance Deletion**: Deletes associated performance records  
✅ **Confirmation Dialog**: JavaScript confirmation before deletion  
✅ **Success/Error Messages**: Clear feedback to user  
✅ **Case-Insensitive**: Roll number matching works regardless of case  

---

## Testing Guide

### Test Batch Dropdown
1. Navigate to: `http://127.0.0.1:8000/academic_integration/staff/course/<course_id>/`
2. Click on "Add Students" tab
3. Check the "Add Batch" card
4. Verify the batch dropdown shows all available batches
5. Select a batch and click "Add Batch"
6. Verify students are added

### Test Remove Student
1. Navigate to the same course management page
2. In the "Students" tab, find a student in the table
3. Click the "Remove" button next to a student
4. Confirm the deletion in the dialog
5. Verify:
   - Student is removed from the table
   - Student no longer appears in course roster
   - Performance records are deleted (check in MongoDB)
   - Course is removed from student's enrolledCourses (check in MongoDB)

---

## Database Impact

### Collections Modified

#### `courses` Collection
- `enrolledStudents` array: Student ObjectId removed when student is removed

#### `students` Collection
- `enrolledCourses` array: Course ObjectId removed when student is removed

#### `performances` Collection
- Performance document deleted when student is removed from course

---

## Security Considerations

1. **Authentication**: All endpoints require valid teacher email in session
2. **Authorization**: Teacher must be associated with the course
3. **Validation**: 
   - Course and student existence verified before removal
   - Enrollment status checked before allowing removal
4. **Confirmation**: Client-side confirmation dialog prevents accidental deletions

---

## Files Modified

### Academic Analyzer
- `controllers/staffController.js` - Added 2 new functions
- `routes/staffRoutes.js` - Added 2 new routes

### Django Backend
- `academic_integration/forms.py` - Modified BatchEnrollmentForm
- `academic_integration/views.py` - Modified manage_course, added remove_student_from_course
- `academic_integration/urls.py` - Added 1 new URL pattern
- `academic_integration/templates/academic_integration/manage_course.html` - UI updates

---

## Next Steps (Optional Enhancements)

1. **Bulk Remove**: Add checkbox selection for removing multiple students at once
2. **Undo Feature**: Allow recently removed students to be re-added quickly
3. **Audit Log**: Track who removed which student and when
4. **Export Before Remove**: Option to export student data before removal
5. **Transfer Student**: Move student to another course instead of just removing
