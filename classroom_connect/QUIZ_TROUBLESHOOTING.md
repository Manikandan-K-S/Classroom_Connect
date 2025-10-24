# Quiz System Troubleshooting Guide

This guide provides solutions for common issues with the quiz system and its integration with the Academic Analyzer.

## Setup and Configuration

### 1. Environment Setup

Make sure the following environment configuration is correct:

1. The `ACADEMIC_ANALYZER_BASE_URL` is correctly set in `settings.py`
2. Database connections are properly configured
3. All required dependencies are installed

### 2. Common Issues and Resolutions

#### Quiz Answers Not Being Stored

If quiz answers are not being saved to the database:

1. **Check Choice IDs**: Run the management command to check for inconsistent choice IDs
   ```
   python manage.py check_choice_ids
   ```

2. **Verify Quiz Data**: Run the data cleanup command to identify any inconsistencies
   ```
   python manage.py cleanup_quiz_data
   ```

3. **Review JavaScript Console**: Check for any JavaScript errors in the browser console when submitting quizzes

#### "Choice with ID X does not exist for question Y" Errors

This error occurs when the quiz submission includes choice IDs that don't exist in the database. To fix:

1. **Check JavaScript**: Ensure the quiz_detail.html template is using the correct choice IDs from the database
2. **Update Quiz**: Try editing the quiz in the admin interface to refresh the choices
3. **Run Data Verification**: Use the cleanup_quiz_data command to identify problematic records

#### Tutorial Marks Not Being Updated

To ensure quiz results are properly integrated with tutorial marks:

1. **Check API Connectivity**:
   ```
   python manage.py check_api_connectivity
   ```

2. **Manually Process Quiz Results**:
   ```
   python manage.py integrate_quiz_results
   ```

3. **Verify Quiz Scores**:
   ```
   python manage.py verify_quiz_scores --fix
   ```

## Management Commands

The system includes several management commands to help diagnose and fix issues:

### `check_api_connectivity`

Tests connectivity to the Academic Analyzer API and diagnoses any issues.

```
python manage.py check_api_connectivity --verbose
```

### `fix_quiz_choices`

Creates default choices for questions that don't have any.

```
python manage.py fix_quiz_choices
```

### `repair_quiz_choices`

Fixes choice ordering issues and ensures they are sequential.

```
python manage.py repair_quiz_choices [--quiz QUIZ_ID] [--dry-run]
```

### `fix_quiz_answers`

Fixes missing answers and recalculates scores.

```
python manage.py fix_quiz_answers [--quiz QUIZ_ID] [--attempt ATTEMPT_ID] [--recalculate-scores] [--dry-run]
```

### `test_tutorial_marks`

Tests the integration with Academic Analyzer API for tutorial marks.

```
python manage.py test_tutorial_marks [--quiz QUIZ_ID] [--attempt ATTEMPT_ID] [--dry-run] [--force]
```

### `verify_quiz_scores`

Verifies that quiz scores are calculated correctly.

```
python manage.py verify_quiz_scores [--quiz QUIZ_ID] [--fix]
```

### `fix_quiz_dates`

Fixes timezone issues with quiz dates.

```
python manage.py fix_quiz_dates [--dry-run]
```

## JavaScript Debugging

If you encounter issues with the quiz submission process, you can enable additional debugging by adding this to your JavaScript console:

```javascript
sessionStorage.setItem('QUIZ_DEBUG', 'true');
```

This will output additional debugging information to the console when interacting with quizzes.

## Common Error Messages and Solutions

### "Invalid filter: 'modulo'"

**Solution**: Ensure the `math_filters.py` file in `academic_integration/templatetags/` is correctly installed and contains the `modulo` filter function.

### "Choice with ID X does not exist for question Y"

**Solution**: Run the `check_choice_ids` management command to identify issues, then edit the quiz to recreate the choices or fix the JavaScript to use correct IDs.

### "Cannot reach Academic Analyzer API"

**Solution**: Run the `check_api_connectivity` command to diagnose the issue, ensure the API server is running, and that the URL is correctly configured.

## Database Schema Diagram

For reference, here's how the quiz-related models are related:

```
Quiz
├── questions (Question)
│   └── choices (Choice)
└── attempts (QuizAttempt)
    └── answers (QuizAnswer)
```

Remember to check the logs for detailed error information when troubleshooting issues.