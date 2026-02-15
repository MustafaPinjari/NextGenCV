/**
 * Progress Indicator Usage Examples
 * Demonstrates how to use progress indicators in various scenarios
 */

// Example 1: Simple loading overlay
function exampleSimpleLoading() {
    // Show loading
    window.progressIndicator.showLoading('Processing your request...');
    
    // Simulate async operation
    setTimeout(() => {
        window.progressIndicator.hideLoading();
    }, 2000);
}

// Example 2: Progress bar with updates
function exampleProgressBar() {
    window.progressIndicator.showProgress('Optimizing resume...');
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10;
        window.progressIndicator.updateProgress(progress);
        
        if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                window.progressIndicator.hideLoading();
            }, 500);
        }
    }, 300);
}

// Example 3: Button loading state
function exampleButtonLoading() {
    const button = document.getElementById('submit-btn');
    
    // Set loading state
    window.progressIndicator.setButtonLoading(button, true);
    
    // Simulate async operation
    setTimeout(() => {
        window.progressIndicator.setButtonLoading(button, false);
    }, 2000);
}

// Example 4: File upload with progress
function exampleFileUpload() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    uploadFileWithProgress(file, '/api/upload/', 'upload-container')
        .then(response => {
            console.log('Upload successful:', response);
        })
        .catch(error => {
            console.error('Upload failed:', error);
        });
}

// Example 5: Step progress indicator
function exampleStepProgress() {
    const steps = ['Upload PDF', 'Parse Content', 'Review Data', 'Confirm'];
    
    // Show initial step
    window.progressIndicator.showStepProgress(steps, 1, 'step-container');
    
    // Simulate progression
    let currentStep = 1;
    const interval = setInterval(() => {
        currentStep++;
        window.progressIndicator.updateStepProgress(currentStep, 'step-container');
        
        if (currentStep > steps.length) {
            clearInterval(interval);
        }
    }, 2000);
}

// Example 6: Inline spinner
function exampleInlineSpinner() {
    const element = document.getElementById('status-text');
    
    // Show spinner
    window.progressIndicator.showInlineSpinner(element);
    
    // Hide after delay
    setTimeout(() => {
        window.progressIndicator.hideInlineSpinner(element);
    }, 2000);
}

// Example 7: Skeleton loader
function exampleSkeletonLoader() {
    const container = document.getElementById('content-container');
    
    // Show skeleton
    window.progressIndicator.showSkeleton(container, 'text', 5);
    
    // Load actual content after delay
    setTimeout(() => {
        container.innerHTML = '<p>Actual content loaded!</p>';
    }, 2000);
}

// Example 8: Form submission with progress
function exampleFormSubmission() {
    const form = document.getElementById('resume-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        window.progressIndicator.setButtonLoading(submitBtn, true);
        window.progressIndicator.showProgress('Saving your resume...');
        
        // Simulate form submission
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            window.progressIndicator.updateProgress(100);
            setTimeout(() => {
                window.progressIndicator.hideLoading();
                window.progressIndicator.setButtonLoading(submitBtn, false);
                alert('Resume saved successfully!');
            }, 500);
        })
        .catch(error => {
            window.progressIndicator.hideLoading();
            window.progressIndicator.setButtonLoading(submitBtn, false);
            alert('Error saving resume: ' + error.message);
        });
    });
}

// Example 9: PDF parsing with progress
function examplePDFParsing() {
    window.progressIndicator.showProgress('Parsing PDF...');
    
    const stages = [
        { progress: 20, message: 'Extracting text...' },
        { progress: 40, message: 'Identifying sections...' },
        { progress: 60, message: 'Parsing experiences...' },
        { progress: 80, message: 'Parsing education...' },
        { progress: 100, message: 'Complete!' }
    ];
    
    let currentStage = 0;
    const interval = setInterval(() => {
        if (currentStage < stages.length) {
            const stage = stages[currentStage];
            window.progressIndicator.updateProgress(stage.progress);
            
            // Update message
            const overlay = document.querySelector('.loading-overlay .loading-content p');
            if (overlay) {
                overlay.textContent = stage.message;
            }
            
            currentStage++;
        } else {
            clearInterval(interval);
            setTimeout(() => {
                window.progressIndicator.hideLoading();
            }, 500);
        }
    }, 800);
}

// Example 10: Resume optimization with progress
function exampleResumeOptimization() {
    const steps = [
        'Analyzing resume',
        'Extracting keywords',
        'Rewriting bullet points',
        'Injecting keywords',
        'Calculating score'
    ];
    
    window.progressIndicator.showStepProgress(steps, 1, 'optimization-steps');
    
    let currentStep = 1;
    const interval = setInterval(() => {
        currentStep++;
        window.progressIndicator.updateStepProgress(currentStep, 'optimization-steps');
        
        if (currentStep > steps.length) {
            clearInterval(interval);
            setTimeout(() => {
                alert('Optimization complete!');
            }, 500);
        }
    }, 1500);
}

/**
 * Initialize progress indicators for common operations
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-add progress to file uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Create progress container if it doesn't exist
                let container = this.parentElement.querySelector('.upload-progress-container');
                if (!container) {
                    container = document.createElement('div');
                    container.className = 'upload-progress-container';
                    container.id = `upload-container-${Date.now()}`;
                    this.parentElement.appendChild(container);
                }
            }
        });
    });

    // Auto-add loading state to forms
    const forms = document.querySelectorAll('form[data-progress]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                window.progressIndicator.setButtonLoading(submitBtn, true);
            }
            
            const message = this.getAttribute('data-progress-message') || 'Processing...';
            window.progressIndicator.showLoading(message);
        });
    });

    // Auto-add loading state to AJAX buttons
    const ajaxButtons = document.querySelectorAll('[data-ajax-action]');
    ajaxButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.progressIndicator.setButtonLoading(this, true);
            
            const message = this.getAttribute('data-loading-message') || 'Loading...';
            window.progressIndicator.showLoading(message);
        });
    });
});

// Export examples for testing
window.ProgressExamples = {
    simpleLoading: exampleSimpleLoading,
    progressBar: exampleProgressBar,
    buttonLoading: exampleButtonLoading,
    fileUpload: exampleFileUpload,
    stepProgress: exampleStepProgress,
    inlineSpinner: exampleInlineSpinner,
    skeletonLoader: exampleSkeletonLoader,
    formSubmission: exampleFormSubmission,
    pdfParsing: examplePDFParsing,
    resumeOptimization: exampleResumeOptimization
};
