/**
 * Gemini Quiz Generator Debug Helper
 * 
 * This script loads after the main quiz generation page loads and ensures
 * that the DirectGeminiQuizGenerator is properly loaded and functioning.
 * If the main script fails to load, this script will attempt to reload it
 * and display an error message.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Gemini Quiz Generator Debug Helper loaded');
    
    // Check if DirectGeminiQuizGenerator is loaded properly
    if (typeof DirectGeminiQuizGenerator === 'undefined') {
        console.error('ERROR: DirectGeminiQuizGenerator not loaded!');
        
        // Add error message to page
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.innerHTML = `
            <strong>Error:</strong> Quiz generator scripts failed to load properly. 
            <button class="btn btn-sm btn-outline-danger" onclick="location.reload()">Reload Page</button>
        `;
        
        // Insert at the top of the page
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(errorDiv, container.firstChild);
        } else {
            document.body.insertBefore(errorDiv, document.body.firstChild);
        }
        
        // Try to reload the script
        const script = document.createElement('script');
        script.src = '/static/academic_integration/js/directGeminiQuizGenerator.js?_=' + new Date().getTime();
        script.onload = function() {
            console.log('DirectGeminiQuizGenerator reloaded successfully');
            // Add success message
            const successDiv = document.createElement('div');
            successDiv.className = 'alert alert-success';
            successDiv.textContent = 'Scripts reloaded successfully. Please try again.';
            errorDiv.after(successDiv);
        };
        document.head.appendChild(script);
    } else {
        console.log('DirectGeminiQuizGenerator is loaded correctly');
    }
    
    // Add a console method to test the quiz generation API
    window.testQuizApi = async function(sample = true) {
        try {
            console.log('Testing quiz generation API...');
            
            let fileContent, fileType;
            
            if (sample) {
                // Use a simple text sample for testing
                const sampleText = 'This is a test sample for quiz generation. The water cycle is the process by which water circulates through the Earth\'s atmosphere, land, and oceans.';
                fileContent = 'data:text/plain;base64,' + btoa(sampleText);
                fileType = 'text/plain';
            } else {
                // Get file from input
                const fileInput = document.getElementById('file-input');
                if (!fileInput || !fileInput.files || !fileInput.files[0]) {
                    console.error('No file selected');
                    return;
                }
                
                const file = fileInput.files[0];
                fileType = file.type;
                
                // Read file
                const reader = new FileReader();
                fileContent = await new Promise((resolve, reject) => {
                    reader.onload = e => resolve(e.target.result);
                    reader.onerror = e => reject(new Error('Failed to read file'));
                    reader.readAsDataURL(file);
                });
            }
            
            // Prepare request data
            const requestData = {
                fileContent: fileContent,
                fileType: fileType,
                quizTitle: 'API Test Quiz',
                quizDescription: 'Testing the quiz generation API',
                numQuestions: 2,
                difficulty: 'easy',
                questionTypes: ['mcq_single', 'true_false'],
                durationMinutes: 10
            };
            
            const csrfToken = DirectGeminiQuizGenerator.getCsrfToken();
            console.log('CSRF token available:', !!csrfToken);
            
            console.log('Sending test API request...');
            const response = await fetch('/academic_integration/api/direct-generate-questions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(requestData)
            });
            
            console.log('API response status:', response.status, response.statusText);
            
            // Get response text first for debugging
            const responseText = await response.text();
            console.log('Response text:', responseText);
            
            // Try to parse as JSON
            try {
                const jsonResponse = JSON.parse(responseText);
                console.log('API test result:', jsonResponse);
                
                // Show result on page
                const resultDiv = document.createElement('div');
                resultDiv.className = response.ok ? 'alert alert-success' : 'alert alert-danger';
                resultDiv.innerHTML = `
                    <h4>API Test Result: ${response.ok ? 'Success' : 'Failed'}</h4>
                    <pre>${JSON.stringify(jsonResponse, null, 2)}</pre>
                `;
                
                // Add to page
                const statusMessages = document.getElementById('status-messages');
                if (statusMessages) {
                    statusMessages.appendChild(resultDiv);
                } else {
                    document.querySelector('.container').appendChild(resultDiv);
                }
                
                return jsonResponse;
            } catch (e) {
                console.error('Failed to parse response as JSON:', e);
                return { success: false, error: 'Invalid JSON response' };
            }
        } catch (error) {
            console.error('API test failed:', error);
            return { success: false, error: error.message };
        }
    };
    
    // Add a test button to the page
    const testButton = document.createElement('button');
    testButton.textContent = '🧪 Test API';
    testButton.className = 'btn btn-sm btn-outline-info';
    testButton.style.position = 'fixed';
    testButton.style.top = '10px';
    testButton.style.right = '10px';
    testButton.style.zIndex = '9999';
    testButton.onclick = () => window.testQuizApi();
    document.body.appendChild(testButton);
});