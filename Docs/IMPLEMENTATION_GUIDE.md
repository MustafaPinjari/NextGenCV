# NextGenCV Implementation Guide

## Overview

This guide provides detailed implementation instructions for the NextGenCV UI/UX redesign. It covers the template folder structure, Bootstrap customization approach, SCSS architecture, and animation specifications.

## Table of Contents

1. [Template Folder Structure](#template-folder-structure)
2. [Bootstrap Customization](#bootstrap-customization)
3. [SCSS Architecture](#scss-architecture)
4. [Animation Specifications](#animation-specifications)
5. [Build Process](#build-process)
6. [Development Workflow](#development-workflow)

---

## Template Folder Structure

### Directory Organization

```
templates/
├── layouts/
│   ├── base.html                 # Base template with common HTML structure
│   ├── authenticated.html        # Layout for logged-in users
│   ├── public.html              # Layout for public pages
│   └── admin.html               # Layout for admin pages
│
├── partials/
│   ├── navigation/
│   │   ├── sidebar.html         # Sidebar navigation component
│   │   ├── topbar.html          # Top navigation bar component
│   │   └── footer.html          # Footer component
│   │
│   ├── components/
│   │   ├── button.html          # Button component variants
│   │   ├── card.html            # Card component variants
│   │   ├── form_input.html      # Form input with floating label
│   │   ├── modal.html           # Modal component
│   │   ├── alert.html           # Alert component
│   │   ├── toast.html           # Toast notification component
│   │   ├── progress_bar.html    # Linear progress bar
│   │   ├── circular_progress.html # Circular progress meter
│   │   ├── wizard_progress.html # Wizard step indicator
│   │   ├── empty_state.html     # Empty state component
│   │   ├── loading_spinner.html # Loading spinner
│   │   └── skeleton.html        # Skeleton screen
│   │
│   └── charts/
│       ├── line_chart.html      # Line chart configuration
│       ├── radar_chart.html     # Radar chart configuration
│       ├── bar_chart.html       # Bar chart configuration
│       └── donut_chart.html     # Donut chart configuration
│
├── authentication/
│   ├── login.html               # Login page
│   ├── register.html            # Registration page
│   └── password_reset.html      # Password reset page
│
├── resumes/
│   ├── resume_list.html         # Resume list page
│   ├── resume_wizard.html       # Resume builder wizard
│   ├── resume_preview.html      # Resume preview page
│   ├── version_history.html     # Version history page
│   └── wizard_steps/
│       ├── personal_info.html   # Step 1: Personal info
│       ├── experience.html      # Step 2: Experience
│       ├── education.html       # Step 3: Education
│       ├── skills.html          # Step 4: Skills
│       └── summary.html         # Step 5: Summary
│
├── analyzer/
│   ├── pdf_upload.html          # PDF upload page
│   ├── ats_analyzer.html        # ATS analyzer page
│   └── fix_comparison.html      # Fix comparison page
│
├── analytics/
│   └── dashboard.html           # Analytics dashboard
│
├── authentication/
│   ├── dashboard.html           # User dashboard
│   ├── settings.html            # Settings page
│   └── profile.html             # Profile page
│
├── admin/
│   ├── admin_dashboard.html     # Admin dashboard
│   ├── user_management.html     # User management
│   └── resume_management.html   # Resume management
│
├── errors/
│   ├── 404.html                 # 404 error page
│   └── 500.html                 # 500 error page
│
└── landing.html                 # Landing page
```

### Template Inheritance Pattern

**Base Template (base.html):**
```django
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}NextGenCV{% endblock %}</title>
    
    <!-- Design System CSS -->
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    
    {% block extra_css %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    {% block content %}{% endblock %}
    
    <!-- Core JavaScript -->
    <script src="{% static 'js/main.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

**Authenticated Layout (authenticated.html):**
```django
{% extends "layouts/base.html" %}

{% block body_class %}layout-authenticated{% endblock %}

{% block content %}
<div class="layout-wrapper">
    {% include "partials/navigation/sidebar.html" %}
    
    <div class="layout-main">
        {% include "partials/navigation/topbar.html" %}
        
        <main class="main-content">
            {% block page_content %}{% endblock %}
        </main>
    </div>
</div>
{% endblock %}
```

**Page Template (dashboard.html):**
```django
{% extends "layouts/authenticated.html" %}

{% block title %}Dashboard - NextGenCV{% endblock %}

{% block page_content %}
<div class="dashboard">
    <div class="welcome-header">
        <h1>Welcome back, {{ user.first_name }}!</h1>
        <p class="date">{{ current_date }}</p>
    </div>
    
    <!-- Dashboard content -->
</div>
{% endblock %}
```

---

## Bootstrap Customization

### Customization Strategy

We use Bootstrap 5 as a foundation but heavily customize it via SCSS overrides to match our design system. This approach provides:
- Robust grid system
- Utility classes
- Component base structure
- Accessibility features

While maintaining:
- Custom design tokens
- Unique visual style
- Dark theme
- Premium aesthetic

### Bootstrap Import Structure

**File:** `static/scss/_bootstrap-custom.scss`

```scss
// 1. Include functions first (required for variable overrides)
@import "~bootstrap/scss/functions";

// 2. Override Bootstrap variables with our design tokens
@import "tokens/colors";
@import "tokens/typography";
@import "tokens/spacing";

// Bootstrap variable overrides
$primary: $color-primary-solid;
$secondary: $color-secondary;
$success: $color-success;
$warning: $color-warning;
$danger: $color-error;

$body-bg: $color-base-bg;
$body-color: $color-text-primary;

$font-family-base: $font-primary;
$font-size-base: $font-size-base;

$border-radius: $radius-md;
$border-radius-sm: $radius-sm;
$border-radius-lg: $radius-lg;

$spacer: 1rem; // 16px base for Bootstrap spacing utilities

// 3. Include Bootstrap variables
@import "~bootstrap/scss/variables";

// 4. Include Bootstrap mixins
@import "~bootstrap/scss/mixins";

// 5. Include only the Bootstrap components we need
@import "~bootstrap/scss/root";
@import "~bootstrap/scss/reboot";
@import "~bootstrap/scss/type";
@import "~bootstrap/scss/grid";
@import "~bootstrap/scss/containers";
@import "~bootstrap/scss/forms";
@import "~bootstrap/scss/buttons";
@import "~bootstrap/scss/transitions";
@import "~bootstrap/scss/dropdown";
@import "~bootstrap/scss/nav";
@import "~bootstrap/scss/navbar";
@import "~bootstrap/scss/card";
@import "~bootstrap/scss/modal";
@import "~bootstrap/scss/utilities";

// 6. Include Bootstrap utilities API
@import "~bootstrap/scss/utilities/api";
```

### What We Include from Bootstrap

✅ **Include:**
- Grid system (container, row, col)
- Utility classes (spacing, display, flex)
- Form base structure
- Button base structure
- Modal base structure
- Transitions

❌ **Exclude:**
- Accordion (custom implementation)
- Alerts (custom implementation)
- Badges (custom implementation)
- Breadcrumb
- Carousel
- Close button (custom)
- Collapse (custom)
- List group
- Pagination (custom)
- Popovers
- Progress (custom)
- Spinners (custom)
- Toasts (custom)
- Tooltips (custom)

### Bootstrap Override Examples

**Buttons:**
```scss
// Override Bootstrap button styles
.btn {
  // Keep Bootstrap base structure
  // Override visual styles
  border-radius: $radius-lg;
  font-weight: $font-weight-semibold;
  transition: all $duration-normal $easing-default;
  
  &:focus {
    box-shadow: $glow-primary;
  }
}

.btn-primary {
  background: $color-primary;
  border: none;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(0, 102, 255, 0.5);
  }
}
```

**Forms:**
```scss
// Override Bootstrap form styles
.form-control {
  background: $color-surface;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  color: $color-text-primary;
  
  &:focus {
    background: $color-surface;
    border-color: $color-border-focus;
    box-shadow: $glow-primary;
    color: $color-text-primary;
  }
}
```

---

## SCSS Architecture

### File Structure

```
static/scss/
├── main.scss                    # Main entry point
├── _bootstrap-custom.scss       # Bootstrap customization
│
├── base/
│   ├── _reset.scss             # CSS reset
│   └── _global.scss            # Global styles
│
├── tokens/
│   ├── _colors.scss            # Color tokens
│   ├── _typography.scss        # Typography tokens
│   ├── _spacing.scss           # Spacing tokens
│   ├── _shadows.scss           # Shadow tokens
│   ├── _borders.scss           # Border radius tokens
│   └── _animations.scss        # Animation tokens
│
├── utilities/
│   ├── _mixins.scss            # SCSS mixins
│   └── _accessibility.scss     # Accessibility utilities
│
├── components/
│   ├── _buttons.scss           # Button components
│   ├── _cards.scss             # Card components
│   ├── _forms.scss             # Form components
│   ├── _navigation.scss        # Navigation components
│   ├── _progress.scss          # Progress components
│   ├── _feedback.scss          # Feedback components (alerts, toasts, modals)
│   └── _data-display.scss      # Data display components (tables, empty states)
│
├── layouts/
│   ├── _authenticated.scss     # Authenticated layout styles
│   ├── _public.scss            # Public layout styles
│   └── _admin.scss             # Admin layout styles
│
└── pages/
    ├── _landing.scss           # Landing page styles
    ├── _dashboard.scss         # Dashboard styles
    ├── _resume-list.scss       # Resume list styles
    ├── _resume-builder.scss    # Resume builder styles
    ├── _error-pages.scss       # Error page styles
    └── ... (other page-specific styles)
```

### Main SCSS Entry Point

**File:** `static/scss/main.scss`

```scss
// 1. Tokens (must be first)
@import 'tokens/colors';
@import 'tokens/typography';
@import 'tokens/spacing';
@import 'tokens/shadows';
@import 'tokens/borders';
@import 'tokens/animations';

// 2. Utilities
@import 'utilities/mixins';
@import 'utilities/accessibility';

// 3. Base styles
@import 'base/reset';
@import 'base/global';

// 4. Bootstrap customization
@import 'bootstrap-custom';

// 5. Layouts
@import 'layouts/authenticated';
@import 'layouts/public';
@import 'layouts/admin';

// 6. Components
@import 'components/buttons';
@import 'components/cards';
@import 'components/forms';
@import 'components/navigation';
@import 'components/progress';
@import 'components/feedback';
@import 'components/data-display';

// 7. Pages
@import 'pages/landing';
@import 'pages/dashboard';
@import 'pages/resume-list';
@import 'pages/resume-builder';
@import 'pages/error-pages';
```

### SCSS Naming Conventions

**BEM Methodology:**
- Block: `.card`
- Element: `.card__title`
- Modifier: `.card--elevated`

**Examples:**
```scss
// Block
.card {
  background: $color-surface;
  border-radius: $radius-xl;
  padding: $spacing-4;
}

// Element
.card__title {
  font-size: $font-size-2xl;
  font-weight: $font-weight-bold;
  margin-bottom: $spacing-2;
}

// Modifier
.card--elevated {
  box-shadow: $shadow-md;
  
  &:hover {
    transform: translateY(-4px);
  }
}
```

### Useful Mixins

**File:** `static/scss/utilities/_mixins.scss`

```scss
// Responsive breakpoint mixin
@mixin respond-to($breakpoint) {
  @if $breakpoint == 'sm' {
    @media (min-width: $breakpoint-sm) { @content; }
  }
  @else if $breakpoint == 'md' {
    @media (min-width: $breakpoint-md) { @content; }
  }
  @else if $breakpoint == 'lg' {
    @media (min-width: $breakpoint-lg) { @content; }
  }
  @else if $breakpoint == 'xl' {
    @media (min-width: $breakpoint-xl) { @content; }
  }
}

// Glow effect mixin
@mixin glow($color, $intensity: 0.3) {
  box-shadow: 0 0 20px rgba($color, $intensity);
}

// Hover lift effect mixin
@mixin hover-lift($distance: -2px) {
  transition: transform $duration-normal $easing-default;
  
  &:hover {
    transform: translateY($distance);
  }
}

// Truncate text mixin
@mixin truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

// Visually hidden (for accessibility)
@mixin visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

**Usage:**
```scss
.resume-card {
  @include hover-lift(-4px);
  @include glow($color-primary-solid, 0.2);
  
  @include respond-to('md') {
    width: 50%;
  }
}
```

---


## Animation Specifications

### Animation Principles

1. **Purposeful**: Every animation should have a clear purpose (feedback, guidance, delight)
2. **Subtle**: Animations should enhance, not distract
3. **Fast**: Keep durations between 150-250ms for micro-interactions
4. **Smooth**: Use appropriate easing functions
5. **Performant**: Use CSS transforms and opacity (GPU-accelerated)
6. **Accessible**: Respect `prefers-reduced-motion`

### Animation Types

#### 1. Micro-Interactions (150-250ms)

**Button Hover:**
```scss
.btn {
  transition: all $duration-normal $easing-default;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(0, 102, 255, 0.5);
  }
  
  &:active {
    transform: scale(0.98);
  }
}
```

**Input Focus:**
```scss
.form-input {
  transition: all $duration-normal $easing-default;
  
  &:focus {
    border-color: $color-border-focus;
    box-shadow: $glow-primary;
  }
}

.form-label {
  transition: all $duration-normal $easing-default;
  
  .form-input:focus + & {
    transform: translateY(-1.5rem) scale(0.85);
    color: $color-primary-solid;
  }
}
```

**Card Hover:**
```scss
.card-elevated {
  transition: all $duration-normal $easing-default;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-lg;
  }
}
```

#### 2. Page Transitions (250-350ms)

**Fade In:**
```scss
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.page-content {
  animation: fadeIn $duration-slow $easing-out;
}
```

**Slide In:**
```scss
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast {
  animation: slideInRight $duration-normal $easing-out;
}
```

#### 3. Loading Animations

**Spinner:**
```scss
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.spinner {
  animation: spin 1s linear infinite;
}
```

**Skeleton Shimmer:**
```scss
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    $color-surface 0%,
    $color-surface-elevated 50%,
    $color-surface 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite;
}
```

**Pulse (for CTA buttons):**
```scss
@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 30px rgba(0, 102, 255, 0.4);
  }
  50% {
    box-shadow: 0 0 40px rgba(0, 102, 255, 0.5);
  }
}

.btn-gradient {
  animation: pulse 2s infinite;
}
```

#### 4. Progress Animations

**Linear Progress:**
```scss
.progress-bar {
  transition: width $duration-slow $easing-default;
}
```

**Circular Progress:**
```scss
.progress-fill {
  stroke-dasharray: 339.292;
  stroke-dashoffset: 339.292;
  transition: stroke-dashoffset $duration-slow $easing-default;
}

// JavaScript sets stroke-dashoffset based on percentage
// strokeDashoffset = circumference - (percentage / 100 * circumference)
```

**Score Reveal:**
```scss
@keyframes countUp {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.score-value {
  animation: countUp $duration-slow $easing-bounce;
}

// JavaScript animates the number from 0 to actual value
```

#### 5. Modal Animations

**Modal Backdrop:**
```scss
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-backdrop {
  animation: fadeIn 200ms $easing-default;
}
```

**Modal Content:**
```scss
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal {
  animation: modalSlideIn $duration-normal $easing-bounce;
}
```

#### 6. Wizard Step Transitions

**Step Change:**
```scss
@keyframes slideOutLeft {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(-100%);
    opacity: 0;
  }
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.wizard-step-exit {
  animation: slideOutLeft $duration-normal $easing-in;
}

.wizard-step-enter {
  animation: slideInRight $duration-normal $easing-out;
}
```

#### 7. Chart Animations

**Chart.js Configuration:**
```javascript
const chartOptions = {
  animation: {
    duration: 750,
    easing: 'easeOutQuart',
    onComplete: function() {
      // Animation complete callback
    }
  }
};
```

**Stagger Animation for Multiple Charts:**
```scss
.chart-container {
  opacity: 0;
  animation: fadeIn $duration-slow $easing-out forwards;
  
  &:nth-child(1) { animation-delay: 0ms; }
  &:nth-child(2) { animation-delay: 100ms; }
  &:nth-child(3) { animation-delay: 200ms; }
  &:nth-child(4) { animation-delay: 300ms; }
}
```

### Accessibility: Reduced Motion

**Always respect user preferences:**

```scss
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### JavaScript Animation Helpers

**File:** `static/js/animations.js`

```javascript
// Animate number count-up
function animateValue(element, start, end, duration) {
  const range = end - start;
  const increment = range / (duration / 16); // 60fps
  let current = start;
  
  const timer = setInterval(() => {
    current += increment;
    if (current >= end) {
      current = end;
      clearInterval(timer);
    }
    element.textContent = Math.round(current);
  }, 16);
}

// Animate circular progress
function animateCircularProgress(element, percentage) {
  const circle = element.querySelector('.progress-fill');
  const circumference = 2 * Math.PI * 54; // radius = 54
  const offset = circumference - (percentage / 100 * circumference);
  
  circle.style.strokeDashoffset = offset;
}

// Stagger animation for list items
function staggerAnimation(elements, delay = 100) {
  elements.forEach((element, index) => {
    element.style.animationDelay = `${index * delay}ms`;
    element.classList.add('animate-in');
  });
}

// Intersection Observer for scroll animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observe elements
document.querySelectorAll('.animate-on-scroll').forEach(el => {
  observer.observe(el);
});
```

---

## Build Process

### SCSS Compilation

**Using Django Compressor:**

1. **Install Django Compressor:**
```bash
pip install django-compressor
```

2. **Configure in settings.py:**
```python
INSTALLED_APPS = [
    # ...
    'compressor',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True  # For production

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
```

3. **In templates:**
```django
{% load compress %}

{% compress css %}
<link rel="stylesheet" type="text/x-scss" href="{% static 'scss/main.scss' %}">
{% endcompress %}
```

**Alternative: Using Node.js/npm:**

1. **Install dependencies:**
```bash
npm install --save-dev sass autoprefixer postcss-cli
```

2. **Add npm scripts to package.json:**
```json
{
  "scripts": {
    "build:css": "sass static/scss/main.scss static/css/main.css",
    "watch:css": "sass --watch static/scss/main.scss static/css/main.css",
    "prefix:css": "postcss static/css/main.css --use autoprefixer -o static/css/main.css",
    "build": "npm run build:css && npm run prefix:css"
  }
}
```

3. **Run build:**
```bash
npm run build
```

### Asset Optimization

**CSS Minification:**
```bash
npm install --save-dev cssnano
postcss static/css/main.css --use cssnano -o static/css/main.min.css
```

**JavaScript Minification:**
```bash
npm install --save-dev terser
terser static/js/main.js -o static/js/main.min.js --compress --mangle
```

**Image Optimization:**
```bash
npm install --save-dev imagemin-cli
imagemin static/images/* --out-dir=static/images/optimized
```

**Gzip Compression:**
```python
# Django middleware
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    # ... other middleware
]
```

---

## Development Workflow

### Local Development Setup

1. **Clone repository:**
```bash
git clone <repository-url>
cd nextgencv
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
npm install  # If using Node.js for SCSS compilation
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Compile SCSS:**
```bash
npm run watch:css  # Watches for changes
# OR
python manage.py compilescss  # If using Django compressor
```

6. **Run development server:**
```bash
python manage.py runserver
```

### Development Best Practices

**1. Component-First Development:**
- Build components in isolation first
- Test components independently
- Document component usage
- Then integrate into pages

**2. Mobile-First Approach:**
- Design for mobile first
- Enhance for larger screens
- Test at all breakpoints
- Use responsive images

**3. Accessibility Testing:**
- Test with keyboard navigation
- Test with screen readers
- Check color contrast
- Validate HTML semantics

**4. Performance Monitoring:**
- Use Lighthouse audits
- Monitor Core Web Vitals
- Optimize images
- Minimize CSS/JS

**5. Version Control:**
- Commit compiled CSS to repository
- Use meaningful commit messages
- Create feature branches
- Review before merging

### Code Review Checklist

**Before submitting a pull request:**

✅ SCSS follows BEM naming conventions
✅ Design tokens used (no arbitrary values)
✅ Responsive at all breakpoints
✅ Accessible (keyboard, screen reader, contrast)
✅ Animations respect prefers-reduced-motion
✅ No console errors
✅ Lighthouse score > 90
✅ Cross-browser tested
✅ Documentation updated

### Testing Workflow

**1. Visual Testing:**
```bash
# Run visual regression tests
npm run test:visual
```

**2. Accessibility Testing:**
```bash
# Run accessibility audit
npm run test:a11y
```

**3. Performance Testing:**
```bash
# Run Lighthouse
npm run test:performance
```

**4. Cross-Browser Testing:**
- Test on Chrome, Firefox, Safari, Edge
- Test on mobile browsers
- Use BrowserStack for comprehensive testing

---

## Troubleshooting

### Common Issues

**Issue: SCSS not compiling**
- Check SCSS syntax errors
- Verify file paths in imports
- Ensure SCSS compiler is installed
- Check for circular imports

**Issue: Styles not applying**
- Clear browser cache
- Check CSS specificity
- Verify class names match
- Inspect element in DevTools

**Issue: Animations not working**
- Check browser support
- Verify animation syntax
- Check for JavaScript errors
- Test with prefers-reduced-motion disabled

**Issue: Layout breaking on mobile**
- Test at actual breakpoints
- Check for fixed widths
- Verify responsive utilities
- Test on real devices

**Issue: Performance issues**
- Optimize images
- Minify CSS/JS
- Remove unused CSS
- Enable compression

---

## Production Deployment

### Pre-Deployment Checklist

✅ All SCSS compiled to CSS
✅ CSS minified
✅ JavaScript minified
✅ Images optimized
✅ Gzip compression enabled
✅ Cache headers configured
✅ CDN configured (if applicable)
✅ All tests passing
✅ Lighthouse score > 90
✅ Cross-browser tested
✅ Accessibility audit passed

### Django Production Settings

```python
# settings.py (production)

DEBUG = False

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Compression
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# Cache static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Deployment Commands

```bash
# 1. Compile SCSS
npm run build

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run migrations
python manage.py migrate

# 4. Restart application server
# (depends on your hosting setup)
```

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review performance metrics
- Check error logs
- Monitor user feedback
- Update dependencies (security patches)

**Monthly:**
- Run full accessibility audit
- Review and optimize CSS bundle size
- Update documentation
- Review and refactor code

**Quarterly:**
- Major dependency updates
- Design system review
- User testing sessions
- Performance optimization sprint

---

## Resources

### Documentation
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [SCSS Documentation](https://sass-lang.com/documentation)
- [MDN Web Docs](https://developer.mozilla.org/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Tools
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [BrowserStack](https://www.browserstack.com/)
- [Can I Use](https://caniuse.com/)

### Design Resources
- [Coolors](https://coolors.co/) - Color palette generator
- [Google Fonts](https://fonts.google.com/) - Web fonts
- [Feather Icons](https://feathericons.com/) - Icon library
- [Heroicons](https://heroicons.com/) - Icon library

---

## Version History

- **v1.0.0** (2026-02-15): Initial implementation guide
