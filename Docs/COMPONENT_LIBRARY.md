# NextGenCV Component Library

## Overview

The NextGenCV Component Library is a comprehensive collection of reusable UI components built on the design system foundation. Each component follows consistent patterns, supports multiple variants and states, and is designed for accessibility and performance.

## Table of Contents

1. [Buttons](#buttons)
2. [Cards](#cards)
3. [Form Inputs](#form-inputs)
4. [Navigation](#navigation)
5. [Progress Indicators](#progress-indicators)
6. [Feedback Components](#feedback-components)
7. [Data Display](#data-display)
8. [Usage Guidelines](#usage-guidelines)

---

## Buttons

Buttons are the primary way users take actions in the application.

### Variants

#### 1. Primary Button

The main call-to-action button with gradient background and glow effect.

**Visual Specifications:**
- Background: `$color-primary` gradient (135deg, #0066ff to #00ccff)
- Text: White (#ffffff)
- Padding: `$spacing-2` `$spacing-4` (16px 32px)
- Border radius: `$radius-lg` (16px)
- Font weight: `$font-weight-semibold` (600)
- Box shadow: `$glow-primary`

**States:**
- **Default**: Gradient background with subtle glow
- **Hover**: Lift effect (translateY(-2px)) + enhanced glow
- **Active**: Scale down (scale(0.98))
- **Focus**: Blue border with glow
- **Disabled**: Opacity 0.5, no interaction
- **Loading**: Spinner replaces text, button disabled

**Code Example:**
```html
<!-- Default -->
<button class="btn btn-primary">Sign Up</button>

<!-- With icon -->
<button class="btn btn-primary">
  <i class="icon-plus"></i>
  Create Resume
</button>

<!-- Loading state -->
<button class="btn btn-primary" disabled>
  <span class="spinner"></span>
  Processing...
</button>

<!-- Disabled -->
<button class="btn btn-primary" disabled>Unavailable</button>
```

**SCSS:**
```scss
.btn-primary {
  background: $color-primary;
  color: #ffffff;
  padding: $spacing-2 $spacing-4;
  border-radius: $radius-lg;
  font-weight: $font-weight-semibold;
  box-shadow: $glow-primary;
  transition: all $duration-normal $easing-default;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 0 30px rgba(0, 102, 255, 0.5);
  }
  
  &:active:not(:disabled) {
    transform: scale(0.98);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}
```

**When to Use:**
- Primary actions (Sign Up, Create, Submit)
- One primary button per section
- Most important action on the page

---

#### 2. Ghost Button

Transparent button with border, used for secondary actions.

**Visual Specifications:**
- Background: Transparent
- Border: 1px solid `$color-border`
- Text: `$color-text-primary`
- Padding: `$spacing-2` `$spacing-4`
- Border radius: `$radius-lg`

**States:**
- **Default**: Transparent with subtle border
- **Hover**: Background `$color-surface-elevated` + border glow
- **Active**: Slight scale down
- **Focus**: Blue border with glow
- **Disabled**: Opacity 0.5

**Code Example:**
```html
<button class="btn btn-ghost">Learn More</button>
<button class="btn btn-ghost">Cancel</button>
```

**SCSS:**
```scss
.btn-ghost {
  background: transparent;
  border: 1px solid $color-border;
  color: $color-text-primary;
  padding: $spacing-2 $spacing-4;
  border-radius: $radius-lg;
  transition: all $duration-normal $easing-default;
  
  &:hover:not(:disabled) {
    background: $color-surface-elevated;
    border-color: $color-border-hover;
  }
}
```

**When to Use:**
- Secondary actions (Cancel, Back, Learn More)
- Multiple actions in a group
- Less important actions

---

#### 3. Outline Button

Button with colored border, used for tertiary actions.

**Visual Specifications:**
- Background: Transparent
- Border: 2px solid `$color-primary-solid`
- Text: `$color-primary-solid`
- Padding: `$spacing-2` `$spacing-4`
- Border radius: `$radius-lg`

**States:**
- **Default**: Transparent with colored border
- **Hover**: Background `$color-primary-solid` + text white
- **Active**: Slight scale down
- **Focus**: Enhanced border glow

**Code Example:**
```html
<button class="btn btn-outline">View Details</button>
```

**SCSS:**
```scss
.btn-outline {
  background: transparent;
  border: 2px solid $color-primary-solid;
  color: $color-primary-solid;
  padding: $spacing-2 $spacing-4;
  border-radius: $radius-lg;
  transition: all $duration-normal $easing-default;
  
  &:hover:not(:disabled) {
    background: $color-primary-solid;
    color: #ffffff;
  }
}
```

**When to Use:**
- Tertiary actions
- Alternative to ghost buttons
- When you need more visual weight than ghost

---

#### 4. Gradient Button (CTA)

Special button with enhanced gradient and pulse animation for critical CTAs.

**Visual Specifications:**
- Background: `$color-primary` gradient
- Box shadow: Enhanced `$glow-primary`
- Padding: `$spacing-3` `$spacing-5` (24px 40px)
- Border radius: `$radius-xl` (20px)
- Font size: `$font-size-lg`
- Animation: Subtle pulse on idle

**States:**
- **Default**: Gradient with pulse animation
- **Hover**: Enhanced glow + lift
- **Active**: Scale down
- **Focus**: Blue border with glow

**Code Example:**
```html
<button class="btn btn-gradient">Get Started Free</button>
<button class="btn btn-gradient">Fix My Resume</button>
```

**SCSS:**
```scss
.btn-gradient {
  background: $color-primary;
  box-shadow: 0 0 30px rgba(0, 102, 255, 0.4);
  padding: $spacing-3 $spacing-5;
  border-radius: $radius-xl;
  font-size: $font-size-lg;
  color: #ffffff;
  animation: pulse 2s infinite;
  transition: all $duration-normal $easing-default;
  
  &:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 0 40px rgba(0, 102, 255, 0.6);
  }
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 30px rgba(0, 102, 255, 0.4); }
  50% { box-shadow: 0 0 40px rgba(0, 102, 255, 0.5); }
}
```

**When to Use:**
- Critical CTAs (Sign Up, Get Started)
- One per page maximum
- Hero sections and conversion points

---

### Button Sizes

Buttons come in three sizes:

```html
<!-- Small -->
<button class="btn btn-primary btn-sm">Small</button>

<!-- Default (no size class needed) -->
<button class="btn btn-primary">Default</button>

<!-- Large -->
<button class="btn btn-primary btn-lg">Large</button>
```

**Size Specifications:**
- **Small**: Padding `$spacing-1` `$spacing-3` (8px 24px), font-size `$font-size-sm`
- **Default**: Padding `$spacing-2` `$spacing-4` (16px 32px), font-size `$font-size-base`
- **Large**: Padding `$spacing-3` `$spacing-5` (24px 40px), font-size `$font-size-lg`

---

## Cards

Cards are containers for grouping related content.

### Variants

#### 1. Default Card

Standard card for general content.

**Visual Specifications:**
- Background: `$color-surface`
- Border: 1px solid `$color-border`
- Border radius: `$radius-xl` (20px)
- Padding: `$spacing-4` (32px)
- Shadow: `$shadow-sm`

**Code Example:**
```html
<div class="card">
  <h3 class="card-title">Card Title</h3>
  <p class="card-text">Card content goes here.</p>
  <button class="btn btn-primary">Action</button>
</div>
```

**SCSS:**
```scss
.card {
  background: $color-surface;
  border: 1px solid $color-border;
  border-radius: $radius-xl;
  padding: $spacing-4;
  box-shadow: $shadow-sm;
}
```

**When to Use:**
- General content containers
- Resume cards
- Feature cards

---

#### 2. Elevated Card

Card with enhanced shadow for emphasis.

**Visual Specifications:**
- Background: `$color-surface-elevated`
- Border: 1px solid `$color-border`
- Border radius: `$radius-xl`
- Padding: `$spacing-5` (40px)
- Shadow: `$shadow-md`
- Hover: Lift effect + enhanced shadow

**Code Example:**
```html
<div class="card card-elevated">
  <h3 class="card-title">Important Content</h3>
  <p class="card-text">This card stands out more.</p>
</div>
```

**SCSS:**
```scss
.card-elevated {
  background: $color-surface-elevated;
  padding: $spacing-5;
  box-shadow: $shadow-md;
  transition: all $duration-normal $easing-default;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-lg;
  }
}
```

**When to Use:**
- Important content
- Interactive cards
- Hover-able items

---

#### 3. Glass Card

Translucent card with backdrop blur.

**Visual Specifications:**
- Background: rgba(255, 255, 255, 0.05)
- Backdrop filter: blur(10px)
- Border: 1px solid rgba(255, 255, 255, 0.1)
- Border radius: `$radius-xl`
- Padding: `$spacing-4`

**Code Example:**
```html
<div class="card card-glass">
  <h3 class="card-title">Glass Effect</h3>
  <p class="card-text">Translucent with blur.</p>
</div>
```

**SCSS:**
```scss
.card-glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: $radius-xl;
  padding: $spacing-4;
}
```

**When to Use:**
- Feature sections on landing page
- Overlays
- Premium content

---

#### 4. Highlighted Card

Card with accent border and glow.

**Visual Specifications:**
- Background: `$color-surface`
- Border: 2px solid `$color-primary-solid`
- Border radius: `$radius-xl`
- Padding: `$spacing-4`
- Box shadow: `$glow-primary`

**Code Example:**
```html
<div class="card card-highlighted">
  <h3 class="card-title">Featured</h3>
  <p class="card-text">This card is highlighted.</p>
</div>
```

**SCSS:**
```scss
.card-highlighted {
  background: $color-surface;
  border: 2px solid $color-primary-solid;
  border-radius: $radius-xl;
  padding: $spacing-4;
  box-shadow: $glow-primary;
}
```

**When to Use:**
- Featured content
- Selected items
- Premium features

---

## Form Inputs

Form inputs with floating labels and validation states.

### Base Input

**Visual Specifications:**
- Background: `$color-surface`
- Border: 1px solid `$color-border`
- Border radius: `$radius-md` (14px)
- Padding: `$spacing-3` `$spacing-2` (24px 16px)
- Font size: `$font-size-base`
- Label: Floating, positioned inside input

**States:**

#### Default State
```html
<div class="form-group">
  <input type="text" class="form-input" id="name" placeholder=" ">
  <label for="name" class="form-label">Full Name</label>
</div>
```

#### Focus State
- Border: 2px solid `$color-border-focus`
- Box shadow: `$glow-primary`
- Label: Moves up and scales down, color changes to `$color-primary-solid`

#### Error State
```html
<div class="form-group has-error">
  <input type="email" class="form-input" id="email" placeholder=" ">
  <label for="email" class="form-label">Email</label>
  <span class="form-error">Please enter a valid email address</span>
</div>
```

- Border: 2px solid `$color-error`
- Box shadow: `$glow-error`
- Error message: Displayed below in `$color-error`

#### Success State
```html
<div class="form-group has-success">
  <input type="email" class="form-input" id="email" placeholder=" ">
  <label for="email" class="form-label">Email</label>
  <i class="icon-check form-success-icon"></i>
</div>
```

- Border: 2px solid `$color-success`
- Box shadow: `$glow-success`
- Success icon: Green checkmark displayed

#### Disabled State
```html
<div class="form-group">
  <input type="text" class="form-input" id="name" placeholder=" " disabled>
  <label for="name" class="form-label">Full Name</label>
</div>
```

- Background: `$color-base-bg`
- Opacity: 0.5
- Cursor: not-allowed

**SCSS:**
```scss
.form-group {
  position: relative;
  margin-bottom: $spacing-4;
}

.form-input {
  width: 100%;
  background: $color-surface;
  border: 1px solid $color-border;
  border-radius: $radius-md;
  padding: $spacing-3 $spacing-2;
  font-size: $font-size-base;
  color: $color-text-primary;
  transition: all $duration-normal $easing-default;
  
  &:focus {
    outline: none;
    border: 2px solid $color-border-focus;
    box-shadow: $glow-primary;
    
    + .form-label {
      transform: translateY(-1.5rem) scale(0.85);
      color: $color-primary-solid;
    }
  }
  
  &:not(:placeholder-shown) + .form-label {
    transform: translateY(-1.5rem) scale(0.85);
  }
}

.form-label {
  position: absolute;
  left: $spacing-2;
  top: $spacing-3;
  color: $color-text-secondary;
  pointer-events: none;
  transition: all $duration-normal $easing-default;
  transform-origin: left top;
}

.has-error .form-input {
  border: 2px solid $color-error;
  box-shadow: $glow-error;
}

.form-error {
  display: block;
  margin-top: $spacing-1;
  color: $color-error;
  font-size: $font-size-sm;
}

.has-success .form-input {
  border: 2px solid $color-success;
  box-shadow: $glow-success;
}
```

**When to Use:**
- All text inputs
- Email, password, number inputs
- Textareas (with adjusted height)

---

### Input with Icon

```html
<div class="form-group form-group-icon">
  <i class="icon-search form-icon"></i>
  <input type="text" class="form-input" id="search" placeholder=" ">
  <label for="search" class="form-label">Search</label>
</div>
```

**SCSS:**
```scss
.form-group-icon {
  .form-icon {
    position: absolute;
    left: $spacing-2;
    top: 50%;
    transform: translateY(-50%);
    color: $color-text-secondary;
  }
  
  .form-input {
    padding-left: $spacing-6;
  }
}
```

---

## Navigation

### Sidebar Navigation

**Visual Specifications:**
- Width: 280px (expanded), 80px (collapsed)
- Background: `$color-surface`
- Border right: 1px solid `$color-border`
- Fixed position
- Smooth collapse animation (300ms)

**Code Example:**
```html
<nav class="sidebar">
  <div class="sidebar-header">
    <img src="logo.svg" alt="NextGenCV" class="sidebar-logo">
    <button class="sidebar-toggle">
      <i class="icon-menu"></i>
    </button>
  </div>
  
  <ul class="sidebar-nav">
    <li class="sidebar-item active">
      <a href="/dashboard" class="sidebar-link">
        <i class="icon-home"></i>
        <span class="sidebar-text">Dashboard</span>
      </a>
    </li>
    <li class="sidebar-item">
      <a href="/resumes" class="sidebar-link">
        <i class="icon-file"></i>
        <span class="sidebar-text">Resumes</span>
      </a>
    </li>
  </ul>
</nav>
```

**SCSS:**
```scss
.sidebar {
  width: 280px;
  background: $color-surface;
  border-right: 1px solid $color-border;
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  transition: width $duration-slow $easing-default;
  
  &.collapsed {
    width: 80px;
    
    .sidebar-text {
      opacity: 0;
    }
  }
}

.sidebar-item {
  margin: $spacing-1 $spacing-2;
}

.sidebar-link {
  display: flex;
  align-items: center;
  padding: $spacing-2 $spacing-3;
  border-radius: $radius-md;
  color: $color-text-secondary;
  transition: all $duration-normal $easing-default;
  
  &:hover {
    background: $color-surface-elevated;
    color: $color-text-primary;
  }
  
  .sidebar-item.active & {
    background: $color-surface-elevated;
    color: $color-primary-solid;
    border-left: 4px solid $color-primary-solid;
  }
}
```

---

### Top Navigation Bar

**Visual Specifications:**
- Height: 64px
- Background: `$color-surface`
- Border bottom: 1px solid `$color-border`
- Fixed position

**Code Example:**
```html
<header class="topbar">
  <div class="topbar-left">
    <button class="sidebar-toggle-btn">
      <i class="icon-menu"></i>
    </button>
  </div>
  
  <div class="topbar-center">
    <div class="search-box">
      <i class="icon-search"></i>
      <input type="text" placeholder="Search...">
    </div>
  </div>
  
  <div class="topbar-right">
    <button class="topbar-icon-btn">
      <i class="icon-bell"></i>
      <span class="badge">3</span>
    </button>
    
    <div class="profile-dropdown">
      <img src="avatar.jpg" alt="User" class="avatar">
      <span class="username">John Doe</span>
      <i class="icon-chevron-down"></i>
    </div>
  </div>
</header>
```

---

## Progress Indicators

### Linear Progress Bar

**Visual Specifications:**
- Height: 8px
- Background: `$color-surface-elevated`
- Fill: `$color-primary` gradient
- Border radius: `$radius-full`
- Animated fill transition

**Code Example:**
```html
<div class="progress">
  <div class="progress-bar" style="width: 75%"></div>
</div>

<!-- With label -->
<div class="progress-wrapper">
  <div class="progress-label">
    <span>Resume Score</span>
    <span>75%</span>
  </div>
  <div class="progress">
    <div class="progress-bar" style="width: 75%"></div>
  </div>
</div>
```

**SCSS:**
```scss
.progress {
  height: 8px;
  background: $color-surface-elevated;
  border-radius: $radius-full;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: $color-primary;
  border-radius: $radius-full;
  transition: width $duration-slow $easing-default;
}
```

---

### Circular Progress

**Visual Specifications:**
- SVG-based circular progress
- Stroke: `$color-primary` gradient
- Background stroke: `$color-surface-elevated`
- Animated stroke-dashoffset
- Center: Score value + label

**Code Example:**
```html
<div class="circular-progress" data-progress="75">
  <svg viewBox="0 0 120 120">
    <circle class="progress-bg" cx="60" cy="60" r="54"></circle>
    <circle class="progress-fill" cx="60" cy="60" r="54"></circle>
  </svg>
  <div class="progress-value">
    <span class="progress-number">75</span>
    <span class="progress-label">Score</span>
  </div>
</div>
```

**SCSS:**
```scss
.circular-progress {
  position: relative;
  width: 120px;
  height: 120px;
  
  svg {
    transform: rotate(-90deg);
  }
  
  .progress-bg {
    fill: none;
    stroke: $color-surface-elevated;
    stroke-width: 8;
  }
  
  .progress-fill {
    fill: none;
    stroke: $color-primary-solid;
    stroke-width: 8;
    stroke-linecap: round;
    stroke-dasharray: 339.292;
    stroke-dashoffset: 339.292;
    transition: stroke-dashoffset $duration-slow $easing-default;
  }
  
  .progress-value {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
  }
}
```

---

### Wizard Step Progress

**Visual Specifications:**
- Horizontal step indicator
- Completed steps: `$color-success` with checkmark
- Current step: `$color-primary-solid` with glow
- Future steps: `$color-text-tertiary`
- Connecting lines between steps

**Code Example:**
```html
<div class="wizard-progress">
  <div class="wizard-step completed">
    <div class="step-indicator">
      <i class="icon-check"></i>
    </div>
    <span class="step-label">Personal Info</span>
  </div>
  
  <div class="wizard-line completed"></div>
  
  <div class="wizard-step active">
    <div class="step-indicator">2</div>
    <span class="step-label">Experience</span>
  </div>
  
  <div class="wizard-line"></div>
  
  <div class="wizard-step">
    <div class="step-indicator">3</div>
    <span class="step-label">Education</span>
  </div>
</div>
```

---

## Feedback Components

### Alert Component

**Variants:** Success, Error, Warning, Info

**Code Example:**
```html
<!-- Success Alert -->
<div class="alert alert-success">
  <i class="icon-check-circle"></i>
  <div class="alert-content">
    <h4 class="alert-title">Success!</h4>
    <p class="alert-message">Your resume has been saved.</p>
  </div>
  <button class="alert-close">
    <i class="icon-x"></i>
  </button>
</div>

<!-- Error Alert -->
<div class="alert alert-error">
  <i class="icon-x-circle"></i>
  <div class="alert-content">
    <h4 class="alert-title">Error</h4>
    <p class="alert-message">Failed to upload file.</p>
  </div>
  <button class="alert-close">
    <i class="icon-x"></i>
  </button>
</div>
```

**SCSS:**
```scss
.alert {
  display: flex;
  align-items: flex-start;
  padding: $spacing-3;
  border-radius: $radius-lg;
  margin-bottom: $spacing-3;
  
  &-success {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid $color-success;
    color: $color-success;
  }
  
  &-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid $color-error;
    color: $color-error;
  }
}
```

---

### Toast Notification

**Visual Specifications:**
- Position: Top-right corner
- Stack vertically if multiple
- Auto-dismiss after 5 seconds
- Slide in from right animation

**Code Example:**
```html
<div class="toast toast-success">
  <i class="icon-check-circle"></i>
  <span class="toast-message">Resume saved successfully!</span>
  <button class="toast-close">
    <i class="icon-x"></i>
  </button>
  <div class="toast-progress"></div>
</div>
```

---

### Modal Component

**Visual Specifications:**
- Backdrop: rgba(0, 0, 0, 0.8) with backdrop blur
- Modal: Centered, max-width 600px
- Background: `$color-surface-elevated`
- Border radius: `$radius-xl`
- Shadow: `$shadow-lg`

**Code Example:**
```html
<div class="modal-backdrop">
  <div class="modal">
    <div class="modal-header">
      <h3 class="modal-title">Confirm Action</h3>
      <button class="modal-close">
        <i class="icon-x"></i>
      </button>
    </div>
    
    <div class="modal-body">
      <p>Are you sure you want to delete this resume?</p>
    </div>
    
    <div class="modal-footer">
      <button class="btn btn-ghost">Cancel</button>
      <button class="btn btn-primary">Confirm</button>
    </div>
  </div>
</div>
```

---

### Badge Component

**Code Example:**
```html
<span class="badge badge-primary">New</span>
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Error</span>
```

---

## Data Display

### Data Table

**Visual Specifications:**
- Container: `$color-surface` card
- Header row: `$color-surface-elevated` background
- Rows: Alternating subtle background
- Hover: Row highlight
- Borders: Subtle `$color-border`

**Code Example:**
```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Status</th>
        <th>Score</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Software Engineer Resume</td>
        <td><span class="badge badge-success">Active</span></td>
        <td>85</td>
        <td>
          <button class="btn btn-sm btn-ghost">Edit</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

---

### Empty State

**Code Example:**
```html
<div class="empty-state">
  <i class="empty-state-icon icon-file"></i>
  <h3 class="empty-state-title">No resumes yet</h3>
  <p class="empty-state-text">Create your first resume to get started</p>
  <button class="btn btn-primary">Create Resume</button>
</div>
```

---

### Loading States

**Spinner:**
```html
<div class="spinner"></div>
```

**Skeleton Screen:**
```html
<div class="skeleton skeleton-card">
  <div class="skeleton-header"></div>
  <div class="skeleton-text"></div>
  <div class="skeleton-text"></div>
</div>
```

---

## Usage Guidelines

### Component Selection

**Choose the right component for the job:**

- **Buttons**: Use primary for main actions, ghost for secondary, outline for tertiary
- **Cards**: Use default for general content, elevated for interactive items, glass for premium features
- **Forms**: Always use floating labels, provide inline validation
- **Navigation**: Use sidebar for main navigation, topbar for global actions
- **Progress**: Use linear for simple progress, circular for scores, wizard for multi-step flows
- **Feedback**: Use alerts for persistent messages, toasts for temporary notifications, modals for confirmations
- **Data**: Use tables for structured data, empty states when no content, skeletons while loading

### Accessibility

**All components must:**
- Be keyboard navigable
- Have proper ARIA labels
- Meet WCAG AA contrast standards
- Support screen readers
- Have visible focus states

### Performance

**Optimize component usage:**
- Lazy load below-fold components
- Use CSS transforms for animations
- Minimize DOM manipulation
- Debounce expensive operations
- Use skeleton screens instead of spinners

### Consistency

**Maintain consistency:**
- Use design tokens for all values
- Follow naming conventions
- Reuse components across pages
- Document any customizations
- Test across browsers

---

## Version History

- **v1.0.0** (2026-02-15): Initial component library documentation
