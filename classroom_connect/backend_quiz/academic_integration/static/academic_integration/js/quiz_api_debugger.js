/**
 * quiz_api_debugger.js
 * 
 * This script monitors and logs all network requests to help diagnose issues with the quiz API.
 * It's particularly useful for seeing what API calls are being made and what responses are being received.
 */

(function() {
    // Execute when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Quiz API Debugger initialized');
        
        // Monitor XMLHttpRequests
        setupXHRMonitoring();
        
        // Monitor Fetch API
        setupFetchMonitoring();
        
        // Add UI elements for debugging
        setupDebugUI();
    });
    
    function setupXHRMonitoring() {
        const originalXhrOpen = XMLHttpRequest.prototype.open;
        const originalXhrSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url) {
            this._requestMethod = method;
            this._requestUrl = url;
            console.log(`XHR Request prepared: ${method} ${url}`);
            return originalXhrOpen.apply(this, arguments);
        };
        
        XMLHttpRequest.prototype.send = function(data) {
            console.log(`XHR Request sent: ${this._requestMethod} ${this._requestUrl}`, data ? 'with data' : 'without data');
            
            if (data) {
                try {
                    const jsonData = JSON.parse(data);
                    console.log('Request payload:', jsonData);
                } catch (e) {
                    // Not JSON data
                }
            }
            
            // Monitor response
            this.addEventListener('load', function() {
                console.log(`XHR Response received for ${this._requestUrl}:`, {
                    status: this.status,
                    statusText: this.statusText,
                    responseType: this.responseType,
                    responseSize: this.responseText ? this.responseText.length : 0,
                    responsePreview: this.responseText ? 
                        (this.responseText.length > 100 ? this.responseText.substring(0, 100) + '...' : this.responseText) : 'No text response'
                });
                
                // Try to parse JSON responses
                if (this.responseText && (this.responseType === '' || this.responseType === 'json')) {
                    try {
                        const jsonResponse = JSON.parse(this.responseText);
                        console.log('Parsed JSON response:', jsonResponse);
                    } catch (e) {
                        // Not JSON or invalid JSON
                    }
                }
            });
            
            this.addEventListener('error', function() {
                console.error(`XHR Request failed: ${this._requestMethod} ${this._requestUrl}`);
            });
            
            return originalXhrSend.apply(this, arguments);
        };
    }
    
    function setupFetchMonitoring() {
        const originalFetch = window.fetch;
        
        window.fetch = function(url, options) {
            const method = options && options.method ? options.method : 'GET';
            console.log(`Fetch Request: ${method} ${url}`, options);
            
            // Log request body if available
            if (options && options.body) {
                try {
                    const bodyJson = JSON.parse(options.body);
                    console.log('Fetch request body:', bodyJson);
                } catch (e) {
                    // Not JSON or can't be parsed
                }
            }
            
            return originalFetch.apply(this, arguments).then(response => {
                console.log(`Fetch Response received for ${url}:`, {
                    status: response.status,
                    statusText: response.statusText,
                    type: response.type,
                    headers: Array.from(response.headers.entries())
                });
                
                // Clone the response so we can read it and still return the original
                const clone = response.clone();
                
                // Try to read and log response body
                clone.text().then(text => {
                    console.log(`Fetch Response body preview for ${url}:`, 
                        text.length > 100 ? text.substring(0, 100) + '...' : text);
                    
                    // Try to parse JSON
                    try {
                        const json = JSON.parse(text);
                        console.log('Parsed JSON response:', json);
                    } catch (e) {
                        // Not JSON or invalid JSON
                    }
                }).catch(err => {
                    console.log(`Could not read response body: ${err}`);
                });
                
                return response;
            }).catch(error => {
                console.error(`Fetch error for ${url}:`, error);
                throw error;
            });
        };
    }
    
    function setupDebugUI() {
        // Check if we're on the quiz page
        if (!window.location.href.includes('/quiz/') && !window.location.href.includes('/academic_integration/')) {
            return;
        }
        
        // Create debug button
        const debugButton = document.createElement('button');
        debugButton.textContent = '🔍 Debug Quiz API';
        debugButton.style.position = 'fixed';
        debugButton.style.bottom = '10px';
        debugButton.style.right = '10px';
        debugButton.style.zIndex = '9999';
        debugButton.style.backgroundColor = '#f8f9fa';
        debugButton.style.border = '1px solid #dee2e6';
        debugButton.style.borderRadius = '4px';
        debugButton.style.padding = '6px 12px';
        debugButton.style.cursor = 'pointer';
        debugButton.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        
        // Add click event
        debugButton.addEventListener('click', function() {
            // Test the DirectGeminiQuizGenerator if available
            if (window.DirectGeminiQuizGenerator) {
                console.log('Testing DirectGeminiQuizGenerator...');
                console.log('DirectGeminiQuizGenerator available:', window.DirectGeminiQuizGenerator);
                
                // Test CSRF token retrieval
                const token = window.DirectGeminiQuizGenerator.getCsrfToken();
                console.log('CSRF token available:', !!token);
                
                // Create a dialog with debug info
                alert(
                    'Debug Info:\n' +
                    '- DirectGeminiQuizGenerator is loaded\n' +
                    `- CSRF token is ${token ? 'available' : 'missing'}\n` +
                    '- See browser console for detailed logs\n\n' +
                    'Press F12 to open developer tools and view detailed logs.'
                );
            } else {
                alert(
                    'Error: DirectGeminiQuizGenerator not found!\n\n' +
                    'This indicates there may be a problem loading the required JavaScript file.\n' +
                    'Check the browser console (F12) for more details.'
                );
            }
        });
        
        // Add to document
        document.body.appendChild(debugButton);
    }
})();