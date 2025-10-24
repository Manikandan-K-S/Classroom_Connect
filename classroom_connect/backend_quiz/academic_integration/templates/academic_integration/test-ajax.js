/**
 * Test file for debugging Ajax request issues
 * 
 * Instructions:
 * 1. Open browser console when using the quiz creation page
 * 2. Check for any JavaScript errors that might prevent form submission
 * 3. Verify that the CSRF token is being properly included in requests
 * 4. Confirm that the server is receiving the requests (check Django logs)
 */

function testAjaxRequest() {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    console.log('CSRF Token:', csrfToken);
    
    // Simple test data
    const testData = {
        test: true,
        timestamp: new Date().toISOString()
    };
    
    // Test fetch API
    console.log('Testing fetch API...');
    fetch('/test-endpoint/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(testData)
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        return response.text();
    })
    .then(text => {
        console.log('Response body:', text);
    })
    .catch(error => {
        console.error('Fetch error:', error);
    });
}

// Instructions for form debugging
console.log(`
=== Quiz Form Submission Debugging Guide ===
1. Check that the form has a valid 'id' attribute
2. Verify that all required fields have values
3. Ensure there's at least one question added
4. Check that MCQ questions have at least one correct answer
5. Look for any JavaScript errors in the console
6. Verify the CSRF token is available
7. Check server logs for any backend errors
`);