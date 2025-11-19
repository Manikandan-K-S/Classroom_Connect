# Archive/Restore Course - Student Dashboard Fix

## Problem Description

**Issue**: After restoring an archived course, students could not see the course in their dashboard.

**Root Cause**: The archive/restore process was not properly maintaining the relationship between students and courses in the `Student` collection's `enrolledCourses` array.

### What was happening:

1. **During Archive**:
   - Course document was deleted from `Course` collection
   - Students' `enrolledCourses` arrays **still contained the old Course ObjectId**
   - This created "dangling references" that couldn't be populated

2. **During Restore**:
   - A **new Course document** was created with a **new ObjectId**
   - Students' `enrolledCourses` arrays **still had the old ObjectId**
   - When `Student.populate('enrolledCourses')` was called, it couldn't find the course
   - Result: Course didn't appear in student dashboard

---

## Solution Implemented

### 1. Archive Function Fix (`archiveCourse`)

**Added**: Remove course from students' `enrolledCourses` arrays when archiving

```javascript
// CRITICAL FIX: Remove course from all students' enrolledCourses arrays
// This prevents broken references when the course is deleted
const studentIds = course.enrolledStudents.map(s => s._id);
const updateResult = await Student.updateMany(
    { _id: { $in: studentIds } },
    { $pull: { enrolledCourses: course._id } }
);
console.log(`👥 Removed course from ${updateResult.modifiedCount} students' enrolledCourses arrays`);
```

**Why**: Cleans up student references before deleting the course, preventing orphaned ObjectIds.

---

### 2. Restore Function Fix (`restoreCourse`)

**Added**: Update students' `enrolledCourses` arrays with new course ObjectId

```javascript
// CRITICAL FIX: Update all students' enrolledCourses arrays with the new course ObjectId
// This is necessary because when we archived the course, the old Course document was deleted,
// and now we've created a new one with a different ObjectId
const studentIds = archivedCourse.enrolledStudents.map(s => s._id);
const updateResult = await Student.updateMany(
    { _id: { $in: studentIds } },
    { $addToSet: { enrolledCourses: restoredCourse._id } }
);
console.log(`👥 Updated ${updateResult.modifiedCount} students' enrolledCourses arrays`);
```

**Why**: Ensures students can access the restored course by updating their references to point to the new Course document.

---

## Complete Archive/Restore Flow

### Archive Process (Now Fixed):
```
1. Find course and enrolled students
2. Create performance snapshot with marks
3. Create ArchivedCourse document
4. Remove course from teacher's coursesHandled
5. ✅ NEW: Remove course from students' enrolledCourses
6. Delete Performance records
7. Delete Course document
```

### Restore Process (Now Fixed):
```
1. Find ArchivedCourse document
2. Verify teacher authorization
3. Create new Course document (new ObjectId)
4. Restore Performance records (linked to new Course._id)
5. Add course to teacher's coursesHandled
6. ✅ NEW: Add new course ObjectId to students' enrolledCourses
7. Delete ArchivedCourse document
```

---

## MongoDB Collections Affected

### Student Collection
- **Field**: `enrolledCourses` (Array of Course ObjectIds)
- **Archive**: Course ObjectId removed via `$pull`
- **Restore**: New Course ObjectId added via `$addToSet`

### Course Collection
- **Archive**: Document deleted
- **Restore**: New document created with new ObjectId

### Performance Collection
- **Archive**: All records deleted
- **Restore**: Records recreated with new courseId reference

### ArchivedCourse Collection
- **Archive**: New document created with course data + performance snapshot
- **Restore**: Document deleted after successful restoration

---

## Testing the Fix

### Test Archive:
1. Log in as a student enrolled in a course
2. Note the course is visible in dashboard
3. Staff: Archive the course
4. Student: Refresh dashboard
5. ✅ Course should disappear from student dashboard

### Test Restore:
1. Staff: Restore the archived course
2. Student: Refresh dashboard
3. ✅ Course should reappear in student dashboard
4. ✅ Click on course - should load course details
5. ✅ Marks should be preserved

### Verify Database:
```javascript
// Check student's enrolledCourses array
db.students.findOne({ rollno: "24MX112" }, { enrolledCourses: 1 })

// Check if Course ObjectId exists
db.courses.findOne({ courseId: "24MX24-24MXG1" }, { _id: 1 })

// Verify they match
```

---

## Code Changes

### File: `academic-analyzer/controllers/staffController.js`

#### Modified Functions:
1. **`archiveCourse()`** (lines ~1376-1479)
   - Added: `Student.updateMany()` to remove course from enrolledCourses

2. **`restoreCourse()`** (lines ~1481-1590)
   - Added: `Student.updateMany()` to add new course to enrolledCourses

---

## Key Learnings

### Problem Pattern:
When deleting and recreating MongoDB documents that are referenced in other documents:
- Always clean up references before deletion
- Always update references after creation
- Use `$pull` to remove ObjectIds from arrays
- Use `$addToSet` to add ObjectIds without duplicates

### MongoDB Populate:
- `populate()` only works with **valid ObjectIds** that exist in the target collection
- Dangling references (ObjectIds pointing to deleted documents) are silently ignored
- This causes data to "disappear" without throwing errors

---

## Prevention

To prevent similar issues in the future:

1. **Always consider bidirectional relationships**
   - If A references B, and B is deleted, clean up A's reference

2. **Test with student accounts**
   - Archive/restore operations affect both staff and students
   - Always test from both perspectives

3. **Use MongoDB indexes**
   - Consider adding index on `Student.enrolledCourses` for faster queries

4. **Add validation**
   - Could add pre-delete hooks to warn about dangling references
   - Could add periodic cleanup jobs to find orphaned ObjectIds

---

## Status

✅ **FIXED**: Students can now see restored courses in their dashboard
✅ **VERIFIED**: Archive properly cleans up student references
✅ **VERIFIED**: Restore properly updates student references
✅ **TESTED**: Marks are preserved during archive/restore cycle

---

## Related Files

- `academic-analyzer/controllers/staffController.js` - Archive/restore logic
- `academic-analyzer/controllers/studentController.js` - Student dashboard
- `academic-analyzer/models/ArchivedCourse.js` - Archive schema
- `ARCHIVE_SYSTEM_IMPLEMENTATION.md` - Original archive documentation
