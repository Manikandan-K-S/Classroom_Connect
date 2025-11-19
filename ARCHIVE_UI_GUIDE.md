# Course Archive System - UI Overview

## Dashboard Changes

### Staff Dashboard - New "Archived Courses" Card

```
┌─────────────────────────────────────────────────────────────────┐
│  Academic Analyzer Dashboard                    user@psg.tech   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐│
│  │   Create    │  │   Manage    │  │   Manage    │  │Archive │││
│  │   Course    │  │  Students   │  │   Quizzes   │  │Courses │││
│  │      📝     │  │     👥      │  │      ❓     │  │   📦   │││
│  │             │  │             │  │             │  │        │││
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘│
│                                                         ^^^      │
│                                                      NEW CARD    │
│                                                                  │
│  Your Courses                                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ Course Name      │ Code    │ Batch     │ Actions        │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │ Data Structures  │ 23MX21  │ 24MXG1    │ [Manage]      │ │
│  │ Algorithms       │ 23MX22  │ 24MXG1    │ [Manage]      │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Course Management Page - New "Archive Course" Tab

```
┌─────────────────────────────────────────────────────────────────┐
│  Manage Course: Data Structures (23MX21-24MXG1)                │
├─────────────────────────────────────────────────────────────────┤
│  [Students] [Analytics] [Add Student] [Add Batch] [Import CSV]  │
│  [Bulk Upload] [Direct Entry] [Archive Course] ← NEW TAB       │
│                                    ^^^^^^^^^^^^^^                │
└─────────────────────────────────────────────────────────────────┘

When Archive Course tab is clicked:

┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ Archive Course                                              │
├─────────────────────────────────────────────────────────────────┤
│  Archiving a course will:                                       │
│  • Remove it from your active courses dashboard                 │
│  • Hide it from quiz creation course selection                  │
│  • Preserve all student enrollment and marks data               │
│  • Make it read-only (no mark modifications allowed)            │
│  • Allow you to restore it later if needed                      │
│                                                                  │
│  Note: Archived courses can be viewed from "Archived Courses"   │
│        section in the dashboard.                                │
├─────────────────────────────────────────────────────────────────┤
│  ❌ Confirm Archive                                             │
│                                                                  │
│  Course: Data Structures (23MX21-24MXG1)                       │
│  Enrolled Students: 45                                          │
│                                                                  │
│  [🗃️ Archive This Course]  ← Confirmation required            │
└─────────────────────────────────────────────────────────────────┘
```

## Archived Courses List Page

```
┌─────────────────────────────────────────────────────────────────┐
│  📦 Archived Courses                     [← Back to Dashboard]  │
├─────────────────────────────────────────────────────────────────┤
│  ℹ️ These courses are archived and read-only. You can view     │
│     details but cannot modify marks. Click "Restore" to move    │
│     a course back to active courses.                            │
├─────────────────────────────────────────────────────────────────┤
│  Course Name      │ Code   │ ID        │ Batch │ Students │ Archived │ Actions      │
│  ─────────────────┼────────┼───────────┼───────┼──────────┼──────────┼──────────────│
│  Data Structures  │ 23MX21 │ 23MX21-.. │ 24MXG1│ 45       │ Nov 2    │ [View][Restore]│
│  Old Course 2023  │ 22CS01 │ 22CS01-.. │ 23MXG1│ 38       │ Oct 15   │ [View][Restore]│
└─────────────────────────────────────────────────────────────────┘
```

## Archived Course Detail Page

```
┌─────────────────────────────────────────────────────────────────┐
│  📦 Data Structures [ARCHIVED]  [🔄 Restore] [← Back to Archived]│
├─────────────────────────────────────────────────────────────────┤
│  ⚠️ This is an archived course. All data is read-only.         │
│     To modify marks or add students, restore the course first.  │
├─────────────────────────────────────────────────────────────────┤
│  Course Code: 23MX21              Batch: 24MXG1                 │
│  Course ID: 23MX21-24MXG1         Students: 45                  │
│                                                                  │
│  Teacher: Dr. Smith                                             │
│  Archived Date: November 2, 2025 14:30                          │
│  Archived By: teacher@psg.tech                                  │
├─────────────────────────────────────────────────────────────────┤
│  👥 Students & Performance Data                                 │
├─────────────────────────────────────────────────────────────────┤
│  # │ Roll  │ Name        │ Email         │ T1 │ T2 │ T3 │ T4 │ CA1│ CA2│ Asg│ Total│
│  ──┼───────┼─────────────┼───────────────┼────┼────┼────┼────┼────┼────┼────┼──────│
│  1 │ 24MX1 │ Student A   │ a@psg.tech    │ 8  │ 9  │ 7  │ 8  │ 9  │ 8  │ 9  │ 58.0 │
│  2 │ 24MX2 │ Student B   │ b@psg.tech    │ 7  │ 8  │ 9  │ 7  │ 8  │ 9  │ 8  │ 56.0 │
│                                                                  │
│  [← Back to Archived Courses]  [🔄 Restore This Course]        │
└─────────────────────────────────────────────────────────────────┘

Note: NO EDIT BUTTONS present - everything is read-only
```

## Quiz Creation - Archived Courses Hidden

### Before Archive:
```
Create Quiz
┌─────────────────────────────────────┐
│ Select Course:                      │
│ ┌─────────────────────────────────┐ │
│ │ Data Structures (23MX21-24MXG1) │ │  ← Visible
│ │ Algorithms (23MX22-24MXG1)      │ │
│ │ Database Systems (23MX23-24MXG1)│ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### After Archive (Data Structures archived):
```
Create Quiz
┌─────────────────────────────────────┐
│ Select Course:                      │
│ ┌─────────────────────────────────┐ │
│ │ Algorithms (23MX22-24MXG1)      │ │  ← Only active courses
│ │ Database Systems (23MX23-24MXG1)│ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

Data Structures is NOT in the list (archived)
```

## User Flow Diagrams

### Archive Flow:
```
[Dashboard] 
    ↓ (click course)
[Course Management] 
    ↓ (click "Archive Course" tab)
[Archive Warning Page]
    ↓ (click "Archive This Course")
[Confirmation Dialog: "Are you sure?"]
    ↓ (confirm)
[API: Move to ArchivedCourse collection]
    ↓ (success)
[Dashboard] (course removed)
    ↓
[Success Message: "Course archived successfully!"]
```

### View Archived Flow:
```
[Dashboard]
    ↓ (click "Archived Courses" card)
[Archived Courses List]
    ↓ (click "View" button)
[Archived Course Detail] (read-only)
    ↓ (view all data)
[All marks and students visible]
```

### Restore Flow:
```
[Archived Courses List]
    ↓ (click "Restore" button)
[Confirmation Dialog: "Restore to active?"]
    ↓ (confirm)
[API: Move back to Course collection]
    ↓ (success)
[Dashboard] (course appears again)
    ↓
[Success Message: "Course restored successfully!"]
```

## Color Coding

### Visual Indicators:
- 🟡 **Yellow/Warning**: Archive-related pages and buttons
- 🔴 **Red/Danger**: Destructive action confirmations
- 🟢 **Green/Success**: Restore actions
- 🔵 **Blue/Info**: Informational messages
- ⚫ **Gray/Secondary**: Archived/inactive status

### Icons Used:
- 📦 `bi-archive`: Archive icon
- 🔄 `bi-arrow-counterclockwise`: Restore icon
- ⚠️ `bi-exclamation-triangle`: Warning icon
- ℹ️ `bi-info-circle`: Information icon
- 👁️ `bi-eye`: View icon
- ← `bi-arrow-left`: Back button
- ✅ Badge "ARCHIVED": Status indicator

## Navigation Structure

```
Staff Dashboard
├── [Create Course]
├── [Manage Students]
├── [Manage Quizzes]
├── [Archived Courses] ← NEW
│   ├── Archived Courses List
│   │   ├── [View] → Archived Course Detail (read-only)
│   │   └── [Restore] → Back to Active Courses
└── Active Courses
    └── [Manage] → Course Management
        └── [Archive Course Tab] → Archive → Archived Courses
```

## Button States

### Archive Button:
- **Normal**: Red button "Archive This Course"
- **Hover**: Darker red with pointer cursor
- **Click**: Shows confirmation dialog
- **After confirm**: Disabled during API call

### Restore Button:
- **Normal**: Green button "Restore"
- **Hover**: Darker green with pointer cursor
- **Click**: Shows confirmation dialog
- **After confirm**: Disabled during API call

### View Button:
- **Normal**: Blue button "View"
- **Hover**: Darker blue with pointer cursor
- **Click**: Navigate to detail page

## Responsive Design

All pages are responsive with Bootstrap 5:
- Mobile: Stacked cards and tables
- Tablet: 2-column layout for cards
- Desktop: 4-column layout for quick action cards

## Accessibility

- ✅ All buttons have descriptive text
- ✅ Icons accompanied by text labels
- ✅ Color is not the only indicator (icons + text)
- ✅ Confirmation dialogs prevent accidents
- ✅ Clear feedback messages after actions
- ✅ Keyboard navigation supported
- ✅ Screen reader friendly (semantic HTML)
