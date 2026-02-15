/**
 * Tutorial and Guided Tour System for NextGenCV v2.0
 * Provides interactive tutorials, contextual help, and tooltips
 */

class TutorialSystem {
    constructor() {
        this.currentStep = 0;
        this.currentTutorial = null;
        this.overlay = null;
        this.tutorialBox = null;
        this.completedTutorials = this.loadCompletedTutorials();
    }

    /**
     * Load completed tutorials from localStorage
     */
    loadCompletedTutorials() {
        const completed = localStorage.getItem('completedTutorials');
        return completed ? JSON.parse(completed) : [];
    }

    /**
     * Save completed tutorial to localStorage
     */
    saveCompletedTutorial(tutorialId) {
        if (!this.completedTutorials.includes(tutorialId)) {
            this.completedTutorials.push(tutorialId);
            localStorage.setItem('completedTutorials', JSON.stringify(this.completedTutorials));
        }
    }

    /**
     * Check if tutorial has been completed
     */
    isTutorialCompleted(tutorialId) {
        return this.completedTutorials.includes(tutorialId);
    }

    /**
     * Start a tutorial
     */
    startTutorial(tutorialId) {
        const tutorial = TUTORIALS[tutorialId];
        if (!tutorial) {
            console.error(`Tutorial ${tutorialId} not found`);
            return;
        }

        this.currentTutorial = tutorial;
        this.currentStep = 0;
        this.createOverlay();
        this.showStep(0);
    }

    /**
     * Create overlay for tutorial
     */
    createOverlay() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'tutorial-overlay';
        this.overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 9998;
            display: flex;
            align-items: center;
            justify-content: center;
        `;

        // Create tutorial box
        this.tutorialBox = document.createElement('div');
        this.tutorialBox.className = 'tutorial-box';
        this.tutorialBox.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;

        this.overlay.appendChild(this.tutorialBox);
        document.body.appendChild(this.overlay);

        // Add animation keyframes
        if (!document.getElementById('tutorial-animations')) {
            const style = document.createElement('style');
            style.id = 'tutorial-animations';
            style.textContent = `
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                @keyframes pulse {
                    0%, 100% {
                        box-shadow: 0 0 0 0 rgba(13, 110, 253, 0.7);
                    }
                    50% {
                        box-shadow: 0 0 0 10px rgba(13, 110, 253, 0);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Show a specific step
     */
    showStep(stepIndex) {
        const step = this.currentTutorial.steps[stepIndex];
        if (!step) return;

        // Highlight target element if specified
        if (step.target) {
            this.highlightElement(step.target);
        }

        // Update tutorial box content
        this.tutorialBox.innerHTML = `
            <div class="tutorial-header mb-3">
                <h4 class="mb-1">${this.currentTutorial.title}</h4>
                <p class="text-muted mb-0">Step ${stepIndex + 1} of ${this.currentTutorial.steps.length}</p>
            </div>
            <div class="tutorial-content mb-4">
                <h5 class="mb-2">${step.title}</h5>
                <p class="mb-0">${step.content}</p>
                ${step.image ? `<img src="${step.image}" class="img-fluid mt-3 rounded" alt="${step.title}">` : ''}
            </div>
            <div class="tutorial-progress mb-3">
                <div class="progress" style="height: 4px;">
                    <div class="progress-bar" role="progressbar" 
                         style="width: ${((stepIndex + 1) / this.currentTutorial.steps.length) * 100}%"></div>
                </div>
            </div>
            <div class="tutorial-actions d-flex justify-content-between">
                <button class="btn btn-outline-secondary" id="tutorial-skip">
                    Skip Tutorial
                </button>
                <div>
                    ${stepIndex > 0 ? '<button class="btn btn-outline-primary me-2" id="tutorial-prev">Previous</button>' : ''}
                    <button class="btn btn-primary" id="tutorial-next">
                        ${stepIndex < this.currentTutorial.steps.length - 1 ? 'Next' : 'Finish'}
                    </button>
                </div>
            </div>
        `;

        // Attach event listeners
        document.getElementById('tutorial-skip').addEventListener('click', () => this.endTutorial(false));
        document.getElementById('tutorial-next').addEventListener('click', () => this.nextStep());
        
        const prevBtn = document.getElementById('tutorial-prev');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.previousStep());
        }
    }

    /**
     * Highlight target element
     */
    highlightElement(selector) {
        // Remove previous highlights
        document.querySelectorAll('.tutorial-highlight').forEach(el => {
            el.classList.remove('tutorial-highlight');
        });

        // Add highlight to target
        const element = document.querySelector(selector);
        if (element) {
            element.classList.add('tutorial-highlight');
            element.style.cssText += `
                position: relative;
                z-index: 10000;
                animation: pulse 2s infinite;
            `;
            
            // Scroll to element
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Go to next step
     */
    nextStep() {
        if (this.currentStep < this.currentTutorial.steps.length - 1) {
            this.currentStep++;
            this.showStep(this.currentStep);
        } else {
            this.endTutorial(true);
        }
    }

    /**
     * Go to previous step
     */
    previousStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.showStep(this.currentStep);
        }
    }

    /**
     * End tutorial
     */
    endTutorial(completed) {
        // Remove highlights
        document.querySelectorAll('.tutorial-highlight').forEach(el => {
            el.classList.remove('tutorial-highlight');
            el.style.animation = '';
        });

        // Remove overlay
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }

        // Save completion
        if (completed && this.currentTutorial) {
            this.saveCompletedTutorial(this.currentTutorial.id);
        }

        this.currentTutorial = null;
        this.currentStep = 0;
    }

    /**
     * Show contextual help tooltip
     */
    showHelp(helpId) {
        const helpContent = HELP_CONTENT[helpId];
        if (!helpContent) return;

        // Create help modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-question-circle text-primary me-2"></i>
                            ${helpContent.title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${helpContent.content}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Remove modal from DOM after hiding
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
}

/**
 * Tutorial Definitions
 */
const TUTORIALS = {
    'pdf-upload': {
        id: 'pdf-upload',
        title: 'Upload Your Resume',
        steps: [
            {
                title: 'Welcome to PDF Upload',
                content: 'This feature allows you to upload your existing resume in PDF format. We\'ll automatically extract and structure the information for you.',
                target: null
            },
            {
                title: 'Select Your PDF',
                content: 'Click the file upload area or drag and drop your resume PDF. Make sure your file is under 10MB and is a text-based PDF (not a scanned image).',
                target: '#pdf-upload-area'
            },
            {
                title: 'Review Extracted Data',
                content: 'After upload, we\'ll show you the extracted information. You can review and edit any fields before confirming.',
                target: null
            },
            {
                title: 'Parsing Confidence',
                content: 'We\'ll show you a confidence score indicating how well we understood your resume format. Lower scores mean you should review the data more carefully.',
                target: null
            }
        ]
    },
    'resume-optimization': {
        id: 'resume-optimization',
        title: 'AI-Powered Resume Optimization',
        steps: [
            {
                title: 'Welcome to Resume Fix',
                content: 'This powerful feature uses AI to automatically improve your resume based on best practices and job descriptions.',
                target: null
            },
            {
                title: 'Paste Job Description',
                content: 'Copy and paste the job description you\'re applying for. Our AI will analyze it to find missing keywords and suggest improvements.',
                target: '#job-description-textarea'
            },
            {
                title: 'Review Suggestions',
                content: 'We\'ll show you a side-by-side comparison of your original resume and the optimized version, with all changes highlighted.',
                target: null
            },
            {
                title: 'Accept or Reject Changes',
                content: 'You have full control. Review each change and accept or reject them individually. Your original resume is never modified.',
                target: null
            },
            {
                title: 'Track Improvements',
                content: 'See your ATS score improvement and track all optimization sessions in your analytics dashboard.',
                target: null
            }
        ]
    },
    'version-control': {
        id: 'version-control',
        title: 'Resume Version Control',
        steps: [
            {
                title: 'Automatic Versioning',
                content: 'Every time you make changes to your resume, we automatically create a new version. You never lose your work!',
                target: null
            },
            {
                title: 'View Version History',
                content: 'Access all previous versions of your resume from the versions page. See when each version was created and what changed.',
                target: '#versions-link'
            },
            {
                title: 'Compare Versions',
                content: 'Select any two versions to see a detailed comparison with highlighted differences.',
                target: null
            },
            {
                title: 'Restore Previous Versions',
                content: 'Need to go back? You can restore any previous version, which creates a new version based on the old one.',
                target: null
            }
        ]
    },
    'analytics-dashboard': {
        id: 'analytics-dashboard',
        title: 'Analytics Dashboard',
        steps: [
            {
                title: 'Track Your Progress',
                content: 'The analytics dashboard gives you comprehensive insights into your resume\'s performance and improvement over time.',
                target: null
            },
            {
                title: 'Resume Health Score',
                content: 'See your overall resume health score based on completeness, formatting, and best practices.',
                target: '#health-score-meter'
            },
            {
                title: 'ATS Score Trends',
                content: 'Track how your ATS score has improved over time with interactive charts.',
                target: '#score-trend-chart'
            },
            {
                title: 'Missing Keywords',
                content: 'Discover the most frequently missing keywords across all your analyses to know what skills to highlight.',
                target: '#missing-keywords-section'
            },
            {
                title: 'Improvement Recommendations',
                content: 'Get personalized recommendations on how to further improve your resume.',
                target: null
            }
        ]
    }
};

/**
 * Contextual Help Content
 */
const HELP_CONTENT = {
    'ats-score': {
        title: 'What is an ATS Score?',
        content: `
            <p>An ATS (Applicant Tracking System) score measures how well your resume will perform when scanned by automated systems that many companies use to filter applications.</p>
            <p><strong>Score Components:</strong></p>
            <ul>
                <li><strong>Keyword Match (30%):</strong> How many job description keywords appear in your resume</li>
                <li><strong>Skill Relevance (20%):</strong> How relevant your skills are to the position</li>
                <li><strong>Section Completeness (15%):</strong> Whether all standard sections are present</li>
                <li><strong>Experience Impact (15%):</strong> Quality of your experience descriptions</li>
                <li><strong>Quantification (10%):</strong> Use of numbers and metrics</li>
                <li><strong>Action Verbs (10%):</strong> Use of strong action verbs</li>
            </ul>
            <p><strong>Score Ranges:</strong></p>
            <ul>
                <li><strong>80-100:</strong> Excellent - Very likely to pass ATS</li>
                <li><strong>60-79:</strong> Good - Should pass most ATS</li>
                <li><strong>40-59:</strong> Fair - May need improvements</li>
                <li><strong>0-39:</strong> Poor - Significant improvements needed</li>
            </ul>
        `
    },
    'pdf-parsing': {
        title: 'PDF Parsing Tips',
        content: `
            <p>For best results when uploading your resume PDF:</p>
            <ul>
                <li><strong>Use text-based PDFs:</strong> Avoid scanned images or photos of resumes</li>
                <li><strong>Standard formatting:</strong> Use common section headings like "Experience", "Education", "Skills"</li>
                <li><strong>Simple layouts:</strong> Avoid complex multi-column layouts or tables</li>
                <li><strong>Clear structure:</strong> Use consistent formatting for dates, companies, and roles</li>
                <li><strong>File size:</strong> Keep files under 10MB</li>
            </ul>
            <p><strong>Parsing Confidence:</strong></p>
            <ul>
                <li><strong>90-100%:</strong> Excellent - Data extracted accurately</li>
                <li><strong>70-89%:</strong> Good - Minor review recommended</li>
                <li><strong>Below 70%:</strong> Review carefully - Manual corrections may be needed</li>
            </ul>
        `
    },
    'optimization-process': {
        title: 'How Resume Optimization Works',
        content: `
            <p>Our AI-powered optimization engine improves your resume in several ways:</p>
            <p><strong>1. Keyword Injection:</strong></p>
            <p>We identify important keywords from the job description that are missing from your resume and naturally insert them where appropriate.</p>
            <p><strong>2. Action Verb Enhancement:</strong></p>
            <p>Weak verbs like "did" or "worked on" are replaced with strong action verbs like "achieved", "led", or "implemented".</p>
            <p><strong>3. Quantification Suggestions:</strong></p>
            <p>We suggest adding metrics and numbers to your achievements to make them more impactful.</p>
            <p><strong>4. Formatting Standardization:</strong></p>
            <p>Section headings and date formats are standardized to be ATS-friendly.</p>
            <p><strong>Important:</strong> Your original resume is never modified. All changes create a new version that you can review and accept or reject.</p>
        `
    },
    'version-comparison': {
        title: 'Understanding Version Comparisons',
        content: `
            <p>When comparing two resume versions, you'll see:</p>
            <ul>
                <li><strong>Green highlights:</strong> Content that was added</li>
                <li><strong>Red highlights:</strong> Content that was removed</li>
                <li><strong>Yellow highlights:</strong> Content that was modified</li>
            </ul>
            <p><strong>Comparison Features:</strong></p>
            <ul>
                <li>Side-by-side view of both versions</li>
                <li>Section-by-section navigation</li>
                <li>Score changes between versions</li>
                <li>Detailed change log</li>
            </ul>
            <p><strong>Tip:</strong> Use version comparison to understand how optimizations improved your resume and learn what changes work best.</p>
        `
    },
    'resume-health': {
        title: 'Resume Health Metrics',
        content: `
            <p>Your resume health score is calculated based on multiple factors:</p>
            <p><strong>Section Completeness (40 points):</strong></p>
            <p>Checks for presence of essential sections: Personal Info, Experience, Education, and Skills.</p>
            <p><strong>Contact Information (15 points):</strong></p>
            <p>Verifies you have email, phone, and location information.</p>
            <p><strong>Quantified Achievements (20 points):</strong></p>
            <p>Measures how many of your bullet points include numbers, percentages, or metrics.</p>
            <p><strong>Action Verb Usage (15 points):</strong></p>
            <p>Evaluates use of strong action verbs at the start of bullet points.</p>
            <p><strong>ATS-Friendly Formatting (10 points):</strong></p>
            <p>Checks for formatting that works well with ATS systems.</p>
            <p><strong>Improving Your Score:</strong></p>
            <ul>
                <li>Complete all sections</li>
                <li>Add metrics to achievements</li>
                <li>Use strong action verbs</li>
                <li>Avoid complex formatting</li>
            </ul>
        `
    },
    'template-customization': {
        title: 'Template Customization',
        content: `
            <p>Customize your resume template to match your personal brand:</p>
            <p><strong>Color Schemes:</strong></p>
            <p>Choose from pre-defined color schemes or create your own. Colors are applied to headings, accents, and borders.</p>
            <p><strong>Font Families:</strong></p>
            <p>Select from ATS-safe fonts that look professional and are readable by automated systems.</p>
            <p><strong>Custom CSS:</strong></p>
            <p>Advanced users can add custom CSS for fine-tuned control over styling.</p>
            <p><strong>Important:</strong> All customizations are saved per resume and applied when exporting to PDF.</p>
            <p><strong>ATS Compatibility:</strong></p>
            <p>We ensure all customization options maintain ATS compatibility. Avoid overly complex designs that may confuse automated systems.</p>
        `
    }
};

/**
 * Initialize tutorial system on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    window.tutorialSystem = new TutorialSystem();

    // Auto-start tutorials for first-time users
    const currentPage = document.body.getAttribute('data-page');
    
    if (currentPage && !window.tutorialSystem.isTutorialCompleted(currentPage)) {
        // Show tutorial prompt
        setTimeout(() => {
            if (TUTORIALS[currentPage]) {
                showTutorialPrompt(currentPage);
            }
        }, 1000);
    }

    // Initialize help buttons
    document.querySelectorAll('[data-help]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const helpId = this.getAttribute('data-help');
            window.tutorialSystem.showHelp(helpId);
        });
    });

    // Initialize tutorial start buttons
    document.querySelectorAll('[data-tutorial]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const tutorialId = this.getAttribute('data-tutorial');
            window.tutorialSystem.startTutorial(tutorialId);
        });
    });
});

/**
 * Show tutorial prompt
 */
function showTutorialPrompt(tutorialId) {
    const tutorial = TUTORIALS[tutorialId];
    if (!tutorial) return;

    const prompt = document.createElement('div');
    prompt.className = 'tutorial-prompt';
    prompt.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        max-width: 350px;
        z-index: 9997;
        animation: slideInRight 0.3s ease-out;
    `;

    prompt.innerHTML = `
        <div class="d-flex align-items-start">
            <div class="flex-shrink-0">
                <i class="bi bi-lightbulb text-warning" style="font-size: 2rem;"></i>
            </div>
            <div class="flex-grow-1 ms-3">
                <h6 class="mb-2">New Feature Tour</h6>
                <p class="mb-3 small text-muted">Would you like a quick tour of ${tutorial.title}?</p>
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-primary" id="start-tutorial-prompt">
                        Start Tour
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" id="dismiss-tutorial-prompt">
                        Maybe Later
                    </button>
                </div>
            </div>
            <button class="btn-close btn-sm ms-2" id="close-tutorial-prompt"></button>
        </div>
    `;

    document.body.appendChild(prompt);

    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
    `;
    document.head.appendChild(style);

    // Event listeners
    document.getElementById('start-tutorial-prompt').addEventListener('click', () => {
        prompt.remove();
        window.tutorialSystem.startTutorial(tutorialId);
    });

    document.getElementById('dismiss-tutorial-prompt').addEventListener('click', () => {
        prompt.remove();
        window.tutorialSystem.saveCompletedTutorial(tutorialId);
    });

    document.getElementById('close-tutorial-prompt').addEventListener('click', () => {
        prompt.remove();
    });
}

// Export for global access
window.TutorialSystem = TutorialSystem;
window.TUTORIALS = TUTORIALS;
window.HELP_CONTENT = HELP_CONTENT;
