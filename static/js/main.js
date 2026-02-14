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
