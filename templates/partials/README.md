# Shared Template Partials

This directory contains reusable template components that can be included across different pages.

## Empty State Components

### 1. No Resumes Empty State
**File:** `empty_state_no_resumes.html`

Usage:
```django
{% include 'partials/empty_state_no_resumes.html' %}
```

Displays when user has no resumes created yet. Includes a CTA button to create first resume.

### 2. No Search Results Empty State
**File:** `empty_state_no_results.html`

Usage:
```django
{% include 'partials/empty_state_no_results.html' %}
```

Displays when search/filter returns no results. Includes a "Clear Filters" button.

### 3. No Activity Empty State
**File:** `empty_state_no_activity.html`

Usage:
```django
{% include 'partials/empty_state_no_activity.html' %}
```

Displays when user has no recent activity. Smaller variant suitable for dashboard widgets.

### 4. Generic Empty State
**File:** `empty_state.html`

Usage:
```django
{% include 'partials/empty_state.html' with title="Custom Title" description="Custom description" button_text="Action" button_url="/url/" %}
```

Customizable empty state component. Parameters:
- `title`: Main heading text
- `description`: Description text
- `icon_svg`: Custom SVG icon (optional)
- `button_text`: Button label
- `button_url`: Button link URL
- `button_onclick`: Button onclick handler (alternative to URL)
- `size`: Set to "sm" for smaller variant

## Loading State Components

### 1. Page Loading Overlay
**File:** `loading_page.html`

Usage:
```django
{% include 'partials/loading_page.html' with loading_text="Loading your data..." %}
```

Full-page loading overlay with spinner. Auto-hides when page loads.

### 2. Inline Loading Spinner
**File:** `loading_inline.html`

Usage:
```django
{% include 'partials/loading_inline.html' with loading_text="Processing..." %}
```

Small inline loading indicator for use within content.

### 3. Section Loading State
**File:** `loading_section.html`

Usage:
```django
{% include 'partials/loading_section.html' with loading_text="Loading section..." %}
```

Loading state for a specific section or card.

### 4. Skeleton Card
**File:** `skeleton_card.html`

Usage:
```django
{% include 'partials/skeleton_card.html' %}
```

Skeleton loading placeholder for card components.

### 5. Skeleton Table
**File:** `skeleton_table.html`

Usage:
```django
{% include 'partials/skeleton_table.html' %}
```

Skeleton loading placeholder for table components.

### 6. Button Loading State
**File:** `button_loading_example.html`

Usage:
```html
<button class="btn btn-primary btn-loading" disabled>Submit</button>
```

Or use JavaScript:
```javascript
setButtonLoading(buttonElement, true);  // Show loading
setButtonLoading(buttonElement, false); // Hide loading
```

## Design System Integration

All components use the NextGenCV design system tokens:
- Colors from `tokens/_colors.scss`
- Typography from `tokens/_typography.scss`
- Spacing from `tokens/_spacing.scss`
- Animations from `tokens/_animations.scss`

## Styling

Component styles are defined in:
- `static/scss/components/_data-display.scss` - Empty states, loading states, skeletons
- `static/scss/components/_buttons.scss` - Button loading state
- `static/scss/pages/_error-pages.scss` - Error page styles

## Requirements Validation

These components satisfy:
- **Requirement 2.1**: Universal page coverage with consistent design
- **Requirement 12.1**: Minimal illustration matching dark theme
- **Requirement 12.2**: Guiding messages explaining situations
- **Requirement 12.3**: Clear CTA buttons for next actions
- **Requirement 12.4**: Avoiding generic blank screens
- **Requirement 12.6**: Elegant loading animations with glow effects
