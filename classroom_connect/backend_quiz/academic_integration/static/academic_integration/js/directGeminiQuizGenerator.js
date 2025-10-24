/**
 * directGeminiQuizGenerator.js
 * 
 * Utility functions for generating quizzes directly using the Gemini API integration.
 * This simplifies the process by handling file encoding, API communication, and quiz creation.
 */

class DirectGeminiQuizGenerator {
    /**
     * Create a quiz with questions generated from a file using the Gemini API
     * 
     * @param {File} file - The file to generate questions from
     * @param {Object} options - Options for quiz generation
     * @param {string} options.quizTitle - Title of the quiz
     * @param {string} options.quizDescription - Description of the quiz
     * @param {string} options.courseId - Course ID to associate with the quiz
     * @param {number} options.tutorialNumber - Tutorial number (1-4)
     * @param {number} options.numQuestions - Number of questions to generate (default: 5)
     * @param {string} options.difficulty - Difficulty level ("easy", "medium", "hard") (default: "medium")
     * @param {Array} options.questionTypes - Types of questions to generate (default: ["mcq_single", "mcq_multiple", "true_false"])
     * @param {number} options.durationMinutes - Quiz duration in minutes (default: 30)
     * @param {string} options.quizType - Type of quiz ("tutorial", "mock", "exam") (default: "tutorial")
     * @param {boolean} options.isActive - Whether the quiz is active (default: true)
     * @param {boolean} options.showResults - Whether to show results after submission (default: true)
     * @param {boolean} options.allowReview - Whether to allow students to review answers (default: true)
     * @param {string} options.startDate - Start date of the quiz (ISO format)
     * @param {string} options.completeByDate - Completion deadline of the quiz (ISO format)
     * @returns {Promise<Object>} - Result of quiz creation
     */
    static async createQuizFromFile(file, options = {}) {
        return new Promise((resolve, reject) => {
            // Validate the file
            if (!file) {
                reject(new Error('No file provided'));
                return;
            }

            // Set default options
            const defaultOptions = {
                quizTitle: 'Generated Quiz',
                quizDescription: 'Automatically generated from uploaded content',
                numQuestions: 5,
                difficulty: 'medium',
                questionTypes: ['mcq_single', 'mcq_multiple', 'true_false'],
                durationMinutes: 30,
                quizType: 'tutorial',
                isActive: true,
                showResults: true,
                allowReview: true
            };

            // Merge provided options with defaults
            const mergedOptions = { ...defaultOptions, ...options };

            // Read the file and encode it as base64
            const reader = new FileReader();
            
            reader.onload = async function(e) {
                try {
                    // Encode file content as base64
                    const fileContent = e.target.result;
                    
                    // Prepare request data
                    const requestData = {
                        fileContent: fileContent,
                        fileType: file.type,
                        ...mergedOptions
                    };
                    
                    // Get CSRF token
                    const csrfToken = DirectGeminiQuizGenerator.getCsrfToken();
                    console.log('Sending request to generate questions with token:', 
                                csrfToken ? 'Token found' : 'No token!');
                    
                    // Debug info
                    console.log('Request options:', {
                        quizTitle: requestData.quizTitle,
                        fileType: file.type,
                        numQuestions: requestData.numQuestions,
                        difficulty: requestData.difficulty,
                        questionTypes: requestData.questionTypes
                    });
                    
                    // Create an abort controller for timeout handling
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
                    
                    let response;
                    try {
                        // Send request to the API
                        response = await fetch('/academic_integration/api/direct-generate-questions/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrfToken
                            },
                            body: JSON.stringify(requestData),
                            signal: controller.signal
                        });
                        
                        // Clear the timeout since we got a response
                        clearTimeout(timeoutId);
                    
                        console.log('Server response received:', response.status, response.statusText);
                        
                        // Check if response is ok before trying to parse JSON
                        if (!response.ok) {
                            if (response.status === 401) {
                                throw new Error('Authentication failed. Please log in again.');
                            } else if (response.status === 413) {
                                throw new Error('The uploaded file is too large. Please use a smaller file.');
                            } else if (response.status === 429) {
                                throw new Error('Too many requests. Please wait a while and try again.');
                            } else if (response.status >= 500) {
                                throw new Error(`Server error (${response.status}). Please try again later.`);
                            }
                        }
                    } catch (fetchError) {
                        // Check if the error is due to timeout/abort
                        if (fetchError.name === 'AbortError') {
                            throw new Error('Request timed out after 2 minutes. The file may be too large or the server is busy.');
                        }
                        throw fetchError;
                    }
                    
                    // Parse response
                    let responseData;
                    try {
                        // Get the response text
                        const responseText = await response.text();
                        console.log('Response text (first 100 chars):', 
                                   responseText.length > 100 ? responseText.substring(0, 100) + '...' : responseText);
                        
                        // Parse it as JSON
                        try {
                            responseData = JSON.parse(responseText);
                        } catch (jsonParseError) {
                            console.error('Failed to parse JSON response:', jsonParseError);
                            console.error('Raw response:', responseText);
                            throw new Error('Invalid JSON response from server. The server may have encountered an error.');
                        }
                    } catch (fetchError) {
                        console.error('Failed to read response:', fetchError);
                        throw new Error('Failed to read server response. The request may have timed out.');
                    }
                    
                    // Now we have response data, check for API-level errors
                    if (!response.ok) {
                        // We tried to parse the error response above, use it if available
                        throw new Error(responseData?.error || `Server error: ${response.status} ${response.statusText}`);
                    }
                    
                    if (!responseData.success) {
                        throw new Error(responseData.error || 'Quiz generation failed for an unknown reason');
                    }
                    
                    if (!responseData.quiz_id) {
                        throw new Error('Quiz was created but no quiz ID was returned');
                    }
                    
                    console.log('Quiz created successfully:', responseData);
                    resolve(responseData);
                } catch (error) {
                    console.error('Error in quiz creation process:', error);
                    reject(error);
                }
            };
            
            reader.onerror = function(error) {
                console.error('FileReader error:', error);
                reject(new Error('Failed to read file. Make sure the file format is supported.'));
            };
            
            // Read file as data URL (this will give us a base64 encoded string)
            reader.readAsDataURL(file);
        });
    }
    
    /**
     * Get CSRF token from cookies
     */
    static getCsrfToken() {
        // Get the CSRF token from the cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
    
    /**
     * Create a status message element to show progress
     * 
     * @param {string} id - ID to give the status element
     * @param {string} container - CSS selector for the container to append to
     * @returns {Object} - Object with functions to update the status
     */
    static createStatusElement(id, container) {
        // Create status element
        const statusElement = document.createElement('div');
        statusElement.id = id;
        statusElement.className = 'quiz-generation-status alert';
        statusElement.style.display = 'none';
        
        // Append to container
        const containerElement = document.querySelector(container);
        if (containerElement) {
            containerElement.appendChild(statusElement);
        } else {
            document.body.appendChild(statusElement);
        }
        
        return {
            showLoading: (message = 'Generating questions...') => {
                statusElement.className = 'quiz-generation-status alert alert-info';
                statusElement.innerHTML = `
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="sr-only">Loading...</span>
                    </div>
                    <span class="ml-2">${message}</span>
                `;
                statusElement.style.display = 'block';
            },
            showSuccess: (message) => {
                statusElement.className = 'quiz-generation-status alert alert-success';
                statusElement.textContent = message;
                statusElement.style.display = 'block';
            },
            showError: (message) => {
                statusElement.className = 'quiz-generation-status alert alert-danger';
                statusElement.textContent = message;
                statusElement.style.display = 'block';
            },
            hide: () => {
                statusElement.style.display = 'none';
            }
        };
    }
}