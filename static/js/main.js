// Main JavaScript for ATS Resume Builder

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initAlerts();
    initDeleteConfirmations();
    initFormValidation();
    initDynamicFormFields();
    initTooltips();
});

/**
 * Auto-dismiss alerts after 5 seconds
 */
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * Confirm delete actions with custom dialog
 */
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const itemName = button.getAttribute('data-item-name') || 'this item';
            const message = `Are you sure you want to delete ${itemName}? This action cannot be undone.`;
            
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Client-side form validation for immediate feedback
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        // Real-time validation on input
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(input);
            });
            
            input.addEventListener('input', function() {
                if (input.classList.contains('is-invalid')) {
                    validateField(input);
                }
            });
        });
        
        // Form submission validation
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const isValid = field.checkValidity();
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
    
    // Custom validation messages
    if (!isValid) {
        const feedback = field.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            if (field.validity.valueMissing) {
                feedback.textContent = 'This field is required.';
            } else if (field.validity.typeMismatch) {
                if (field.type === 'email') {
                    feedback.textContent = 'Please enter a valid email address.';
                } else if (field.type === 'url') {
                    feedback.textContent = 'Please enter a valid URL.';
                }
            } else if (field.validity.tooShort) {
                feedback.textContent = `Please enter at least ${field.minLength} characters.`;
            } else if (field.validity.tooLong) {
                feedback.textContent = `Please enter no more than ${field.maxLength} characters.`;
            } else if (field.validity.patternMismatch) {
                feedback.textContent = field.getAttribute('data-pattern-message') || 'Please match the requested format.';
            }
        }
    }
}

/**
 * Dynamic form fields for adding multiple entries
 */
function initDynamicFormFields() {
    // Add entry buttons
    const addButtons = document.querySelectorAll('[data-add-entry]');
    addButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = button.getAttribute('data-add-entry');
            const container = document.getElementById(targetId);
            
            if (container) {
                addFormEntry(container, button.getAttribute('data-entry-type'));
            }
        });
    });
    
    // Remove entry buttons (using event delegation)
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-remove-entry]') || e.target.closest('[data-remove-entry]')) {
            e.preventDefault();
            const button = e.target.matches('[data-remove-entry]') ? e.target : e.target.closest('[data-remove-entry]');
            const entry = button.closest('.dynamic-entry');
            
            if (entry) {
                // Confirm before removing
                if (confirm('Remove this entry?')) {
                    entry.remove();
                    updateEntryNumbers();
                }
            }
        }
    });
}

/**
 * Add a new form entry dynamically
 */
function addFormEntry(container, entryType) {
    const entryCount = container.querySelectorAll('.dynamic-entry').length;
    const newEntry = createFormEntry(entryType, entryCount);
    
    container.appendChild(newEntry);
    
    // Focus on first input of new entry
    const firstInput = newEntry.querySelector('input, textarea, select');
    if (firstInput) {
        firstInput.focus();
    }
    
    updateEntryNumbers();
}

/**
 * Create a new form entry based on type
 */
function createFormEntry(entryType, index) {
    const entry = document.createElement('div');
    entry.className = 'dynamic-entry card mb-3';
    
    let content = '';
    
    switch(entryType) {
        case 'experience':
            content = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="card-title mb-0">Experience #<span class="entry-number">${index + 1}</span></h5>
                        <button type="button" class="btn btn-sm btn-danger" data-remove-entry>
                            <i class="bi bi-trash"></i> Remove
                        </button>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Company</label>
                            <input type="text" class="form-control" name="experience_company_${index}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Role</label>
                            <input type="text" class="form-control" name="experience_role_${index}" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Start Date</label>
                            <input type="date" class="form-control" name="experience_start_${index}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">End Date</label>
                            <input type="date" class="form-control" name="experience_end_${index}">
                            <small class="text-muted">Leave blank if current position</small>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea class="form-control" name="experience_description_${index}" rows="3" required></textarea>
                    </div>
                </div>
            `;
            break;
            
        case 'education':
            content = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="card-title mb-0">Education #<span class="entry-number">${index + 1}</span></h5>
                        <button type="button" class="btn btn-sm btn-danger" data-remove-entry>
                            <i class="bi bi-trash"></i> Remove
                        </button>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Institution</label>
                            <input type="text" class="form-control" name="education_institution_${index}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Degree</label>
                            <input type="text" class="form-control" name="education_degree_${index}" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Field of Study</label>
                            <input type="text" class="form-control" name="education_field_${index}">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">Start Year</label>
                            <input type="number" class="form-control" name="education_start_year_${index}" min="1950" max="2100" required>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label class="form-label">End Year</label>
                            <input type="number" class="form-control" name="education_end_year_${index}" min="1950" max="2100">
                            <small class="text-muted">Leave blank if ongoing</small>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'skill':
            content = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="card-title mb-0">Skill #<span class="entry-number">${index + 1}</span></h5>
                        <button type="button" class="btn btn-sm btn-danger" data-remove-entry>
                            <i class="bi bi-trash"></i> Remove
                        </button>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Skill Name</label>
                            <input type="text" class="form-control" name="skill_name_${index}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Category</label>
                            <select class="form-select" name="skill_category_${index}" required>
                                <option value="">Select category...</option>
                                <option value="Technical">Technical</option>
                                <option value="Soft Skills">Soft Skills</option>
                                <option value="Languages">Languages</option>
                                <option value="Tools">Tools</option>
                            </select>
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'project':
            content = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="card-title mb-0">Project #<span class="entry-number">${index + 1}</span></h5>
                        <button type="button" class="btn btn-sm btn-danger" data-remove-entry>
                            <i class="bi bi-trash"></i> Remove
                        </button>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Project Name</label>
                            <input type="text" class="form-control" name="project_name_${index}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label class="form-label">Technologies</label>
                            <input type="text" class="form-control" name="project_technologies_${index}" placeholder="e.g., Python, Django, React">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Description</label>
                        <textarea class="form-control" name="project_description_${index}" rows="3" required></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">URL (optional)</label>
                        <input type="url" class="form-control" name="project_url_${index}" placeholder="https://...">
                    </div>
                </div>
            `;
            break;
    }
    
    entry.innerHTML = content;
    return entry;
}

/**
 * Update entry numbers after add/remove
 */
function updateEntryNumbers() {
    const containers = document.querySelectorAll('[data-entry-container]');
    containers.forEach(function(container) {
        const entries = container.querySelectorAll('.dynamic-entry');
        entries.forEach(function(entry, index) {
            const numberSpan = entry.querySelector('.entry-number');
            if (numberSpan) {
                numberSpan.textContent = index + 1;
            }
        });
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Character counter for text fields
 */
function initCharacterCounters() {
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'form-text text-muted character-counter';
        counter.textContent = `0 / ${maxLength} characters`;
        
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const currentLength = textarea.value.length;
            counter.textContent = `${currentLength} / ${maxLength} characters`;
            
            if (currentLength > maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
        });
    });
}

/**
 * Smooth scroll to top
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Export functions for use in other scripts
window.ATSResumeBuilder = {
    validateField: validateField,
    scrollToTop: scrollToTop,
    addFormEntry: addFormEntry
};


/**
 * Responsive Design Utilities
 */

// Detect device type
function getDeviceType() {
    const width = window.innerWidth;
    if (width < 576) return 'mobile';
    if (width < 768) return 'mobile-large';
    if (width < 992) return 'tablet';
    if (width < 1200) return 'desktop';
    return 'desktop-large';
}

// Detect touch device
function isTouchDevice() {
    return (('ontouchstart' in window) ||
            (navigator.maxTouchPoints > 0) ||
            (navigator.msMaxTouchPoints > 0));
}

// Add device class to body
function updateDeviceClass() {
    const deviceType = getDeviceType();
    const isTouch = isTouchDevice();
    
    document.body.className = document.body.className.replace(/device-\w+/g, '');
    document.body.classList.add(`device-${deviceType}`);
    
    if (isTouch) {
        document.body.classList.add('touch-device');
    } else {
        document.body.classList.add('no-touch');
    }
}

// Initialize responsive features
function initResponsiveFeatures() {
    updateDeviceClass();
    
    // Update on resize (debounced)
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            updateDeviceClass();
        }, 250);
    });
    
    // Handle orientation change
    window.addEventListener('orientationchange', function() {
        setTimeout(updateDeviceClass, 100);
    });
    
    // Mobile menu enhancements
    if (getDeviceType().includes('mobile')) {
        enhanceMobileMenu();
    }
    
    // Touch-friendly tables
    makeTablesResponsive();
    
    // Responsive images
    handleResponsiveImages();
}

/**
 * Enhance mobile menu
 */
function enhanceMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbarToggler || !navbarCollapse) return;
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!navbarToggler.contains(e.target) && 
            !navbarCollapse.contains(e.target) &&
            navbarCollapse.classList.contains('show')) {
            navbarToggler.click();
        }
    });
    
    // Close menu when clicking a link
    const navLinks = navbarCollapse.querySelectorAll('.nav-link');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            if (navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
    });
}

/**
 * Make tables responsive with horizontal scroll
 */
function makeTablesResponsive() {
    const tables = document.querySelectorAll('table:not(.table-responsive table)');
    tables.forEach(function(table) {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

/**
 * Handle responsive images
 */
function handleResponsiveImages() {
    const images = document.querySelectorAll('img:not([loading])');
    images.forEach(function(img) {
        // Add lazy loading
        img.setAttribute('loading', 'lazy');
        
        // Add responsive class if not present
        if (!img.classList.contains('img-fluid')) {
            img.classList.add('img-fluid');
        }
    });
}

/**
 * Viewport height fix for mobile browsers
 */
function setViewportHeight() {
    const vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

/**
 * Prevent zoom on input focus (iOS)
 */
function preventInputZoom() {
    if (isTouchDevice()) {
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
            // Ensure font size is at least 16px to prevent zoom
            const fontSize = window.getComputedStyle(input).fontSize;
            if (parseFloat(fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });
    }
}

/**
 * Smooth scroll polyfill for older browsers
 */
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Handle swipe gestures on mobile
 */
function initSwipeGestures() {
    if (!isTouchDevice()) return;
    
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left
                document.dispatchEvent(new CustomEvent('swipeleft'));
            } else {
                // Swipe right
                document.dispatchEvent(new CustomEvent('swiperight'));
            }
        }
    }
}

/**
 * Responsive font size adjustment
 */
function adjustFontSize() {
    const deviceType = getDeviceType();
    const root = document.documentElement;
    
    switch(deviceType) {
        case 'mobile':
            root.style.fontSize = '14px';
            break;
        case 'mobile-large':
            root.style.fontSize = '15px';
            break;
        case 'tablet':
            root.style.fontSize = '16px';
            break;
        default:
            root.style.fontSize = '16px';
    }
}

/**
 * Handle responsive modals
 */
function handleResponsiveModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('show.bs.modal', function() {
            if (getDeviceType().includes('mobile')) {
                // Full screen on mobile
                const dialog = modal.querySelector('.modal-dialog');
                if (dialog && !dialog.classList.contains('modal-fullscreen-sm-down')) {
                    dialog.classList.add('modal-fullscreen-sm-down');
                }
            }
        });
    });
}

/**
 * Initialize all responsive features on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    initResponsiveFeatures();
    setViewportHeight();
    preventInputZoom();
    initSmoothScroll();
    initSwipeGestures();
    adjustFontSize();
    handleResponsiveModals();
    
    // Update viewport height on resize
    window.addEventListener('resize', setViewportHeight);
    window.addEventListener('orientationchange', setViewportHeight);
});

// Export responsive utilities
window.ResponsiveUtils = {
    getDeviceType: getDeviceType,
    isTouchDevice: isTouchDevice,
    updateDeviceClass: updateDeviceClass
};
