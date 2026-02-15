/**
 * Progress Indicators for NextGenCV v2.0
 * Loading spinners, progress bars, and status indicators for long operations
 */

class ProgressIndicator {
    constructor() {
        this.activeIndicators = new Map();
        this.injectStyles();
    }

    /**
     * Inject CSS styles for progress indicators
     */
    injectStyles() {
        if (document.getElementById('progress-indicator-styles')) return;

        const style = document.createElement('style');
        style.id = 'progress-indicator-styles';
        style.textContent = `
            /* Loading Overlay */
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                backdrop-filter: blur(2px);
            }

            .loading-content {
                background: white;
                border-radius: 12px;
                padding: 2rem;
                text-align: center;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
                max-width: 400px;
                width: 90%;
            }

            /* Spinner */
            .spinner {
                width: 60px;
                height: 60px;
                margin: 0 auto 1rem;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #0d6efd;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .spinner-sm {
                width: 30px;
                height: 30px;
                border-width: 3px;
            }

            .spinner-lg {
                width: 80px;
                height: 80px;
                border-width: 5px;
            }

            /* Progress Bar */
            .progress-bar-container {
                width: 100%;
                height: 8px;
                background-color: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
                margin: 1rem 0;
            }

            .progress-bar-fill {
                height: 100%;
                background: linear-gradient(90deg, #0d6efd 0%, #0b5ed7 100%);
                border-radius: 4px;
                transition: width 0.3s ease;
                position: relative;
                overflow: hidden;
            }

            .progress-bar-fill::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                bottom: 0;
                right: 0;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(255, 255, 255, 0.3),
                    transparent
                );
                animation: shimmer 2s infinite;
            }

            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }

            /* Inline Spinner */
            .inline-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 2px solid #f3f3f3;
                border-top: 2px solid #0d6efd;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 0.5rem;
                vertical-align: middle;
            }

            /* Button Loading State */
            .btn-loading {
                position: relative;
                pointer-events: none;
                opacity: 0.7;
            }

            .btn-loading::after {
                content: '';
                position: absolute;
                width: 16px;
                height: 16px;
                top: 50%;
                left: 50%;
                margin-left: -8px;
                margin-top: -8px;
                border: 2px solid transparent;
                border-top-color: currentColor;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }

            /* Skeleton Loader */
            .skeleton {
                background: linear-gradient(
                    90deg,
                    #f0f0f0 25%,
                    #e0e0e0 50%,
                    #f0f0f0 75%
                );
                background-size: 200% 100%;
                animation: loading 1.5s ease-in-out infinite;
                border-radius: 4px;
            }

            @keyframes loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }

            .skeleton-text {
                height: 1rem;
                margin-bottom: 0.5rem;
            }

            .skeleton-title {
                height: 1.5rem;
                width: 60%;
                margin-bottom: 1rem;
            }

            .skeleton-card {
                height: 200px;
                margin-bottom: 1rem;
            }

            /* Upload Progress */
            .upload-progress {
                background: white;
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                margin-top: 1rem;
            }

            .upload-progress-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }

            .upload-progress-file {
                font-weight: 600;
                color: #212529;
            }

            .upload-progress-percentage {
                font-weight: 600;
                color: #0d6efd;
            }

            .upload-progress-bar {
                height: 6px;
                background-color: #e9ecef;
                border-radius: 3px;
                overflow: hidden;
            }

            .upload-progress-bar-fill {
                height: 100%;
                background: linear-gradient(90deg, #0d6efd 0%, #0b5ed7 100%);
                border-radius: 3px;
                transition: width 0.3s ease;
            }

            .upload-progress-status {
                margin-top: 0.5rem;
                font-size: 0.875rem;
                color: #6c757d;
            }

            /* Dots Loader */
            .dots-loader {
                display: inline-flex;
                gap: 0.25rem;
            }

            .dots-loader span {
                width: 8px;
                height: 8px;
                background-color: #0d6efd;
                border-radius: 50%;
                animation: bounce 1.4s infinite ease-in-out both;
            }

            .dots-loader span:nth-child(1) {
                animation-delay: -0.32s;
            }

            .dots-loader span:nth-child(2) {
                animation-delay: -0.16s;
            }

            @keyframes bounce {
                0%, 80%, 100% {
                    transform: scale(0);
                    opacity: 0.5;
                }
                40% {
                    transform: scale(1);
                    opacity: 1;
                }
            }

            /* Pulse Loader */
            .pulse-loader {
                width: 60px;
                height: 60px;
                margin: 0 auto;
                border-radius: 50%;
                background-color: #0d6efd;
                animation: pulse 1.5s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% {
                    transform: scale(0.8);
                    opacity: 0.5;
                }
                50% {
                    transform: scale(1);
                    opacity: 1;
                }
            }

            /* Step Progress */
            .step-progress {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 2rem 0;
            }

            .step-progress-item {
                flex: 1;
                text-align: center;
                position: relative;
            }

            .step-progress-item:not(:last-child)::after {
                content: '';
                position: absolute;
                top: 20px;
                left: 50%;
                width: 100%;
                height: 2px;
                background-color: #e9ecef;
                z-index: -1;
            }

            .step-progress-item.completed::after {
                background-color: #198754;
            }

            .step-progress-item.active::after {
                background: linear-gradient(90deg, #198754 0%, #e9ecef 100%);
            }

            .step-progress-circle {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background-color: #e9ecef;
                color: #6c757d;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                margin-bottom: 0.5rem;
                transition: all 0.3s ease;
            }

            .step-progress-item.completed .step-progress-circle {
                background-color: #198754;
                color: white;
            }

            .step-progress-item.active .step-progress-circle {
                background-color: #0d6efd;
                color: white;
                box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.2);
            }

            .step-progress-label {
                font-size: 0.875rem;
                color: #6c757d;
            }

            .step-progress-item.completed .step-progress-label,
            .step-progress-item.active .step-progress-label {
                color: #212529;
                font-weight: 500;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Show loading overlay with spinner
     */
    showLoading(message = 'Loading...', id = 'default') {
        this.hideLoading(id); // Remove existing

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = `loading-${id}`;
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <p class="mb-0">${message}</p>
            </div>
        `;

        document.body.appendChild(overlay);
        this.activeIndicators.set(id, overlay);
    }

    /**
     * Hide loading overlay
     */
    hideLoading(id = 'default') {
        const overlay = this.activeIndicators.get(id);
        if (overlay) {
            overlay.remove();
            this.activeIndicators.delete(id);
        }
    }

    /**
     * Show progress bar
     */
    showProgress(message = 'Processing...', id = 'default') {
        this.hideLoading(id);

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = `loading-${id}`;
        overlay.innerHTML = `
            <div class="loading-content">
                <p class="mb-2">${message}</p>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: 0%"></div>
                </div>
                <p class="mb-0 text-muted" id="progress-percentage-${id}">0%</p>
            </div>
        `;

        document.body.appendChild(overlay);
        this.activeIndicators.set(id, overlay);
    }

    /**
     * Update progress bar
     */
    updateProgress(percentage, id = 'default') {
        const overlay = this.activeIndicators.get(id);
        if (!overlay) return;

        const progressBar = overlay.querySelector('.progress-bar-fill');
        const percentageText = overlay.querySelector(`#progress-percentage-${id}`);

        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
        if (percentageText) {
            percentageText.textContent = `${Math.round(percentage)}%`;
        }
    }

    /**
     * Show inline spinner
     */
    showInlineSpinner(element) {
        if (element.querySelector('.inline-spinner')) return;

        const spinner = document.createElement('span');
        spinner.className = 'inline-spinner';
        element.appendChild(spinner);
    }

    /**
     * Hide inline spinner
     */
    hideInlineSpinner(element) {
        const spinner = element.querySelector('.inline-spinner');
        if (spinner) {
            spinner.remove();
        }
    }

    /**
     * Add loading state to button
     */
    setButtonLoading(button, loading = true) {
        if (loading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.setAttribute('data-original-text', button.textContent);
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            const originalText = button.getAttribute('data-original-text');
            if (originalText) {
                button.textContent = originalText;
                button.removeAttribute('data-original-text');
            }
        }
    }

    /**
     * Show upload progress
     */
    showUploadProgress(fileName, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const progressHtml = `
            <div class="upload-progress" id="upload-progress-${containerId}">
                <div class="upload-progress-header">
                    <span class="upload-progress-file">${fileName}</span>
                    <span class="upload-progress-percentage">0%</span>
                </div>
                <div class="upload-progress-bar">
                    <div class="upload-progress-bar-fill" style="width: 0%"></div>
                </div>
                <div class="upload-progress-status">Uploading...</div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', progressHtml);
    }

    /**
     * Update upload progress
     */
    updateUploadProgress(percentage, containerId, status = 'Uploading...') {
        const progressElement = document.getElementById(`upload-progress-${containerId}`);
        if (!progressElement) return;

        const progressBar = progressElement.querySelector('.upload-progress-bar-fill');
        const percentageText = progressElement.querySelector('.upload-progress-percentage');
        const statusText = progressElement.querySelector('.upload-progress-status');

        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }
        if (percentageText) {
            percentageText.textContent = `${Math.round(percentage)}%`;
        }
        if (statusText) {
            statusText.textContent = status;
        }
    }

    /**
     * Complete upload progress
     */
    completeUploadProgress(containerId, success = true) {
        const progressElement = document.getElementById(`upload-progress-${containerId}`);
        if (!progressElement) return;

        const statusText = progressElement.querySelector('.upload-progress-status');
        if (statusText) {
            statusText.textContent = success ? 'Upload complete!' : 'Upload failed';
            statusText.style.color = success ? '#198754' : '#dc3545';
        }

        if (success) {
            setTimeout(() => {
                progressElement.remove();
            }, 2000);
        }
    }

    /**
     * Show skeleton loader
     */
    showSkeleton(container, type = 'text', count = 3) {
        const skeletons = [];
        for (let i = 0; i < count; i++) {
            skeletons.push(`<div class="skeleton skeleton-${type}"></div>`);
        }
        container.innerHTML = skeletons.join('');
    }

    /**
     * Show step progress
     */
    showStepProgress(steps, currentStep, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const stepsHtml = steps.map((step, index) => {
            const stepNumber = index + 1;
            let className = 'step-progress-item';
            if (stepNumber < currentStep) className += ' completed';
            if (stepNumber === currentStep) className += ' active';

            return `
                <div class="${className}">
                    <div class="step-progress-circle">
                        ${stepNumber < currentStep ? '<i class="bi bi-check"></i>' : stepNumber}
                    </div>
                    <div class="step-progress-label">${step}</div>
                </div>
            `;
        }).join('');

        container.innerHTML = `<div class="step-progress">${stepsHtml}</div>`;
    }

    /**
     * Update step progress
     */
    updateStepProgress(currentStep, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const items = container.querySelectorAll('.step-progress-item');
        items.forEach((item, index) => {
            const stepNumber = index + 1;
            item.className = 'step-progress-item';
            
            if (stepNumber < currentStep) {
                item.classList.add('completed');
                const circle = item.querySelector('.step-progress-circle');
                circle.innerHTML = '<i class="bi bi-check"></i>';
            } else if (stepNumber === currentStep) {
                item.classList.add('active');
            }
        });
    }
}

// Create global instance
window.progressIndicator = new ProgressIndicator();

/**
 * File upload with progress
 */
function uploadFileWithProgress(file, url, containerId) {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        formData.append('file', file);

        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            formData.append('csrfmiddlewaretoken', csrfToken);
        }

        const xhr = new XMLHttpRequest();

        // Show progress
        window.progressIndicator.showUploadProgress(file.name, containerId);

        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentage = (e.loaded / e.total) * 100;
                window.progressIndicator.updateUploadProgress(percentage, containerId);
            }
        });

        // Handle completion
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                window.progressIndicator.completeUploadProgress(containerId, true);
                resolve(JSON.parse(xhr.responseText));
            } else {
                window.progressIndicator.completeUploadProgress(containerId, false);
                reject(new Error(`Upload failed: ${xhr.statusText}`));
            }
        });

        // Handle errors
        xhr.addEventListener('error', () => {
            window.progressIndicator.completeUploadProgress(containerId, false);
            reject(new Error('Upload failed'));
        });

        // Send request
        xhr.open('POST', url);
        xhr.send(formData);
    });
}

// Export utilities
window.ProgressIndicator = ProgressIndicator;
window.uploadFileWithProgress = uploadFileWithProgress;
