# Course Archive System - Testing Guide

## Prerequisites
✅ Academic Analyzer API running on http://localhost:5000
✅ Django server running on http://127.0.0.1:8000

## Test Scenarios

### Scenario 1: Archive a Course

**Steps:**
1. Login as staff at http://127.0.0.1:8000/academic_integration/staff/login/
2. Navigate to Dashboard
3. Click on any course (e.g., http://127.0.0.1:8000/academic_integration/staff/course/23MX21-24MXG1/)
4. Click on the **"Archive Course"** tab (last tab)
5. Read the warning information:
   - ✓ Removes from active dashboard
   - ✓ Hides from quiz creation
   - ✓ Preserves all data
   - ✓ Makes read-only
   - ✓ Allows restore later
6. Click **"Archive This Course"** button
7. Confirm in the popup dialog
8. Verify redirect to Dashboard
9. Verify success message shown
10. **Verify course is NO LONGER in the active courses list**

### Scenario 2: View Archived Courses

**Steps:**
1. From Dashboard, locate the **"Archived Courses"** card (4th card with archive icon)
2. Click on it to navigate to http://127.0.0.1:8000/academic_integration/staff/archived-courses/
3. Verify the archived course appears in the list with:
   - Course Name
   - Course Code
   - Course ID
   - Batch
   - Student count
   - Archive date
4. Note the **"ARCHIVED"** status indicator

### Scenario 3: View Archived Course Details

**Steps:**
1. From Archived Courses list, click **"View"** button
2. Verify detailed page shows:
   - ✓ Course information (code, ID, batch)
   - ✓ Teacher name
   - ✓ Archive date and "Archived by" info
   - ✓ Warning banner about read-only status
   - ✓ Complete student list
   - ✓ All marks displayed (Tutorial 1-4, CA 1-2, Assignment, Total)
3. Verify **NO EDIT BUTTONS** present (read-only)
4. Check students are sorted by roll number

### Scenario 4: Verify Hidden from Quiz Creation

**Steps:**
1. Navigate to Quiz Management: http://127.0.0.1:8000/academic_integration/staff/quizzes/
2. Click **"Create Quiz"**
3. In the "Select Course" dropdown
4. **Verify archived course is NOT listed**
5. Only active courses should appear

### Scenario 5: Restore a Course

**Steps:**
1. Navigate to Archived Courses list
2. Click **"Restore"** button next to the archived course
3. Confirm in the popup dialog
4. Verify redirect to Dashboard
5. Verify success message shown
6. **Verify course is NOW BACK in active courses list**
7. Navigate to Quiz Creation
8. **Verify course is NOW available in course selection dropdown**
9. Open the restored course management page
10. Verify all marks and students are intact

### Scenario 6: Verify Archive is Deleted After Restore

**Steps:**
1. After restoring a course (Scenario 5)
2. Navigate to Archived Courses list
3. **Verify the restored course is NO LONGER in archived list**

### Scenario 7: Multiple Archives

**Steps:**
1. Archive 2-3 different courses
2. Navigate to Archived Courses list
3. Verify all archived courses appear
4. Verify each has correct student count
5. Verify sorted by archive date (newest first)

### Scenario 8: Restore Button from Detail View

**Steps:**
1. Navigate to an archived course detail page
2. Click **"Restore This Course"** button at top right
3. Confirm restoration
4. Verify redirect and success message
5. Verify course back in active list

## Edge Cases to Test

### Edge Case 1: Archive Course with No Students
**Expected:** Should archive successfully, show 0 students in archived list

### Edge Case 2: Try to Restore Duplicate Course ID
**Expected:** Should show error if course with same ID already exists
**Steps to Test:**
1. Archive course A
2. Create new course with same courseId
3. Try to restore archived course A
4. Should fail with error message

### Edge Case 3: Different Teachers
**Expected:** Teacher A cannot see Teacher B's archived courses
**Steps to Test:**
1. Login as Teacher A, archive a course
2. Logout
3. Login as Teacher B
4. Navigate to Archived Courses
5. Should NOT see Teacher A's archived course

### Edge Case 4: Archive Course with Marks
**Steps:**
1. Ensure course has students with various marks entered
2. Archive the course
3. View archived course detail
4. Verify ALL marks are preserved and visible
5. Restore the course
6. Open course management
7. Verify all marks still intact in direct entry and analytics

## Verification Points

### After Archive:
- [ ] Course removed from `Course` collection in MongoDB
- [ ] Course removed from teacher's `coursesHandled` array
- [ ] Performance records deleted from `Performance` collection
- [ ] New document created in `ArchivedCourse` collection
- [ ] All student data in `performanceSnapshot`
- [ ] `archivedAt` date set correctly
- [ ] `archivedBy` email recorded

### After Restore:
- [ ] Course recreated in `Course` collection
- [ ] Course added back to teacher's `coursesHandled` array
- [ ] Performance records restored in `Performance` collection
- [ ] Archived document deleted from `ArchivedCourse` collection
- [ ] All marks match original values
- [ ] Original creation date preserved

## MongoDB Verification (Optional)

If you have MongoDB access, verify data structure:

```javascript
// Check ArchivedCourse collection
db.archivedcourses.find({}).pretty()

// Verify structure
{
  courseId: "23MX21-24MXG1",
  courseName: "Course Name",
  courseCode: "23MX21",
  batch: "24MXG1",
  teacherId: ObjectId("..."),
  teacherEmail: "teacher@psg.tech",
  enrolledStudents: [ObjectId("..."), ...],
  archivedAt: ISODate("..."),
  archivedBy: "teacher@psg.tech",
  originalCreatedAt: ISODate("..."),
  performanceSnapshot: [
    {
      studentId: ObjectId("..."),
      marks: {
        tutorial1: 8.5,
        tutorial2: 9.0,
        // ...
      },
      totalMarks: 56.5
    },
    // ...
  ]
}
```

## User Experience Checklist

- [ ] Clear visual indicators (badges, colors) for archived status
- [ ] Confirmation dialogs prevent accidental actions
- [ ] Success/error messages provide feedback
- [ ] Navigation flows logically (back buttons work)
- [ ] Read-only archived courses clearly indicated
- [ ] Active courses remain unaffected
- [ ] Dashboard remains clean and organized

## Performance Testing

1. **Archive with Large Course:**
   - Test with course having 100+ students
   - Verify archiving completes within reasonable time
   - Check all performance data preserved

2. **Restore Large Course:**
   - Restore course with 100+ students
   - Verify restoration completes successfully
   - Check all marks restored correctly

## Troubleshooting

### Issue: Course not disappearing from dashboard after archive
**Solution:** Refresh the page, check API response in browser console

### Issue: Archived course not showing in archived list
**Solution:** Check MongoDB ArchivedCourse collection, verify teacher email matches

### Issue: Marks missing after restore
**Solution:** Check performanceSnapshot in archived document, verify restore API logs

### Issue: 403 Forbidden error
**Solution:** Check CSRF token, verify user is logged in as staff

### Issue: 404 Not Found on archive
**Solution:** Verify Academic Analyzer API is running, check network tab

## Success Criteria

✅ All test scenarios pass without errors
✅ Data integrity maintained (no data loss)
✅ Clear separation between active and archived
✅ Smooth archive and restore workflows
✅ Appropriate access control enforced
✅ User-friendly interface with clear feedback
✅ No impact on existing functionality

## Report Template

After testing, report status:

```
Course Archive System Test Report
Date: [DATE]
Tester: [NAME]

Scenario 1 (Archive): ✅ PASS / ❌ FAIL
Scenario 2 (View List): ✅ PASS / ❌ FAIL
Scenario 3 (View Detail): ✅ PASS / ❌ FAIL
Scenario 4 (Quiz Filter): ✅ PASS / ❌ FAIL
Scenario 5 (Restore): ✅ PASS / ❌ FAIL
Scenario 6 (Archive Deleted): ✅ PASS / ❌ FAIL
Scenario 7 (Multiple): ✅ PASS / ❌ FAIL
Scenario 8 (Restore from Detail): ✅ PASS / ❌ FAIL

Edge Cases:
- No Students: ✅ PASS / ❌ FAIL
- Duplicate ID: ✅ PASS / ❌ FAIL
- Different Teachers: ✅ PASS / ❌ FAIL
- Marks Preservation: ✅ PASS / ❌ FAIL

Overall Status: ✅ READY FOR PRODUCTION / ⚠️ NEEDS FIXES

Notes:
[Any issues or observations]
```
