# Quiz Performance Page - Enrolled Students Tracking

## Feature Added

Added tracking and display of enrolled students who haven't taken the quiz yet on the quiz performance page.

## Implementation

### 1. **Backend Changes** (`views_quiz_grading.py`)

#### Added Imports
```python
import requests
from .views import api_base_url, _safe_json
```

#### Updated `quiz_student_performance` Function
```python
# Get enrolled students who haven't taken the quiz
students_not_taken = []
total_enrolled = 0

if quiz.course_id:
    try:
        # Get course roster from Academic Analyzer
        course_response = requests.get(
            f"{api_base_url()}/staff/course-detail",
            params={"courseId": quiz.course_id},
            timeout=5,
        )
        
        if course_response.ok:
            course_data = _safe_json(course_response)
            if course_data.get("success"):
                enrolled_students = course_data.get("students", [])
                total_enrolled = len(enrolled_students)
                
                # Get list of students who have taken the quiz
                students_taken = set(attempt.user.username for attempt in attempts)
                
                # Filter students who haven't taken the quiz
                students_not_taken = [
                    student for student in enrolled_students 
                    if student.get('rollno') not in students_taken
                ]
    except Exception as e:
        logger.warning(f"Failed to get course roster: {str(e)}")
```

#### Added Context Variables
- `students_not_taken`: List of students who haven't taken the quiz
- `total_enrolled`: Total number of students enrolled in the course
- `not_taken_count`: Number of students who haven't taken the quiz

### 2. **Frontend Changes** (`quiz_student_performance.html`)

#### Updated Statistics Cards (5 cards now)

**Original 4 cards:**
- Total Attempts
- Average Score
- Passing Rate
- Needs Grading

**New 5 cards:**
- **Total Attempts** (now shows "out of X enrolled")
- **Average Score**
- **Passing Rate**
- **Needs Grading**
- **Yet to Take** (NEW - clickable card)

#### New "Yet to Take" Card
```html
<div class="card shadow-sm h-100 bg-info-subtle" style="cursor: pointer;" 
     onclick="toggleNotTakenList()">
    <div class="card-body text-center">
        <h6 class="text-uppercase text-muted">Yet to Take</h6>
        <h2>{{ not_taken_count }}</h2>
        <p class="text-info mb-0 small">
            <i class="bi bi-arrow-down-circle"></i> Click to view list
        </p>
    </div>
</div>
```

Features:
- Shows count of students who haven't taken the quiz
- Light blue background (`bg-info-subtle`) if count > 0
- Clickable to expand/collapse the student list
- Shows "Click to view list" instruction

#### Collapsible Student List Section
```html
<div id="not-taken-section" class="card shadow-sm mb-4" style="display: none;">
    <div class="card-header bg-info-subtle">
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
                <i class="bi bi-exclamation-circle-fill text-info"></i>
                Students Who Haven't Taken the Quiz ({{ not_taken_count }})
            </h5>
            <button class="btn btn-sm btn-outline-secondary" onclick="toggleNotTakenList()">
                <i class="bi bi-x-lg"></i> Close
            </button>
        </div>
    </div>
    <div class="card-body">
        <div class="row">
            {% for student in students_not_taken %}
            <div class="col-md-4 mb-3">
                <div class="card border-info">
                    <div class="card-body py-2">
                        <div class="d-flex align-items-center">
                            <div class="me-2">
                                <i class="bi bi-person-circle text-info"></i>
                            </div>
                            <div>
                                <div class="fw-medium">{{ student.name }}</div>
                                <div class="small text-muted">{{ student.rollno }}</div>
                                {% if student.email %}
                                <div class="small text-muted">{{ student.email }}</div>
                                {% endif %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
```

Features:
- Initially hidden (`display: none`)
- Shows student cards in 3-column grid (responsive)
- Each card displays:
  - Person icon
  - Student name
  - Roll number
  - Email (if available)
- Header with close button
- Info-themed styling (light blue)

#### JavaScript Function
```javascript
function toggleNotTakenList() {
    const section = document.getElementById('not-taken-section');
    if (section) {
        if (section.style.display === 'none' || section.style.display === '') {
            section.style.display = 'block';
            // Smooth scroll to the section
            section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            section.style.display = 'none';
        }
    }
}
```

Features:
- Toggles visibility of student list
- Smooth scroll when opening
- Can be triggered by clicking card or close button

## User Experience

### Before
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Total     │   Average   │   Passing   │   Needs     │
│  Attempts   │    Score    │    Rate     │  Grading    │
│     15      │    75.2%    │    80.0%    │      2      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### After
```
┌────────────┬───────────┬───────────┬───────────┬────────────┐
│   Total    │  Average  │  Passing  │   Needs   │  Yet to    │
│  Attempts  │   Score   │   Rate    │  Grading  │   Take     │
│     15     │   75.2%   │   80.0%   │     2     │     5      │
│ of 20      │           │  12/15    │  Manual   │  Click to  │
│ enrolled   │           │  passed   │  grading  │  view list │
└────────────┴───────────┴───────────┴───────────┴────────────┘
                                                       ↓ Click
┌──────────────────────────────────────────────────────────────┐
│ Students Who Haven't Taken the Quiz (5)           [X] Close  │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 👤 John Doe │  │ 👤 Jane S.  │  │ 👤 Bob J.   │         │
│  │ 21PW01      │  │ 21PW02      │  │ 21PW05      │         │
│  │ john@psg... │  │ jane@psg... │  │ bob@psg...  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │ 👤 Alice W. │  │ 👤 Charlie  │                          │
│  │ 21PW08      │  │ 21PW12      │                          │
│  │ alice@psg.. │  │ charlie@... │                          │
│  └─────────────┘  └─────────────┘                          │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Quiz Performance Page Load
    ↓
Check if quiz.course_id exists
    ↓ YES
GET /staff/course-detail?courseId={course_id}
    ↓
Academic Analyzer returns enrolled students
    ↓
Get list of students who attempted quiz (from QuizAttempt)
    ↓
Filter: enrolled_students NOT IN attempted_students
    ↓
Display count on "Yet to Take" card
    ↓
User clicks card
    ↓
Show collapsible list of students
```

## Edge Cases Handled

### 1. **Quiz Not Linked to Course**
```python
if quiz.course_id:
    # Only try to fetch if course_id exists
```
- If no course_id: Shows 0 for "Yet to Take"
- Card is not clickable

### 2. **Academic Analyzer API Down**
```python
try:
    course_response = requests.get(...)
except Exception as e:
    logger.warning(f"Failed to get course roster: {str(e)}")
```
- Falls back to showing 0 students
- Logs warning for debugging
- Page still loads successfully

### 3. **All Students Took Quiz**
```html
{% if not_taken_count > 0 %}
    <!-- Show clickable card -->
{% else %}
    <p class="text-muted mb-0 small">All students attempted</p>
{% endif %}
```
- Shows "All students attempted" message
- Card is not clickable
- No collapsible section rendered

### 4. **No Attempts Yet**
- "Total Attempts" shows 0
- "Yet to Take" shows full enrollment count
- List shows all enrolled students

## Visual Design

### Color Scheme
- **Info Blue**: Used for "Yet to Take" card and student list
  - Card background: `bg-info-subtle` (light blue)
  - Text: `text-info` (blue)
  - Icon: `text-info`
  - Borders: `border-info`

### Icons
- 📊 **bi-arrow-down-circle**: "Click to view list" indicator
- ⚠️ **bi-exclamation-circle-fill**: "Students Who Haven't Taken" header
- 👤 **bi-person-circle**: Student icon in list
- ❌ **bi-x-lg**: Close button

### Responsive Design
- Cards: Adjusts from 5 columns (desktop) to stacked (mobile)
- Student list: 3 columns (desktop) → 2 columns (tablet) → 1 column (mobile)
- Uses Bootstrap grid: `col-md-4`

## Benefits

### For Teachers/Staff:
1. ✅ **Quick Overview**: See at a glance how many students haven't taken the quiz
2. ✅ **Easy Identification**: Click to see exactly who needs to take it
3. ✅ **Follow-up**: Can easily contact students who haven't attempted
4. ✅ **Participation Tracking**: Monitor quiz participation rate
5. ✅ **Proactive Reminders**: Know who to send reminders to

### For Students:
- Teachers can proactively reach out with reminders
- Better communication about pending quizzes

## Testing Checklist

### Scenarios to Test:

#### ✅ Normal Case: Some students haven't taken quiz
- [ ] Card shows correct count
- [ ] Clicking card expands student list
- [ ] All not-taken students appear in list
- [ ] Student info (name, roll no, email) displays correctly
- [ ] Close button collapses the list

#### ✅ All Students Took Quiz
- [ ] Card shows 0
- [ ] Message says "All students attempted"
- [ ] Card is not clickable
- [ ] No collapsible section rendered

#### ✅ No Students Took Quiz Yet
- [ ] "Yet to Take" shows full enrollment count
- [ ] List shows all enrolled students
- [ ] "Total Attempts" shows 0

#### ✅ Quiz Not Linked to Course
- [ ] "Yet to Take" shows 0 or N/A
- [ ] "Total Attempts" shows count without "of X enrolled"
- [ ] No errors in console

#### ✅ Academic Analyzer API Down
- [ ] Page loads successfully
- [ ] Shows 0 for "Yet to Take"
- [ ] Warning logged in backend
- [ ] No errors shown to user

#### ✅ Student Info Edge Cases
- [ ] Student with missing email: Email not shown
- [ ] Student with long name: Wraps properly
- [ ] Special characters in name: Displays correctly

#### ✅ Responsive Design
- [ ] Desktop: 5 cards in one row
- [ ] Tablet: Cards wrap appropriately
- [ ] Mobile: Cards stack vertically
- [ ] Student list: 3 columns → 2 → 1

## API Requirements

### Academic Analyzer Endpoint
```
GET /staff/course-detail?courseId={courseId}
```

**Expected Response:**
```json
{
    "success": true,
    "students": [
        {
            "rollno": "21PW01",
            "name": "John Doe",
            "email": "john@psgtech.ac.in"
        },
        ...
    ]
}
```

**Required Fields:**
- `rollno` (string): Used to match with quiz attempts
- `name` (string): Student's full name
- `email` (string, optional): Student's email

## Future Enhancements

### 1. **Send Reminder Emails**
```html
<button class="btn btn-primary" onclick="sendReminders()">
    <i class="bi bi-envelope"></i> Send Reminder to All
</button>
```

### 2. **Export Not-Taken List**
```javascript
function exportNotTakenList() {
    // Export students who haven't taken quiz to CSV
}
```

### 3. **Deadline Warning**
```html
{% if quiz.complete_by_date and days_remaining < 3 %}
<div class="alert alert-warning">
    Deadline approaching! {{ not_taken_count }} students still need to take this quiz.
</div>
{% endif %}
```

### 4. **Individual Reminders**
```html
<a href="mailto:{{ student.email }}?subject=Reminder: Quiz Pending">
    <i class="bi bi-envelope"></i> Send Reminder
</a>
```

### 5. **Show Last Login Time**
```html
<div class="small text-muted">
    Last seen: {{ student.last_login|timesince }} ago
</div>
```

## Files Modified

1. **`views_quiz_grading.py`**
   - Added imports for `requests`, `api_base_url`, `_safe_json`
   - Updated `quiz_student_performance` function
   - Added logic to fetch enrolled students from Academic Analyzer
   - Added filtering logic for students who haven't taken quiz

2. **`quiz_student_performance.html`**
   - Updated statistics cards layout (4 → 5 cards)
   - Added "Yet to Take" card with click functionality
   - Added collapsible student list section
   - Added `toggleNotTakenList()` JavaScript function
   - Updated responsive design classes

## Summary

This feature provides teachers with visibility into quiz participation by:
- Showing how many enrolled students haven't taken the quiz
- Providing a clickable interface to view the list of students
- Displaying student information for easy follow-up
- Integrating seamlessly with existing performance metrics

The implementation is robust, handling edge cases like API failures and missing data gracefully, while providing a smooth user experience with collapsible sections and responsive design.
