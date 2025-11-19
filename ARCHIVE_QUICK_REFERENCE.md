# Course Archive System - Quick Reference

## 🎯 What It Does

Archives old/completed courses to keep dashboard clean while preserving all data for future reference.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Archive Course** | Move course to separate collection with all data |
| **View Archived** | Browse and view all archived courses (read-only) |
| **Restore Course** | Move course back to active with all data intact |
| **Auto-Hide** | Archived courses hidden from quiz creation |
| **Data Preservation** | All marks, students, and enrollment preserved |

## 🔗 Quick Links

| Page | URL |
|------|-----|
| Dashboard | http://127.0.0.1:8000/academic_integration/staff/dashboard/ |
| Archived Courses | http://127.0.0.1:8000/academic_integration/staff/archived-courses/ |
| Archive Course | Course page → "Archive Course" tab |

## 📋 Common Tasks

### To Archive a Course:
1. Go to course management page
2. Click "Archive Course" tab
3. Click "Archive This Course"
4. Confirm action

### To View Archived Courses:
1. From dashboard, click "Archived Courses" card
2. Click "View" next to any course

### To Restore a Course:
1. Go to Archived Courses list
2. Click "Restore" button
3. Confirm action

## 🔒 What Changes After Archive

| Aspect | Before Archive | After Archive |
|--------|---------------|---------------|
| Dashboard | ✅ Visible | ❌ Hidden |
| Quiz Creation | ✅ Available | ❌ Not available |
| Mark Entry | ✅ Editable | ❌ Read-only |
| Student Data | ✅ In Course | ✅ In ArchivedCourse |
| Restore | ❌ N/A | ✅ Available |

## 💾 Data Stored in Archive

- ✅ Course name, code, ID, batch
- ✅ Teacher information
- ✅ All enrolled students
- ✅ Complete marks history (Tutorials, CA, Assignment)
- ✅ Total marks for each student
- ✅ Archive timestamp and archived by

## ⚡ Quick Checks

### Is course archived?
- Check: Not in active courses dashboard
- Check: Appears in "Archived Courses" list
- Check: Not in quiz course dropdown

### Can I edit archived course marks?
- ❌ No, archived courses are read-only
- ✅ Restore first to enable editing

### Will I lose data when archiving?
- ❌ No, all data is preserved
- ✅ Can restore anytime with all data intact

## 🚨 Important Notes

⚠️ **Archive removes course from active dashboard** - Expected behavior to keep dashboard clean

⚠️ **Archived courses are read-only** - Must restore to make changes

⚠️ **Cannot restore if same courseId exists** - Ensure no duplicate course IDs

✅ **All data is preserved** - Complete performance snapshot saved

✅ **Can restore anytime** - No time limit on restoration

## 📊 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/staff/archive-course` | POST | Archive a course |
| `/staff/restore-course` | POST | Restore archived course |
| `/staff/archived-courses` | GET | List all archived courses |
| `/staff/archived-course-detail` | GET | Get archived course details |

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Course not disappearing | Refresh page, check API is running |
| Can't see archived courses | Check logged in as correct teacher |
| Restore fails | Check no duplicate courseId exists |
| Marks missing | Contact admin, check MongoDB |

## 📞 Support

- Check: `ARCHIVE_SYSTEM_IMPLEMENTATION.md` for technical details
- Check: `ARCHIVE_TESTING_GUIDE.md` for testing procedures
- Check: `ARCHIVE_UI_GUIDE.md` for UI walkthrough

## 🎓 Use Cases

1. **End of Semester**: Archive completed courses to clean up dashboard
2. **Course Redesign**: Archive old version before creating new one
3. **Historical Reference**: Keep data accessible for future reference
4. **Mistake Recovery**: Restore if accidentally archived wrong course

## ⏱️ When to Archive

✅ **Good times to archive:**
- End of semester/academic year
- Course completed and graded
- No more marks to enter
- Want to clean up dashboard

❌ **Don't archive if:**
- Still entering/updating marks
- Students actively enrolled
- Need course in quiz creation
- Semester still ongoing

## 🎯 Best Practices

1. ✅ Archive at end of semester
2. ✅ Verify all marks entered before archiving
3. ✅ Download marks backup before archiving (optional)
4. ✅ Use descriptive course names for easy identification
5. ✅ Keep archived courses list organized
6. ✅ Restore only when needed to avoid clutter

## 📈 Benefits

| Benefit | Impact |
|---------|--------|
| **Clean Dashboard** | Only active courses visible |
| **Faster Queries** | Less data to search through |
| **Better Organization** | Separate active vs historical |
| **Data Preservation** | Historical records maintained |
| **Flexibility** | Easy restore when needed |
| **Quiz Management** | Only relevant courses shown |

---

**Version**: 1.0  
**Last Updated**: November 2, 2025  
**Status**: ✅ Production Ready
