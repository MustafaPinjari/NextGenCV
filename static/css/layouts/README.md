# Layout Templates Implementation

This directory contains the CSS for the NextGenCV layout templates.

## Files Created

### Templates
- `templates/layouts/authenticated.html` - Layout for logged-in users with sidebar and top navigation
- `templates/layouts/public.html` - Layout for public pages (landing, login, register)

### CSS
- `static/css/layouts/authenticated.css` - Styles for authenticated layout
- `static/css/layouts/public.css` - Styles for public layout
- `static/css/layouts.css` - Combined import file

## Authenticated Layout Features

### Structure
- **Sidebar Navigation** (280px width, collapsible to 80px)
  - Logo and brand
  - Main navigation menu with icons
  - Active state indicators
  - Collapse/expand toggle
  - Bottom section for settings/help
  
- **Top Navigation Bar** (64px height, sticky)
  - Mobile menu toggle
  - Search input
  - Notifications button with badge
  - Profile dropdown menu
  
- **Main Content Area**
  - Responsive padding
  - Max-width container (1400px)
  - Adjusts width when sidebar collapses
  
- **Alert System**
  - Toast-style notifications
  - Auto-dismiss after 5 seconds
  - Success, error, warning, info variants
  - Slide-in/out animations

### Responsive Behavior
- **Desktop (>1024px)**: Full sidebar visible
- **Tablet (768-1024px)**: Sidebar collapsed by default
- **Mobile (<768px)**: Sidebar as overlay drawer with hamburger menu

### Accessibility Features
- Skip to main content link
- Proper ARIA labels and roles
- Keyboard navigation support
- Focus states on all interactive elements
- Semantic HTML structure

## Public Layout Features

### Structure
- **Top Navigation** (transparent, becomes solid on scroll)
  - Logo and brand
  - Desktop menu links
  - Auth action buttons
  - Mobile hamburger menu
  
- **Main Content Area**
  - Full-width sections
  - Hero section structure
  - Feature section structure
  
- **Footer** (5-column grid)
  - Brand column with logo and social links
  - Product links
  - Company links
  - Resources links
  - Legal links
  - Copyright notice

### Navigation Behavior
- Transparent background initially
- Solid background with blur on scroll
- Smooth scroll for anchor links
- Mobile menu slides down from top

### Responsive Behavior
- **Desktop (>1024px)**: Full horizontal menu
- **Tablet (768-1024px)**: Mobile menu, 2-column footer
- **Mobile (<768px)**: Mobile menu, single-column footer, stacked buttons

## Usage

### Using Authenticated Layout
```django
{% extends 'layouts/authenticated.html' %}

{% block title %}My Page Title{% endblock %}

{% block content %}
    <!-- Your page content here -->
{% endblock %}

{% block extra_css %}
    <!-- Optional additional CSS -->
{% endblock %}

{% block extra_js %}
    <!-- Optional additional JavaScript -->
{% endblock %}
```

### Using Public Layout
```django
{% extends 'layouts/public.html' %}

{% block title %}My Page Title{% endblock %}

{% block content %}
    <!-- Your page content here -->
{% endblock %}
```

## Design System Integration

Both layouts use the design system tokens defined in `design-system.css`:
- Color tokens (dark theme)
- Typography tokens
- Spacing tokens (8px grid)
- Shadow tokens (soft glows)
- Animation tokens (150-250ms)
- Border radius tokens (14-20px)

## JavaScript Functionality

### Authenticated Layout
- Sidebar collapse/expand with localStorage persistence
- Mobile menu toggle with overlay
- Profile dropdown toggle
- Alert auto-dismiss and manual close
- Responsive behavior handling

### Public Layout
- Scroll-based navigation background
- Mobile menu toggle with hamburger animation
- Smooth scroll for anchor links
- Auto-close mobile menu on link click

## Browser Support

- Chrome (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Edge (last 2 versions)
- iOS Safari
- Chrome Mobile

## Performance Considerations

- CSS transitions use GPU-accelerated properties (transform, opacity)
- Minimal JavaScript for core functionality
- Efficient selectors and specificity
- No heavy dependencies
- Lazy loading ready

## Next Steps

To use these layouts in existing pages:
1. Update page templates to extend the appropriate layout
2. Remove legacy navigation/footer code
3. Update CSS imports to use layout styles
4. Test responsive behavior
5. Verify accessibility compliance
