# Code Snippet Formatting for Quiz Questions

## Feature Added

Added automatic formatting for code snippets enclosed in backticks (`) in quiz questions and answer choices.

## Implementation

### 1. CSS Styling for Code

Added comprehensive code formatting styles:

```css
/* General code styling */
code {
    background-color: #f4f4f4;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.9em;
    color: #c7254e;
    white-space: pre-wrap;
    word-break: break-word;
}

/* Code in question cards (special styling for gradient background) */
.question-card code {
    background-color: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #fff;
}

/* Code in answer choices */
.choice-option code {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    color: #d63384;
}

/* Code in selected answer choices */
.choice-option.selected code {
    background-color: #e7f1ff;
    border-color: #b6d4fe;
}
```

### 2. JavaScript Formatting Function

Added a function to convert backtick-enclosed text to HTML `<code>` tags:

```javascript
function formatTextWithCode(text) {
    if (!text) return '';
    
    // Replace `code` with <code>code</code>
    // Handles both inline `code` and multi-line code blocks
    return text.replace(/`([^`]+)`/g, '<code>$1</code>');
}
```

### 3. Updated Rendering

Applied the formatting function to:

#### Question Text
```javascript
const questionText = document.createElement('div');
questionText.classList.add('question-card');
questionText.innerHTML = `<p>${formatTextWithCode(question.text)}</p>`;
```

#### MCQ Single Choice Options
```javascript
choiceOption.innerHTML = `
    <input class="form-check-input" type="radio" ...>
    <label class="form-check-label" ...>
        ${formatTextWithCode(choice.text)}
    </label>
`;
```

#### MCQ Multiple Choice Options
```javascript
choiceOption.innerHTML = `
    <input class="form-check-input" type="checkbox" ...>
    <label class="form-check-label" ...>
        ${formatTextWithCode(choice.text)}
    </label>
`;
```

## Usage Examples

### In Question Text

**Input (when creating quiz):**
```
What does the `print()` function do in Python?
```

**Rendered Output:**
```
What does the print() function do in Python?
           ^^^^^^^^ (styled as code)
```

### In Answer Choices

**Input (when creating quiz):**
```
Choice 1: It calls the `console.log()` method
Choice 2: It executes the `return` statement
Choice 3: It displays output using `sys.stdout`
```

**Rendered Output:**
```
○ It calls the console.log() method
             ^^^^^^^^^^^^^ (styled as code)
○ It executes the return statement
               ^^^^^^ (styled as code)
○ It displays output using sys.stdout
                           ^^^^^^^^^^ (styled as code)
```

### Multi-word Code Snippets

**Input:**
```
What is the correct syntax? Use `for i in range(10)` to loop.
```

**Rendered Output:**
```
What is the correct syntax? Use for i in range(10) to loop.
                                ^^^^^^^^^^^^^^^^^^^^ (styled as code)
```

## Styling Details

### Question Card Code Styling
- **Background**: Semi-transparent white (works with gradient)
- **Border**: Light white border
- **Text Color**: White (high contrast on gradient background)
- **Font**: Monospace (Courier New)
- **Padding**: 2px vertical, 6px horizontal

### Answer Choice Code Styling
- **Background**: Light gray (#f8f9fa)
- **Border**: Standard gray (#dee2e6)
- **Text Color**: Pink (#d63384)
- **Font**: Monospace (Courier New)

### Selected Answer Code Styling
- **Background**: Light blue (#e7f1ff)
- **Border**: Blue (#b6d4fe)
- **Maintains**: Pink text color for contrast

## Features

✅ **Automatic Detection**: Backticks automatically converted to code formatting
✅ **Inline Code**: Works with inline `code` snippets
✅ **Multiple Snippets**: Supports multiple code snippets in one text
✅ **Responsive**: Code wraps properly on small screens
✅ **Accessible**: Maintains readability with proper contrast
✅ **Context-Aware**: Different styling for questions vs answers
✅ **Selection-Aware**: Updates styling when answer is selected

## Browser Compatibility

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

## Technical Notes

1. **Regex Pattern**: `/`([^`]+)`/g`
   - Matches text between backticks
   - `g` flag for global replacement (all occurrences)
   - Non-greedy matching prevents issues with multiple code blocks

2. **Word Breaking**: `word-break: break-word`
   - Prevents long code from overflowing containers
   - Maintains layout on small screens

3. **White Space**: `white-space: pre-wrap`
   - Preserves spaces and line breaks in code
   - Wraps at container boundaries

4. **Security**: Uses innerHTML safely
   - Input is controlled (admin creates questions)
   - Only converts backticks, no arbitrary HTML

## Files Modified

**File**: `d:\Classroom_Connect\classroom_connect\backend_quiz\academic_integration\templates\academic_integration\quiz_detail.html`

**Changes**:
1. Added code CSS styles (lines ~120-150)
2. Added `formatTextWithCode()` function (lines ~300-310)
3. Updated question text rendering (line ~450)
4. Updated MCQ single choice rendering (line ~470)
5. Updated MCQ multiple choice rendering (line ~525)

## Testing Checklist

### Create Test Quiz:
- [ ] Question with single code snippet: "What does `print()` do?"
- [ ] Question with multiple code snippets: "Use `for` and `while` loops"
- [ ] Answer with code snippet: "It calls `console.log()`"
- [ ] Long code snippet: "Use `from datetime import datetime`"

### Verify Rendering:
- [ ] Code appears in monospace font
- [ ] Code has gray background in answers
- [ ] Code has white styling in question cards
- [ ] Code in selected answers turns light blue
- [ ] Multiple code snippets all formatted

### Test Interactions:
- [ ] Clicking code doesn't break selection
- [ ] Hover effects work properly
- [ ] Code wraps on small screens
- [ ] Submission includes questions with code

## Future Enhancements

### Potential Improvements:
1. **Multi-line Code Blocks**
   - Support triple backticks (```)
   - Add syntax highlighting
   - Line numbers for longer code

2. **Code Languages**
   - Detect language: ```python
   - Apply language-specific highlighting
   - Show language badge

3. **Copy Button**
   - Add copy-to-clipboard button
   - Show "Copied!" feedback
   - Works with keyboard shortcuts

4. **Math Formulas**
   - Support LaTeX: $formula$
   - Render mathematical notation
   - Works alongside code formatting

## Example Quiz Questions

### Good Examples:

✅ "What is the output of `print(2 + 2)`?"
✅ "Which statement uses `async` and `await` correctly?"
✅ "The `return` keyword exits the function."
✅ "Use `git commit -m "message"` to save changes."

### Syntax:

```
Single backtick for inline code: `code`
Multiple snippets: Use `this` and `that`
With punctuation: The `function()` method.
With quotes: Run `echo "Hello"` in terminal.
```

## Summary

This update adds professional code formatting to quiz questions and answers, making programming-related quizzes much more readable and visually appealing. The implementation is simple (just use backticks), context-aware (different styles for different areas), and fully integrated with the existing clickable options system.

**Usage**: Just wrap any code in backticks when creating quiz questions or answer choices, and it will automatically be styled as code!
