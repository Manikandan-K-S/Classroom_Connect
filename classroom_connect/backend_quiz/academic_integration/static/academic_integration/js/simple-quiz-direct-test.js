/**
 * simple-quiz-direct-test.js
 * 
 * This script is a direct test of the simple quiz creation API
 * that can be run in the browser console to check for issues.
 */

// Sample content for testing
const sampleContent = `
The water cycle, also known as the hydrologic cycle, describes the continuous movement of water on, above, and below the surface of the Earth. 
Water can change states among liquid, vapor, and ice at various places in the water cycle. The water cycle involves the following processes:

1. Evaporation: The process where water transforms from liquid to gas.
2. Transpiration: The process by which plants release water vapor into the atmosphere.
3. Condensation: The process where water vapor transforms into liquid water.
4. Precipitation: Water falling from clouds as rain, sleet, hail, or snow.
5. Infiltration: Water soaking into the soil.
6. Runoff: Water flowing over land.
`;

// Function to get CSRF token
function getCsrfToken() {
    // Try to get token from cookies
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    
    // Try to get token from DOM
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (tokenInput) {
        return tokenInput.value;
    }
    
    return null;
}

// Function to run direct API test
async function testDirectApi() {
    console.log('Starting direct API test...');
    
    // Get CSRF token
    const csrfToken = getCsrfToken();
    console.log('CSRF token available:', csrfToken ? 'Yes' : 'No');
    
    if (!csrfToken) {
        console.error('No CSRF token found. Make sure you are on a page with a CSRF token.');
        return { success: false, error: 'No CSRF token found' };
    }
    
    try {
        // Create a data URL from the sample content (similar to a file upload)
        const fileContent = 'data:text/plain;base64,' + btoa(sampleContent);
        
        // Prepare request data
        const requestData = {
            fileContent: fileContent,
            fileType: 'text/plain',
            quizTitle: 'Test Quiz via Direct API',
            quizDescription: 'A test quiz created via direct API call',
            numQuestions: 2,
            difficulty: 'easy',
            questionTypes: ['mcq_single', 'true_false'],
            durationMinutes: 10
        };
        
        console.log('Sending request to direct API endpoint...');
        
        // Make the request
        const response = await fetch('/academic_integration/api/direct-generate-questions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('Response status:', response.status, response.statusText);
        
        // Get response text
        const responseText = await response.text();
        console.log('Raw response:', responseText);
        
        // Try to parse as JSON
        try {
            const jsonResponse = JSON.parse(responseText);
            console.log('Parsed JSON response:', jsonResponse);
            return jsonResponse;
        } catch (e) {
            console.error('Failed to parse response as JSON:', e);
            return { 
                success: false, 
                error: 'Invalid JSON response', 
                rawResponse: responseText
            };
        }
    } catch (error) {
        console.error('API test failed:', error);
        return { success: false, error: error.message };
    }
}

// Function to test the regular quiz API endpoint
async function testRegularApi() {
    console.log('Starting regular API test...');
    
    // Get CSRF token
    const csrfToken = getCsrfToken();
    console.log('CSRF token available:', csrfToken ? 'Yes' : 'No');
    
    if (!csrfToken) {
        console.error('No CSRF token found. Make sure you are on a page with a CSRF token.');
        return { success: false, error: 'No CSRF token found' };
    }
    
    try {
        // Prepare request data
        const requestData = {
            content: sampleContent,
            question_count: 2,
            question_types: ['mcq_single', 'true_false'],
            difficulty: 'easy'
        };
        
        console.log('Sending request to regular API endpoint...');
        
        // Make the request
        const response = await fetch('/academic_integration/api/generate-questions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('Response status:', response.status, response.statusText);
        
        // Get response text
        const responseText = await response.text();
        console.log('Raw response:', responseText);
        
        // Try to parse as JSON
        try {
            const jsonResponse = JSON.parse(responseText);
            console.log('Parsed JSON response:', jsonResponse);
            return jsonResponse;
        } catch (e) {
            console.error('Failed to parse response as JSON:', e);
            return { 
                success: false, 
                error: 'Invalid JSON response', 
                rawResponse: responseText
            };
        }
    } catch (error) {
        console.error('API test failed:', error);
        return { success: false, error: error.message };
    }
}

// Add test functions to window for easy access in console
window.testDirectApi = testDirectApi;
window.testRegularApi = testRegularApi;

// Add test buttons to the page
function addTestButtons() {
    // Create container
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '10px';
    container.style.right = '10px';
    container.style.zIndex = '9999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '5px';
    
    // Create direct API test button
    const directButton = document.createElement('button');
    directButton.textContent = 'Test Direct API';
    directButton.style.padding = '8px';
    directButton.style.backgroundColor = '#17a2b8';
    directButton.style.color = 'white';
    directButton.style.border = 'none';
    directButton.style.borderRadius = '4px';
    directButton.style.cursor = 'pointer';
    directButton.onclick = async () => {
        const result = await testDirectApi();
        alert(`Direct API test ${result.success ? 'succeeded' : 'failed'}. Check console for details.`);
    };
    
    // Create regular API test button
    const regularButton = document.createElement('button');
    regularButton.textContent = 'Test Regular API';
    regularButton.style.padding = '8px';
    regularButton.style.backgroundColor = '#28a745';
    regularButton.style.color = 'white';
    regularButton.style.border = 'none';
    regularButton.style.borderRadius = '4px';
    regularButton.style.cursor = 'pointer';
    regularButton.onclick = async () => {
        const result = await testRegularApi();
        alert(`Regular API test ${result.success ? 'succeeded' : 'failed'}. Check console for details.`);
    };
    
    // Add buttons to container
    container.appendChild(directButton);
    container.appendChild(regularButton);
    
    // Add container to page
    document.body.appendChild(container);
    
    console.log('Test buttons added to page');
}

// Add buttons when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addTestButtons);
} else {
    addTestButtons();
}

console.log('Simple quiz direct test script loaded');
console.log('You can run tests by clicking the buttons in the top-right corner or by running:');
console.log('- testDirectApi() to test the direct API endpoint');
console.log('- testRegularApi() to test the regular API endpoint');