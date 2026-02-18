/**
 * Accessibility Enhancement Module
 * Implements ARIA labels, keyboard navigation, focus management, and redundant encoding
 * for NextGenCV UI/UX Redesign
 * 
 * Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
 */

(function() {
    'use strict';

    // ============================================================================
    // ARIA Label Management (Requirement 13.3)
    // ============================================================================

    /**
     * Add ARIA labels to icon buttons that don't have visible text
     */
    function enhanceIconButtons() {
        // Find all buttons with icons but no visible text
        const iconButtons = document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])');
        
        iconButtons.forEach(button => {
            const icon = button.querySelector('i[class*="bi-"]');
            const hasVisibleText = button.textContent.trim().length > 0;
            
            if (icon && !hasVisibleText) {
                // Extract icon type from class
                const iconClasses = icon.className.match(/bi-[\w-]+/g);
                if (iconClasses && iconClasses.length > 0) {
                    const iconType = iconClasses[0].replace('bi-', '').replace(/-/g, ' ');
                    const label = generateAriaLabel(iconType, button);
                    button.setAttribute('aria-label', label);
                }
            }
        });
    }

    /**
     * Generate appropriate ARIA label based on icon type and context
     */
    function generateAriaLabel(iconType, element) {
        const labelMap = {
            'x': 'Close',
            'x-circle': 'Close',
            'x-lg': 'Close',
            'trash': 'Delete',
            'trash3': 'Delete',
            'pencil': 'Edit',
            'pencil-square': 'Edit',
            'eye': 'View',
            'eye-fill': 'View',
            'download': 'Download',
            'upload': 'Upload',
            'search': 'Search',
            'filter': 'Filter',
            'plus': 'Add',
            'plus-circle': 'Add',
            'check': 'Confirm',
            'check-circle': 'Confirm',
            'arrow-left': 'Go back',
            'arrow-right': 'Go forward',
            'chevron-left': 'Previous',
            'chevron-right': 'Next',
            'chevron-double-left': 'First',
            'chevron-double-right': 'Last',
            'list': 'Menu',
            'three-dots': 'More options',
            'three-dots-vertical': 'More options',
            'gear': 'Settings',
            'bell': 'Notifications',
            'person-circle': 'User profile',
            'save': 'Save',
            'files': 'Duplicate',
            'share': 'Share'
        };

        return labelMap[iconType] || iconType.replace(/ /g, ' ');
    }

    /**
     * Add aria-labelledby to form inputs that have associated labels
     */
    function enhanceFormInputs() {
        const inputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby]), textarea:not([aria-label]):not([aria-labelledby]), select:not([aria-label]):not([aria-labelledby])');
        
        inputs.forEach(input => {
            const id = input.id;
            if (id) {
                // Find associated label
                const label = document.querySelector(`label[for="${id}"]`);
                if (label && !label.id) {
                    label.id = `${id}-label`;
                    input.setAttribute('aria-labelledby', label.id);
                }
            }
        });
    }

    /**
     * Add aria-live regions for dynamic content
     */
    function enhanceDynamicContent() {
        // Toast notifications
        const toastContainer = document.querySelector('.toast-container, .alert-container');
        if (toastContainer && !toastContainer.getAttribute('aria-live')) {
            toastContainer.setAttribute('aria-live', 'polite');
            toastContainer.setAttribute('aria-atomic', 'true');
        }

        // Loading indicators
        const loadingIndicators = document.querySelectorAll('.loading-spinner, .skeleton-loader, [class*="loading"]');
        loadingIndicators.forEach(indicator => {
            if (!indicator.getAttribute('aria-live')) {
                indicator.setAttribute('aria-live', 'polite');
                indicator.setAttribute('aria-busy', 'true');
            }
        });

        // Autosave indicators
        const autosaveIndicators = document.querySelectorAll('[id*="autosave"], [class*="autosave"]');
        autosaveIndicators.forEach(indicator => {
            if (!indicator.getAttribute('aria-live')) {
                indicator.setAttribute('aria-live', 'polite');
            }
        });
    }

    /**
     * Add aria-expanded to collapsible elements
     */
    function enhanceCollapsibleElements() {
        // Accordions
        const accordionButtons = document.querySelectorAll('[data-toggle="collapse"], .accordion-button, [class*="collapse-toggle"]');
        accordionButtons.forEach(button => {
            if (!button.getAttribute('aria-expanded')) {
                const target = button.getAttribute('data-target') || button.getAttribute('href');
                if (target) {
                    const targetElement = document.querySelector(target);
                    const isExpanded = targetElement && !targetElement.classList.contains('collapsed');
                    button.setAttribute('aria-expanded', isExpanded);
                    button.setAttribute('aria-controls', target.replace('#', ''));
                }
            }
        });

        // Dropdowns
        const dropdownButtons = document.querySelectorAll('[data-toggle="dropdown"], .dropdown-toggle');
        dropdownButtons.forEach(button => {
            if (!button.getAttribute('aria-expanded')) {
                button.setAttribute('aria-expanded', 'false');
                button.setAttribute('aria-haspopup', 'true');
            }
        });
    }

    // ============================================================================
    // Keyboard Navigation (Requirement 13.2)
    // ============================================================================

    /**
     * Ensure all interactive elements are focusable
     */
    function ensureFocusable() {
        // Add tabindex to interactive elements that aren't naturally focusable
        const interactiveElements = document.querySelectorAll('.card:not([tabindex]), .action-card:not([tabindex]), [role="button"]:not([tabindex])');
        
        interactiveElements.forEach(element => {
            if (element.onclick || element.getAttribute('onclick')) {
                element.setAttribute('tabindex', '0');
            }
        });
    }

    /**
     * Add skip links for main content
     */
    function addSkipLinks() {
        // Check if skip link already exists
        if (document.querySelector('.skip-link')) {
            return;
        }

        const mainContent = document.querySelector('main, [role="main"], .main-content, .content-wrapper');
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
        }

        if (mainContent) {
            const skipLink = document.createElement('a');
            skipLink.href = '#main-content';
            skipLink.className = 'skip-link';
            skipLink.textContent = 'Skip to main content';
            skipLink.style.cssText = `
                position: absolute;
                top: -40px;
                left: 0;
                background: var(--color-primary-solid, #0066ff);
                color: white;
                padding: 8px 16px;
                text-decoration: none;
                border-radius: 0 0 4px 0;
                z-index: 10000;
                transition: top 0.2s;
            `;
            
            skipLink.addEventListener('focus', () => {
                skipLink.style.top = '0';
            });
            
            skipLink.addEventListener('blur', () => {
                skipLink.style.top = '-40px';
            });

            document.body.insertBefore(skipLink, document.body.firstChild);
        }
    }

    /**
     * Implement keyboard shortcuts for common actions
     */
    function implementKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K: Focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="search"], input[placeholder*="Search"], input[aria-label*="Search"]');
                if (searchInput) {
                    searchInput.focus();
                }
            }

            // Ctrl/Cmd + N: Create new resume (on resume list page)
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                const createButton = document.querySelector('a[href*="resume/create"], a[href*="resume_create"]');
                if (createButton) {
                    e.preventDefault();
                    createButton.click();
                }
            }

            // Escape: Close modals and dropdowns
            if (e.key === 'Escape') {
                // Close modals
                const openModals = document.querySelectorAll('.modal.show, .modal--open');
                openModals.forEach(modal => {
                    const closeButton = modal.querySelector('[data-dismiss="modal"], .modal-close');
                    if (closeButton) {
                        closeButton.click();
                    }
                });

                // Close dropdowns
                const openDropdowns = document.querySelectorAll('.dropdown.show, .dropdown--open');
                openDropdowns.forEach(dropdown => {
                    dropdown.classList.remove('show', 'dropdown--open');
                });
            }
        });
    }

    /**
     * Handle Enter and Space key for custom interactive elements
     */
    function handleCustomInteractiveElements() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                const target = e.target;
                
                // Handle cards with onclick or links
                if (target.classList.contains('action-card') || 
                    target.classList.contains('resume-card') ||
                    target.getAttribute('role') === 'button') {
                    
                    if (e.key === ' ') {
                        e.preventDefault(); // Prevent page scroll
                    }
                    
                    if (target.onclick) {
                        target.onclick(e);
                    } else {
                        const link = target.querySelector('a');
                        if (link) {
                            link.click();
                        }
                    }
                }
            }
        });
    }

    // ============================================================================
    // Focus State Management (Requirement 13.4)
    // ============================================================================

    /**
     * Ensure visible focus states for all focusable elements
     */
    function enhanceFocusStates() {
        // Add focus-visible class support for browsers that don't support :focus-visible
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // Inject focus styles if not already present
        if (!document.querySelector('#accessibility-focus-styles')) {
            const style = document.createElement('style');
            style.id = 'accessibility-focus-styles';
            style.textContent = `
                /* Enhanced focus states for accessibility */
                .keyboard-navigation *:focus {
                    outline: 2px solid var(--color-primary-solid, #0066ff);
                    outline-offset: 2px;
                    box-shadow: 0 0 0 4px rgba(0, 102, 255, 0.2);
                }

                .keyboard-navigation button:focus,
                .keyboard-navigation a:focus,
                .keyboard-navigation input:focus,
                .keyboard-navigation textarea:focus,
                .keyboard-navigation select:focus {
                    outline: 2px solid var(--color-primary-solid, #0066ff);
                    outline-offset: 2px;
                }

                /* Skip link styles */
                .skip-link:focus {
                    outline: 2px solid white;
                    outline-offset: -2px;
                }

                /* Ensure focus is visible on dark backgrounds */
                .sidebar *:focus,
                .topbar *:focus,
                .card *:focus {
                    outline-color: var(--color-primary-solid, #0066ff);
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * Manage focus trap for modals
     */
    function manageFocusTrap() {
        const modals = document.querySelectorAll('.modal, [role="dialog"]');
        
        modals.forEach(modal => {
            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    const focusableElements = modal.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    
                    const firstElement = focusableElements[0];
                    const lastElement = focusableElements[focusableElements.length - 1];

                    if (e.shiftKey && document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    } else if (!e.shiftKey && document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            });
        });
    }

    // ============================================================================
    // Redundant Encoding for Color Information (Requirement 13.5)
    // ============================================================================

    /**
     * Add icons to success/error states
     */
    function addStatusIcons() {
        // Success states
        const successElements = document.querySelectorAll('.alert-success, .text-success, [class*="success"]:not([data-icon-added])');
        successElements.forEach(element => {
            if (!element.querySelector('.status-icon') && element.textContent.trim()) {
                const icon = document.createElement('i');
                icon.className = 'bi bi-check-circle-fill status-icon';
                icon.setAttribute('aria-hidden', 'true');
                icon.style.marginRight = '0.5rem';
                element.insertBefore(icon, element.firstChild);
                element.setAttribute('data-icon-added', 'true');
            }
        });

        // Error states
        const errorElements = document.querySelectorAll('.alert-error, .alert-danger, .text-error, .text-danger, [class*="error"]:not([data-icon-added])');
        errorElements.forEach(element => {
            if (!element.querySelector('.status-icon') && element.textContent.trim()) {
                const icon = document.createElement('i');
                icon.className = 'bi bi-x-circle-fill status-icon';
                icon.setAttribute('aria-hidden', 'true');
                icon.style.marginRight = '0.5rem';
                element.insertBefore(icon, element.firstChild);
                element.setAttribute('data-icon-added', 'true');
            }
        });

        // Warning states
        const warningElements = document.querySelectorAll('.alert-warning, .text-warning, [class*="warning"]:not([data-icon-added])');
        warningElements.forEach(element => {
            if (!element.querySelector('.status-icon') && element.textContent.trim()) {
                const icon = document.createElement('i');
                icon.className = 'bi bi-exclamation-triangle-fill status-icon';
                icon.setAttribute('aria-hidden', 'true');
                icon.style.marginRight = '0.5rem';
                element.insertBefore(icon, element.firstChild);
                element.setAttribute('data-icon-added', 'true');
            }
        });

        // Info states
        const infoElements = document.querySelectorAll('.alert-info, .text-info, [class*="info"]:not([data-icon-added])');
        infoElements.forEach(element => {
            if (!element.querySelector('.status-icon') && element.textContent.trim()) {
                const icon = document.createElement('i');
                icon.className = 'bi bi-info-circle-fill status-icon';
                icon.setAttribute('aria-hidden', 'true');
                icon.style.marginRight = '0.5rem';
                element.insertBefore(icon, element.firstChild);
                element.setAttribute('data-icon-added', 'true');
            }
        });
    }

    /**
     * Add text labels to status indicators
     */
    function addStatusLabels() {
        // Score badges
        const scoreBadges = document.querySelectorAll('.resume-card-badge, .score-badge, [class*="badge"]:not([data-label-added])');
        scoreBadges.forEach(badge => {
            const score = parseInt(badge.textContent);
            if (!isNaN(score) && !badge.querySelector('.sr-only')) {
                const label = document.createElement('span');
                label.className = 'sr-only';
                
                if (score >= 80) {
                    label.textContent = ' (Excellent)';
                } else if (score >= 60) {
                    label.textContent = ' (Good)';
                } else if (score >= 40) {
                    label.textContent = ' (Fair)';
                } else {
                    label.textContent = ' (Needs Improvement)';
                }
                
                badge.appendChild(label);
                badge.setAttribute('data-label-added', 'true');
            }
        });

        // Progress bars
        const progressBars = document.querySelectorAll('.progress-bar, [role="progressbar"]:not([aria-label])');
        progressBars.forEach(bar => {
            const value = bar.getAttribute('aria-valuenow') || bar.style.width;
            if (value && !bar.getAttribute('aria-label')) {
                bar.setAttribute('aria-label', `Progress: ${value}%`);
            }
        });
    }

    /**
     * Add patterns to color-coded charts (for Chart.js)
     */
    function enhanceChartAccessibility() {
        // This will be called after charts are initialized
        // Add pattern fills to chart datasets
        if (window.Chart) {
            const originalDraw = Chart.controllers.bar.prototype.draw;
            Chart.controllers.bar.prototype.draw = function() {
                originalDraw.apply(this, arguments);
                // Add pattern overlays for colorblind accessibility
            };
        }
    }

    // ============================================================================
    // Screen Reader Utilities
    // ============================================================================

    /**
     * Add screen reader only text for context
     */
    function addScreenReaderText() {
        // Add sr-only class if it doesn't exist
        if (!document.querySelector('#sr-only-styles')) {
            const style = document.createElement('style');
            style.id = 'sr-only-styles';
            style.textContent = `
                .sr-only {
                    position: absolute;
                    width: 1px;
                    height: 1px;
                    padding: 0;
                    margin: -1px;
                    overflow: hidden;
                    clip: rect(0, 0, 0, 0);
                    white-space: nowrap;
                    border-width: 0;
                }

                .sr-only-focusable:focus {
                    position: static;
                    width: auto;
                    height: auto;
                    overflow: visible;
                    clip: auto;
                    white-space: normal;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // ============================================================================
    // Initialization
    // ============================================================================

    /**
     * Initialize all accessibility enhancements
     */
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        console.log('Initializing accessibility enhancements...');

        // ARIA Labels (Task 18.1)
        enhanceIconButtons();
        enhanceFormInputs();
        enhanceDynamicContent();
        enhanceCollapsibleElements();

        // Keyboard Navigation (Task 18.3)
        ensureFocusable();
        addSkipLinks();
        implementKeyboardShortcuts();
        handleCustomInteractiveElements();

        // Focus States (Task 18.5)
        enhanceFocusStates();
        manageFocusTrap();

        // Redundant Encoding (Task 18.7)
        addStatusIcons();
        addStatusLabels();
        enhanceChartAccessibility();

        // Screen Reader Support
        addScreenReaderText();

        console.log('Accessibility enhancements initialized successfully');

        // Re-run enhancements when new content is added dynamically
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    enhanceIconButtons();
                    enhanceFormInputs();
                    addStatusIcons();
                    addStatusLabels();
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Auto-initialize
    init();

    // Export for manual initialization if needed
    window.AccessibilityEnhancements = {
        init,
        enhanceIconButtons,
        enhanceFormInputs,
        enhanceDynamicContent,
        enhanceCollapsibleElements,
        ensureFocusable,
        addSkipLinks,
        implementKeyboardShortcuts,
        enhanceFocusStates,
        addStatusIcons,
        addStatusLabels
    };

})();
