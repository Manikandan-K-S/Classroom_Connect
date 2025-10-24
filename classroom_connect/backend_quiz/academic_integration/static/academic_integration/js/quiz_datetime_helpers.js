/**
 * Quiz Datetime Helper Functions 
 * These functions ensure that dates are properly handled when creating/editing quizzes
 * Prevents "Quiz not available" issues due to timezone mismatches
 */

/**
 * Formats a date input for Django's backend to ensure timezone consistency
 * @param {string} dateValue - The value from a datetime-local input
 * @returns {string|null} - ISO formatted date string with timezone info or null if input is empty
 */
function formatDateForBackend(dateValue) {
    if (!dateValue) return null;
    
    // Convert the local datetime string to a Date object
    const dateObj = new Date(dateValue);
    
    // Check if date is valid
    if (isNaN(dateObj)) {
        console.error("Invalid date value:", dateValue);
        return null;
    }
    
    // Get ISO string with timezone info
    return dateObj.toISOString();
}

/**
 * Prepares quiz data with proper date formatting before submission
 * @param {Object} quizData - The raw quiz data object
 * @returns {Object} - Quiz data with properly formatted dates
 */
function prepareQuizDataWithFormattedDates(quizData) {
    // Make a copy of the data
    const formattedData = { ...quizData };
    
    // Format start date
    if (quizData.start_date) {
        formattedData.start_date = formatDateForBackend(quizData.start_date);
    }
    
    // Format complete by date
    if (quizData.complete_by_date) {
        formattedData.complete_by_date = formatDateForBackend(quizData.complete_by_date);
    }
    
    return formattedData;
}

/**
 * Displays the current server time vs local time to help diagnose timezone issues
 * @param {HTMLElement} container - The element to display the time information in
 */
function displayTimezoneInfo(container) {
    if (!container) return;
    
    // Get local time
    const localTime = new Date();
    const localTimeStr = localTime.toString();
    const localOffset = localTime.getTimezoneOffset();
    const localOffsetHours = Math.abs(Math.floor(localOffset / 60));
    const localOffsetMinutes = Math.abs(localOffset % 60);
    const localOffsetSign = localOffset <= 0 ? '+' : '-';
    const localOffsetFormatted = `${localOffsetSign}${String(localOffsetHours).padStart(2, '0')}:${String(localOffsetMinutes).padStart(2, '0')}`;
    
    // Create info box
    const infoBox = document.createElement('div');
    infoBox.className = 'alert alert-info mt-3';
    infoBox.innerHTML = `
        <h6 class="alert-heading"><i class="bi bi-clock"></i> Timezone Information</h6>
        <p class="mb-1"><strong>Your local time:</strong> ${localTimeStr}</p>
        <p class="mb-0"><strong>Your timezone offset:</strong> UTC${localOffsetFormatted}</p>
        <hr>
        <p class="mb-0 small">Quiz availability is based on server time (UTC). Please set your dates accordingly.</p>
    `;
    
    container.appendChild(infoBox);
}