# NextGenCV Page Layouts Documentation

## Overview

This document provides a comprehensive blueprint for all page layouts in the NextGenCV application. Each page follows one of three base layout templates (Authenticated, Public, or Admin) and implements consistent patterns for structure, navigation, and responsive behavior.

## Table of Contents

1. [Layout Templates](#layout-templates)
2. [Page-by-Page Blueprints](#page-by-page-blueprints)
3. [Responsive Behavior](#responsive-behavior)
4. [Layout Patterns](#layout-patterns)

---

## Layout Templates

### 1. Authenticated Layout

Used for all pages requiring user login.

**Structure:**
```
┌─────────────────────────────────────────┐
│           Top Navigation Bar            │
├──────┬──────────────────────────────────┤
│      │                                  │
│ Side │        Main Content Area         │
│ bar  │                                  │
│      │                                  │
│      │                                  │
└──────┴──────────────────────────────────┘
```

**Specifications:**
- **Sidebar**: Fixed left, 280px wide (expanded), 80px (collapsed)
- **Top Bar**: Fixed top, 64px height, full width
- **Main Content**: Scrollable, max-width 1400px, centered
- **Padding**: `$spacing-6` (48px) on main content
- **Background**: `$color-base-bg`

**Template File:** `templates/layouts/authenticated.html`

**Pages Using This Layout:**
- Dashboard
- Resume List
- Resume Builder
- Resume Preview
- ATS Analyzer
- PDF Upload
- Fix Comparison
- Version History
- Analytics Dashboard
- Settings
- Profile

**Responsive Breakpoints:**
- **Desktop (>1024px)**: Sidebar visible, full layout
- **Tablet (768-1024px)**: Sidebar collapsed by default
- **Mobile (<768px)**: Sidebar as overlay drawer

---

### 2. Public Layout

Used for non-authenticated pages and marketing content.

**Structure:**
```
┌─────────────────────────────────────────┐
│         Top Navigation (Minimal)        │
├─────────────────────────────────────────┤
│                                         │
│            Hero Section                 │
│         (Full viewport height)          │
│                                         │
├─────────────────────────────────────────┤
│          Feature Sections               │
│        (Multiple sections)              │
├─────────────────────────────────────────┤
│              Footer                     │
└─────────────────────────────────────────┘
```

**Specifications:**
- **Top Nav**: Transparent over hero, becomes solid on scroll
- **Hero**: Full viewport height, centered content
- **Sections**: Max-width 1200px, centered, generous vertical spacing
- **Footer**: Full width, `$color-surface`, multiple columns

**Template File:** `templates/layouts/public.html`

**Pages Using This Layout:**
- Landing Page
- Login
- Register
- Forgot Password
- 404 Error
- 500 Error

**Responsive Breakpoints:**
- **Desktop (>1024px)**: Multi-column layouts
- **Tablet (768-1024px)**: 2-column layouts
- **Mobile (<768px)**: Single column, stacked

---

### 3. Admin Layout

Extended authenticated layout with enhanced sidebar for admin functions.

**Structure:** Same as Authenticated Layout with additional admin sections in sidebar

**Template File:** `templates/layouts/admin.html`

**Pages Using This Layout:**
- Admin Dashboard
- User Management
- Resume Management
- System Settings

---

## Page-by-Page Blueprints


### Landing Page

**Layout:** Public Layout

**Sections:**

1. **Hero Section**
   - Full viewport height
   - Centered content (max-width 800px)
   - Large headline (font-size-6xl) with gradient text
   - Subheadline (font-size-xl) in muted gray
   - Two CTA buttons: Primary (Sign Up) + Ghost (Learn More)
   - Animated background: Subtle gradient mesh
   - Scroll indicator at bottom

2. **Features Section**
   - 3-column grid (responsive to 1 column on mobile)
   - Each feature: Icon + Title + Description
   - Glass card style
   - Hover: Lift effect + glow

3. **Social Proof Section**
   - Statistics: Resumes created, score improvement, user count
   - Large numbers with animated count-up
   - Testimonial cards

4. **CTA Section**
   - Full-width with gradient background
   - Large headline + CTA button

5. **Footer**
   - 4-column layout: Product, Company, Resources, Legal
   - Social media icons
   - Copyright notice

**Key Elements:**
- Gradient text effects on headlines
- Glass cards for features
- Animated statistics
- Sticky navigation that becomes solid on scroll

---

### Dashboard

**Layout:** Authenticated Layout

**Grid Structure:** 3 columns on desktop, 1 column on mobile

**Sections:**

1. **Welcome Header**
   - Greeting with user name
   - Current date
   - Quick stats: Total resumes, average score

2. **Resume Health Card** (Featured)
   - Large circular progress meter
   - Current ATS score (large number)
   - Score trend indicator (up/down arrow + percentage)
   - "Improve Score" CTA button

3. **Quick Actions Grid** (2x2)
   - Create Resume
   - Upload PDF
   - View Analytics
   - Templates
   - Each with icon and hover glow

4. **Recent Resumes Section**
   - List of 3-4 resume cards
   - Each card: Title, date, score badge, thumbnail
   - Hover: Lift + show actions (Edit, Delete, Download)
   - "View All" link

5. **Activity Feed**
   - Timeline of recent actions
   - Icons for action types
   - Relative timestamps

6. **Charts Section**
   - Score trend line chart (last 30 days)
   - Keyword match radar chart
   - Animated on scroll

**Responsive Behavior:**
- Desktop: 3-column grid
- Tablet: 2-column grid
- Mobile: Single column, stacked

---

### Login Page

**Layout:** Public Layout

**Structure:**
- Centered card (max-width 480px)
- Split background on desktop: Left branding, right form
- Mobile: Stacked vertically

**Form Elements:**
- Logo at top
- "Welcome back" headline
- Email input (floating label)
- Password input (floating label, show/hide toggle)
- Remember me checkbox
- Forgot password link (right-aligned)
- Sign in button (primary, full-width)
- Divider with "or"
- Social login buttons (Google, LinkedIn)
- Sign up link at bottom

**Validation:**
- Inline validation on blur
- Error states with red glow
- Clear error messages

---

### Register Page

**Layout:** Public Layout

**Structure:** Similar to Login Page

**Form Elements:**
- Logo at top
- "Create your account" headline
- Full name input
- Email input
- Password input
- Confirm password input
- Terms acceptance checkbox
- Sign up button (primary, full-width)
- Already have account link

---

### Resume List Page

**Layout:** Authenticated Layout

**Structure:**

1. **Page Header**
   - Title: "My Resumes"
   - Create new button (primary, with icon)
   - Search input (with icon)
   - Filter dropdown (Sort by: Date, Score, Name)

2. **Resume Grid**
   - 3 columns on desktop, 2 on tablet, 1 on mobile
   - Each resume card:
     - Thumbnail preview (top)
     - Resume title
     - ATS score badge (top-right)
     - Last modified date
     - Action buttons: Edit, Duplicate, Download, Delete
     - Hover: Lift effect + show actions

3. **Empty State** (if no resumes)
   - Centered illustration
   - "No resumes yet" message
   - "Create your first resume" CTA button

4. **Pagination**
   - Bottom of page
   - Page numbers + prev/next buttons
   - Current page highlighted

---

### Resume Builder Wizard

**Layout:** Authenticated Layout (Full-screen variant)

**Structure:**

1. **Progress Indicator** (Top)
   - Horizontal step bar
   - Steps: Personal Info, Experience, Education, Skills, Summary
   - Completed: Green checkmark
   - Current: Blue glow
   - Future: Gray

2. **Split View**
   - Left (60%): Form section
   - Right (40%): Live preview (sticky)

3. **Form Section**
   - Step-specific form fields
   - Floating labels
   - Inline validation
   - Collapsible sections for multiple entries
   - Add/Remove buttons
   - Auto-save indicator (top-right)

4. **Live Preview**
   - Glass card container
   - Rendered resume with current data
   - Updates in real-time
   - Template selector dropdown
   - Zoom controls

5. **Navigation** (Bottom)
   - Back button
   - Save Draft button
   - Next button (or Finish on last step)

**Steps:**
- Step 1: Personal Info (name, email, phone, location, links)
- Step 2: Experience (multiple jobs with bullet points)
- Step 3: Education (multiple entries)
- Step 4: Skills (tag input)
- Step 5: Summary (textarea with AI suggestion)

---

### PDF Upload Page

**Layout:** Authenticated Layout

**Structure:**

1. **Upload Zone** (Centered)
   - Large dashed border with glow
   - Drag-and-drop area
   - "Click to browse" text
   - File icon
   - Supported formats text
   - Animated border glow on drag-over

2. **Upload Progress** (During upload)
   - Progress bar
   - Percentage text
   - File name
   - Cancel button

3. **Results Section** (After upload)
   - Fade in animation
   - ATS score reveal (circular progress animates from 0)
   - Parsed sections preview
   - Missing keywords tags
   - "Fix My Resume" glowing CTA button
   - "Edit Manually" secondary button

---

### ATS Analyzer Page

**Layout:** Authenticated Layout

**Structure:**

1. **Two-Column Layout**
   - Left (40%): Upload/Select section
   - Right (60%): Analysis results

2. **Upload Section**
   - Drag-and-drop zone
   - OR
   - Resume selector dropdown
   - "Analyze" button

3. **Analysis Results**
   - Overall ATS score (large circular progress)
   - Score breakdown:
     - Keyword match (progress bar)
     - Formatting (progress bar)
     - Section completeness (progress bar)
     - Action verbs (progress bar)
   - Missing keywords (tags)
   - Suggestions list (expandable items)
   - "Fix My Resume" CTA button

4. **Loading State**
   - Animated spinner
   - "Analyzing..." text
   - Progress indicator

---

### Fix Resume Comparison Page

**Layout:** Authenticated Layout

**Structure:**

1. **Score Comparison** (Top)
   - Two circular progress meters side by side
   - Arrow between showing improvement
   - Delta badge (e.g., "+15 points")

2. **Split View** (50/50)
   - Left: Original version
   - Right: Optimized version
   - Synchronized scrolling
   - Highlighted differences:
     - Additions: Green left border + light background
     - Removals: Red left border + light background
     - Modifications: Blue left border + light background
   - Hover: Tooltip with explanation

3. **Change Cards**
   - Each improvement as a card
   - Change type badge
   - Before/After text
   - Reason for change
   - Accept/Reject buttons

4. **Action Toolbar** (Bottom)
   - Accept All button
   - Reject All button
   - Apply Selected button (primary)
   - Cancel button

---

### Analytics Dashboard

**Layout:** Authenticated Layout

**Structure:**

1. **Filters** (Top)
   - Date range selector
   - Export button

2. **Stats Cards Row**
   - Total resumes
   - Average score
   - Total improvements
   - Time saved
   - Animated count-up on load

3. **Charts Grid** (2x2 on desktop)
   - Score Trend Line Chart
   - Keyword Coverage Radar Chart
   - Version Comparison Bar Chart
   - Improvement Areas Donut Chart
   - All with dark theme colors
   - Animated on load

**Chart Specifications:**
- Dark theme colors
- Grid lines: `$color-border`
- Tooltips: Dark background with glow
- Legend: `$color-text-secondary`
- Responsive sizing

---

### Settings Page

**Layout:** Authenticated Layout

**Structure:**

1. **Sidebar Navigation** (Left, 30%)
   - Settings categories:
     - Profile
     - Account
     - Notifications
     - Privacy
     - Billing

2. **Content Area** (Right, 70%)
   - Category-specific forms
   - Section headings
   - Form fields with floating labels
   - Save button at bottom

**Categories:**

- **Profile**: Photo upload, name, email, phone, bio
- **Account**: Change password, email preferences, language, timezone
- **Notifications**: Toggle switches for notification types
- **Privacy**: Data sharing preferences
- **Billing**: Payment method, subscription details

---

### Profile Page

**Layout:** Authenticated Layout

**Structure:**

1. **Header Section**
   - Cover photo (editable)
   - Profile photo (editable, overlaps cover)
   - Name and title
   - Edit profile button (top-right)

2. **Stats Row**
   - 3-4 stat cards
   - Icons + numbers + labels

3. **Tabs**
   - Horizontal tab navigation
   - Active tab: Blue underline + glow
   - Tabs: Overview, Resumes, Activity

4. **Content Area** (Based on selected tab)
   - **Overview**: Bio, skills tags, recent activity
   - **Resumes**: Grid of resume cards
   - **Activity**: Timeline of all activities

---

### Resume Version History Page

**Layout:** Authenticated Layout

**Structure:**

1. **Timeline View** (Left, 30%)
   - Vertical timeline
   - Each version: Date, time, score badge, thumbnail
   - Current version highlighted
   - Click to preview
   - Restore button on hover

2. **Version Preview** (Right, 70%)
   - Full resume preview
   - Version info (date, score, changes summary)
   - Compare button
   - Restore button
   - Download button

3. **Comparison View** (Modal or full-screen)
   - Similar to Fix Comparison
   - Shows differences between versions

---

### Error Pages (404, 500)

**Layout:** Public Layout (Minimal)

**Structure:**
- Centered content
- Full viewport height
- Large error code/icon with gradient
- Headline
- Friendly message
- CTA buttons
- Minimal illustration

**404 Page:**
- "404" text with gradient
- "Page not found" headline
- Search bar (optional)
- "Go to Dashboard" button
- "Go to Home" button

**500 Page:**
- Large error icon
- "Something went wrong" headline
- "Try again" button
- "Contact support" link

---

## Responsive Behavior

### Breakpoint Strategy

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 640px | Single column, stacked, sidebar as drawer |
| Tablet | 640-1024px | 2 columns, sidebar collapsed, reduced spacing |
| Desktop | 1024-1280px | 3 columns, full sidebar, standard spacing |
| Large | > 1280px | 3+ columns, full sidebar, generous spacing |

### Mobile Adaptations

**Navigation:**
- Sidebar becomes overlay drawer
- Hamburger menu button in top bar
- Swipe to open/close
- Full-screen when open

**Grids:**
- Multi-column grids become single column
- Maintain card styling
- Reduce spacing between items

**Forms:**
- Full-width inputs
- Larger touch targets (min 44px)
- Simplified layouts
- Stack form groups vertically

**Tables:**
- Horizontal scroll
- Or card-based layout for mobile
- Sticky first column

**Charts:**
- Responsive sizing
- Simplified on small screens
- Horizontal scroll if needed
- Reduce data points

**Typography:**
- Scale down font sizes (10-20% reduction)
- Maintain hierarchy
- Increase line height for readability

**Spacing:**
- Reduce padding/margins (50-75% of desktop)
- Maintain visual breathing room
- Consistent spacing ratios

### Tablet Adaptations

**Navigation:**
- Sidebar collapsed by default
- Expand on click
- Overlay on smaller tablets

**Grids:**
- 2-column layouts
- Adjust card sizes
- Maintain hover effects

**Forms:**
- 2-column layouts for related fields
- Full-width for complex inputs

**Charts:**
- Responsive sizing
- Maintain all features
- Adjust legend position

---

## Layout Patterns

### Content Width Constraints

**Maximum Widths:**
- Main content: 1400px
- Reading content: 800px
- Forms: 600px
- Modals: 600px

**Centering:**
```css
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 $spacing-6;
}
```

### Vertical Spacing

**Section Spacing:**
- Between major sections: `$spacing-8` (64px)
- Between subsections: `$spacing-6` (48px)
- Between elements: `$spacing-4` (32px)
- Between related items: `$spacing-2` (16px)

### Grid Systems

**Standard Grid:**
```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: $spacing-4;
}
```

**Dashboard Grid:**
```css
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-4;
  
  @media (max-width: $breakpoint-lg) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (max-width: $breakpoint-md) {
    grid-template-columns: 1fr;
  }
}
```

### Sticky Elements

**Sticky Sidebar:**
```css
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
}
```

**Sticky Top Bar:**
```css
.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
```

**Sticky Preview:**
```css
.preview-panel {
  position: sticky;
  top: $spacing-6;
  max-height: calc(100vh - #{$spacing-6} * 2);
  overflow-y: auto;
}
```

---

## Best Practices

### Layout Do's

✅ Use consistent max-widths for content
✅ Maintain generous whitespace
✅ Test at all breakpoints
✅ Use CSS Grid for complex layouts
✅ Use Flexbox for component layouts
✅ Implement sticky navigation
✅ Provide clear visual hierarchy
✅ Ensure touch targets are 44px minimum on mobile

### Layout Don'ts

❌ Don't use fixed pixel widths for content
❌ Don't overcrowd the interface
❌ Don't forget mobile testing
❌ Don't use tables for layout
❌ Don't hide important content on mobile
❌ Don't use horizontal scrolling (except tables)
❌ Don't break the back button
❌ Don't use too many columns on mobile

---

## Version History

- **v1.0.0** (2026-02-15): Initial page layouts documentation
