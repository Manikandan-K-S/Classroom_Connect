/**
 * Quiz datetime helpers
 * Provides utilities for handling timezone-aware dates in quiz forms
 */

// Format a date in ISO format with timezone info
function formatDateTimeWithTimezone(dateObject) {
    if (!dateObject) return '';
    
    // Ensure we have a Date object
    const date = (dateObject instanceof Date) ? dateObject : new Date(dateObject);
    
    // Format as YYYY-MM-DDThh:mm (format expected by datetime-local inputs)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Parse an ISO date string with timezone info
function parseISODateWithTimezone(dateString) {
    if (!dateString) return null;
    return new Date(dateString);
}

// Add timezone info to form date inputs before submission
function prepareQuizFormDatesForSubmission(formData) {
    // Get form elements
    const startDate = formData.get('start_date');
    const completeByDate = formData.get('complete_by_date');
    
    // If dates are present, ensure they include timezone info
    if (startDate) {
        const startDateTime = new Date(startDate);
        formData.set('start_date', startDateTime.toISOString());
    }
    
    if (completeByDate) {
        const completeByDateTime = new Date(completeByDate);
        formData.set('complete_by_date', completeByDateTime.toISOString());
    }
    
    return formData;
}

// Populate timezone info display elements
function displayTimezoneInfo() {
    const tzElements = document.querySelectorAll('.timezone-info');
    if (tzElements.length === 0) return;
    
    const now = new Date();
    const timezoneName = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const timezoneOffset = now.getTimezoneOffset();
    const offsetHours = Math.abs(Math.floor(timezoneOffset / 60));
    const offsetMinutes = Math.abs(timezoneOffset % 60);
    const offsetSign = timezoneOffset > 0 ? '-' : '+';
    const offsetFormatted = `${offsetSign}${String(offsetHours).padStart(2, '0')}:${String(offsetMinutes).padStart(2, '0')}`;
    
    const tzInfo = `${timezoneName} (UTC${offsetFormatted})`;
    
    tzElements.forEach(element => {
        element.textContent = tzInfo;
    });
}

// Initialize timezone information when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    displayTimezoneInfo();
    
    // Add timezone info to quiz form submission
    const quizForms = document.querySelectorAll('form.quiz-form');
    quizForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const preparedData = prepareQuizFormDatesForSubmission(formData);
            
            // Submit the form with the prepared data
            // This could be replaced with a fetch API call if using AJAX
            const originalSubmit = HTMLFormElement.prototype.submit;
            originalSubmit.call(form);
        });
    });
});