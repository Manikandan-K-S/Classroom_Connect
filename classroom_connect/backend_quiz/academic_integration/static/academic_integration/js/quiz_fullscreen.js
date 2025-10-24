/**
 * Quiz Fullscreen Manager - Strict Mode
 * Enforces fullscreen mode for quiz taking
 * Auto-submits and redirects on any fullscreen exit
 */

console.log('Quiz Fullscreen Manager - Strict Mode loaded');

let quizStarted = false;
let fullscreenActive = false;
let isSubmitting = false;

// Function to enter fullscreen mode
function enterFullscreen() {
    console.log('Attempting to enter fullscreen...');
    const elem = document.documentElement;
    
    const fullscreenPromise = elem.requestFullscreen ? elem.requestFullscreen() :
                              elem.webkitRequestFullscreen ? elem.webkitRequestFullscreen() :
                              elem.mozRequestFullScreen ? elem.mozRequestFullScreen() :
                              elem.msRequestFullscreen ? elem.msRequestFullscreen() :
                              Promise.reject(new Error('Fullscreen not supported'));
    
    if (fullscreenPromise && fullscreenPromise.then) {
        fullscreenPromise
            .then(() => {
                console.log('✅ Fullscreen activated successfully');
                fullscreenActive = true;
                quizStarted = true;
                
                // Show quiz content
                const quizContent = document.getElementById('quiz-content');
                const notStarted = document.getElementById('not-started');
                const loading = document.getElementById('loading');
                
                if (loading) loading.style.display = 'block';
                if (notStarted) notStarted.style.display = 'none';
                if (quizContent) quizContent.style.display = 'none';
                
                // Load quiz data
                setTimeout(() => {
                    if (typeof loadQuizData === 'function') {
                        loadQuizData();
                    }
                }, 100);
            })
            .catch(err => {
                console.error('❌ Error entering fullscreen:', err);
                // Keep showing the button
            });
    }
}

// Function to check if currently in fullscreen
function isFullscreen() {
    return !!(document.fullscreenElement || 
              document.webkitFullscreenElement || 
              document.mozFullScreenElement || 
              document.msFullscreenElement);
}

// Function to handle fullscreen change - immediate redirect on exit
function handleFullscreenChange() {
    const inFullscreen = isFullscreen();
    console.log('Fullscreen state changed. In fullscreen:', inFullscreen);
    
    if (!inFullscreen && quizStarted && !isSubmitting) {
        console.log('⚠️ Fullscreen exited - redirecting to dashboard');
        redirectToDashboardWithError();
    }
    
    fullscreenActive = inFullscreen;
}

// Function to redirect to dashboard with error message
function redirectToDashboardWithError() {
    if (isSubmitting) return;
    isSubmitting = true;
    
    console.log('Redirecting to dashboard...');
    
    // Get the base URL
    const studentDashboardUrl = '/academic_integration/student/dashboard/';
    
    // Try to submit quiz first (silent)
    if (typeof submitQuiz === 'function') {
        try {
            submitQuiz(null, true);
        } catch (e) {
            console.log('Silent submit failed:', e);
        }
    }
    
    // Add error message to session storage
    sessionStorage.setItem('quizError', 'Quiz terminated: You exited fullscreen mode. Please retake the quiz in fullscreen mode.');
    
    // Redirect to dashboard
    window.location.href = studentDashboardUrl;
}

// Add event listeners for fullscreen changes
document.addEventListener('fullscreenchange', handleFullscreenChange);
document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
document.addEventListener('mozfullscreenchange', handleFullscreenChange);
document.addEventListener('MSFullscreenChange', handleFullscreenChange);

// Detect tab switching and redirect
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'hidden' && quizStarted && !isSubmitting) {
        console.log('⚠️ Tab switched while in quiz - redirecting to dashboard');
        redirectToDashboardWithError();
    }
});

// Prevent right-click during quiz
document.addEventListener('contextmenu', function(e) {
    if (quizStarted && isFullscreen()) {
        e.preventDefault();
        return false;
    }
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded - initializing strict fullscreen quiz');
    
    const urlPath = window.location.pathname;
    console.log('Current URL:', urlPath);
    
    // Check if this is a quiz page (NOT a result page)
    if (urlPath.includes('/academic_integration/quiz/') && 
        /\/\d+\/$/.test(urlPath) && 
        !urlPath.includes('/result/')) {
        console.log('✅ Quiz page detected');
        
        const startContainer = document.getElementById('fullscreen-start-container');
        const quizCard = document.querySelector('.card.shadow-sm.mb-4:not(#fullscreen-start-container)');
        const notStarted = document.getElementById('not-started');
        const loading = document.getElementById('loading');
        
        // Hide all quiz content initially
        if (quizCard) quizCard.style.display = 'none';
        if (notStarted) notStarted.style.display = 'none';
        if (loading) loading.style.display = 'none';
        
        // Show fullscreen button
        if (startContainer) {
            startContainer.style.display = 'block';
        }
        
        // Try auto-fullscreen first (will fail without user interaction, but worth trying)
        setTimeout(() => {
            console.log('Attempting auto-fullscreen...');
            enterFullscreen();
        }, 500);
        
        // Add click handler to start button (fallback)
        const startButton = document.getElementById('start-fullscreen-quiz');
        if (startButton) {
            startButton.addEventListener('click', function() {
                console.log('Start button clicked - entering fullscreen');
                
                // Hide the start button
                if (startContainer) {
                    startContainer.style.display = 'none';
                }
                
                // Show quiz card
                if (quizCard) {
                    quizCard.style.display = 'block';
                }
                
                // Enter fullscreen
                enterFullscreen();
            });
            
            console.log('✅ Start button event listener attached');
        }
    } else {
        console.log('Not a quiz page, skipping fullscreen initialization');
    }
});

console.log('Quiz Fullscreen Manager - Strict Mode initialized');
