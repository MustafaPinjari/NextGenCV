# Design Document: NextGenCV UI/UX Redesign

## Overview

This design document outlines the complete UI/UX redesign of the NextGenCV application, transforming it into a premium, futuristic, dark-themed SaaS product. The redesign establishes a cohesive design system that applies uniformly across all 20+ pages, components, and interactions, eliminating all legacy styling.

The design follows a "design system first" approach, establishing foundational tokens, components, and patterns before applying them to specific pages. This ensures consistency and maintainability while delivering a 2026 AI-powered SaaS aesthetic.

### Design Philosophy

1. **Consistency Over Customization**: Every page follows the same visual language
2. **Premium Feel**: Dark cinematic backgrounds with soft glowing accents create a high-end experience
3. **Clarity Through Hierarchy**: Large typography, generous whitespace, and clear visual hierarchy guide users
4. **Subtle Motion**: Micro-interactions provide feedback without distraction
5. **Accessibility First**: Beautiful design that works for everyone

## Architecture

### System Layers

The redesign architecture consists of four layers:

```
┌─────────────────────────────────────────┐
│         Application Pages               │
│  (Landing, Dashboard, Builder, etc.)    │
├─────────────────────────────────────────┤
│         Layout Templates                │
│  (Authenticated, Public, Admin)         │
├─────────────────────────────────────────┤
│         Component Library               │
│  (Buttons, Cards, Forms, Charts)        │
├─────────────────────────────────────────┤
│         Design Tokens                   │
│  (Colors, Typography, Spacing, etc.)    │
└─────────────────────────────────────────┘
```

**Layer 1: Design Tokens**
- Foundation of the design system
- CSS custom properties (variables) for colors, spacing, typography, shadows, animations
- Single source of truth for all visual values
- Enables theme switching and consistency

**Layer 2: Component Library**
- Reusable UI components built on design tokens
- Variants for different contexts (primary/secondary buttons, card types, etc.)
- Encapsulates styling and behavior
- Documented with usage guidelines

**Layer 3: Layout Templates**
- Page structure templates (authenticated, public, admin)
- Defines navigation, content areas, and responsive behavior
- Ensures consistent page structure

**Layer 4: Application Pages**
- Specific pages composed from layouts and components
- Page-specific logic and content
- Minimal custom styling (uses components)

### Technology Stack

**Frontend Framework**: Django Templates with enhanced CSS/JS
**CSS Architecture**: SCSS with BEM methodology
**CSS Framework**: Bootstrap 5 (heavily customized via SCSS overrides)
**Animation**: CSS transitions + lightweight JavaScript for complex interactions
**Icons**: Modern icon library (Feather Icons or Heroicons)
**Charts**: Chart.js with custom dark theme configuration

### File Structure

```
static/
├── scss/
│   ├── tokens/
│   │   ├── _colors.scss
│   │   ├── _typography.scss
│   │   ├── _spacing.scss
│   │   ├── _shadows.scss
│   │   └── _animations.scss
│   ├── components/
│   │   ├── _buttons.scss
│   │   ├── _cards.scss
│   │   ├── _forms.scss
│   │   ├── _navigation.scss
│   │   ├── _modals.scss
│   │   └── ... (all components)
│   ├── layouts/
│   │   ├── _authenticated.scss
│   │   ├── _public.scss
│   │   └── _admin.scss
│   ├── pages/
│   │   ├── _landing.scss
│   │   ├── _dashboard.scss
│   │   ├── _resume-builder.scss
│   │   └── ... (page-specific styles)
│   ├── utilities/
│   │   ├── _mixins.scss
│   │   └── _helpers.scss
│   └── main.scss (imports all)
├── css/
│   └── main.css (compiled)
├── js/
│   ├── components/
│   │   ├── sidebar.js
│   │   ├── wizard.js
│   │   ├── file-upload.js
│   │   └── ... (component scripts)
│   └── main.js
└── images/
    ├── illustrations/
    └── icons/
```

## Components and Interfaces

### Design Token System

#### Color Tokens

```scss
// Base Colors
$color-base-bg: #0a0a0a;           // Deep matte black
$color-surface: #141414;            // Slightly lighter dark
$color-surface-elevated: #1a1a1a;  // Elevated surfaces

// Accent Colors
$color-primary: linear-gradient(135deg, #0066ff 0%, #00ccff 100%);  // Electric blue
$color-primary-solid: #0066ff;
$color-secondary: #6366f1;          // Purple-blue
$color-secondary-glow: rgba(99, 102, 241, 0.3);

// Semantic Colors
$color-success: #10b981;            // Soft neon green
$color-success-glow: rgba(16, 185, 129, 0.2);
$color-warning: #f59e0b;            // Amber
$color-warning-glow: rgba(245, 158, 11, 0.2);
$color-error: #ef4444;              // Soft red
$color-error-glow: rgba(239, 68, 68, 0.2);

// Text Colors
$color-text-primary: #f5f5f5;       // Soft white
$color-text-secondary: #a3a3a3;     // Muted gray
$color-text-tertiary: #737373;      // Darker gray

// Border Colors
$color-border: rgba(255, 255, 255, 0.08);
$color-border-hover: rgba(255, 255, 255, 0.15);
$color-border-focus: rgba(0, 102, 255, 0.5);
```

#### Typography Tokens

```scss
// Font Families
$font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
$font-display: 'Space Grotesk', $font-primary;

// Font Sizes
$font-size-xs: 0.75rem;    // 12px
$font-size-sm: 0.875rem;   // 14px
$font-size-base: 1rem;     // 16px
$font-size-lg: 1.125rem;   // 18px
$font-size-xl: 1.25rem;    // 20px
$font-size-2xl: 1.5rem;    // 24px
$font-size-3xl: 1.875rem;  // 30px
$font-size-4xl: 2.25rem;   // 36px
$font-size-5xl: 3rem;      // 48px
$font-size-6xl: 3.75rem;   // 60px

// Font Weights
$font-weight-normal: 400;
$font-weight-medium: 500;
$font-weight-semibold: 600;
$font-weight-bold: 700;

// Line Heights
$line-height-tight: 1.25;
$line-height-normal: 1.5;
$line-height-relaxed: 1.75;

// Letter Spacing
$letter-spacing-tight: -0.02em;
$letter-spacing-normal: 0;
$letter-spacing-wide: 0.025em;
$letter-spacing-wider: 0.05em;
```

#### Spacing Tokens (8px Grid)

```scss
$spacing-0: 0;
$spacing-1: 0.5rem;   // 8px
$spacing-2: 1rem;     // 16px
$spacing-3: 1.5rem;   // 24px
$spacing-4: 2rem;     // 32px
$spacing-5: 2.5rem;   // 40px
$spacing-6: 3rem;     // 48px
$spacing-8: 4rem;     // 64px
$spacing-10: 5rem;    // 80px
$spacing-12: 6rem;    // 96px
$spacing-16: 8rem;    // 128px
```

#### Shadow Tokens

```scss
// Soft Glow Shadows
$shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
$shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
$shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);

// Glow Effects
$glow-primary: 0 0 20px rgba(0, 102, 255, 0.3);
$glow-secondary: 0 0 20px rgba(99, 102, 241, 0.3);
$glow-success: 0 0 20px rgba(16, 185, 129, 0.3);
$glow-error: 0 0 20px rgba(239, 68, 68, 0.3);
```

#### Border Radius Tokens

```scss
$radius-sm: 0.5rem;   // 8px
$radius-md: 0.875rem; // 14px
$radius-lg: 1rem;     // 16px
$radius-xl: 1.25rem;  // 20px
$radius-full: 9999px; // Fully rounded
```

#### Animation Tokens

```scss
$duration-fast: 150ms;
$duration-normal: 250ms;
$duration-slow: 350ms;

$easing-default: cubic-bezier(0.4, 0, 0.2, 1);
$easing-in: cubic-bezier(0.4, 0, 1, 1);
$easing-out: cubic-bezier(0, 0, 0.2, 1);
$easing-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Component Specifications

#### Button Component

**Variants:**

1. **Primary Button**
   - Background: `$color-primary` gradient
   - Text: White
   - Hover: Lift effect (translateY(-2px)) + enhanced glow
   - Active: Slight scale down (scale(0.98))
   - Padding: `$spacing-2` `$spacing-4`
   - Border radius: `$radius-lg`

2. **Ghost Button**
   - Background: Transparent
   - Border: 1px solid `$color-border`
   - Text: `$color-text-primary`
   - Hover: Background `$color-surface-elevated` + border glow

3. **Outline Button**
   - Background: Transparent
   - Border: 2px solid `$color-primary-solid`
   - Text: `$color-primary-solid`
   - Hover: Background `$color-primary-solid` + text white

4. **Gradient Button** (CTA)
   - Background: `$color-primary` gradient
   - Box shadow: `$glow-primary`
   - Hover: Enhanced glow + lift
   - Animation: Subtle pulse on idle

**States:**
- Default
- Hover (lift + glow)
- Active (scale down)
- Disabled (opacity 0.5, no interaction)
- Loading (spinner + disabled state)

#### Card Component

**Variants:**

1. **Default Card**
   - Background: `$color-surface`
   - Border: 1px solid `$color-border`
   - Border radius: `$radius-xl`
   - Padding: `$spacing-4`
   - Shadow: `$shadow-sm`

2. **Elevated Card**
   - Background: `$color-surface-elevated`
   - Border: 1px solid `$color-border`
   - Border radius: `$radius-xl`
   - Padding: `$spacing-5`
   - Shadow: `$shadow-md`
   - Hover: Lift effect + enhanced shadow

3. **Glass Card**
   - Background: rgba(255, 255, 255, 0.05)
   - Backdrop filter: blur(10px)
   - Border: 1px solid rgba(255, 255, 255, 0.1)
   - Border radius: `$radius-xl`
   - Padding: `$spacing-4`

4. **Highlighted Card**
   - Background: `$color-surface`
   - Border: 2px solid `$color-primary-solid`
   - Border radius: `$radius-xl`
   - Padding: `$spacing-4`
   - Box shadow: `$glow-primary`

#### Form Input Component

**Structure:**
- Container with relative positioning
- Input field with dark background
- Floating label that moves up on focus/filled
- Icon slot (optional)
- Helper text slot
- Error message slot

**States:**

1. **Default**
   - Background: `$color-surface`
   - Border: 1px solid `$color-border`
   - Text: `$color-text-primary`
   - Label: `$color-text-secondary` (positioned inside)

2. **Focus**
   - Border: 2px solid `$color-border-focus`
   - Box shadow: `$glow-primary`
   - Label: Moves up and scales down, color changes to `$color-primary-solid`

3. **Filled**
   - Label: Stays in up position
   - Border: 1px solid `$color-border`

4. **Error**
   - Border: 2px solid `$color-error`
   - Box shadow: `$glow-error`
   - Error message: Displayed below in `$color-error`
   - Label: `$color-error`

5. **Success**
   - Border: 2px solid `$color-success`
   - Box shadow: `$glow-success`
   - Success icon: Displayed
   - Label: `$color-success`

6. **Disabled**
   - Background: `$color-base-bg`
   - Opacity: 0.5
   - Cursor: not-allowed

#### Navigation Components

**Sidebar Navigation:**
- Width: 280px (expanded), 80px (collapsed)
- Background: `$color-surface`
- Border right: 1px solid `$color-border`
- Fixed position
- Smooth collapse animation (300ms)

**Sidebar Item:**
- Padding: `$spacing-2` `$spacing-3`
- Border radius: `$radius-md`
- Hover: Background `$color-surface-elevated`
- Active: Background `$color-surface-elevated` + left border `$color-primary-solid` (4px)
- Icon + Text layout
- Collapsed: Show only icon with tooltip

**Top Navigation Bar:**
- Height: 64px
- Background: `$color-surface`
- Border bottom: 1px solid `$color-border`
- Fixed position
- Contains: Logo, search, notifications, profile dropdown

#### Progress Components

**Linear Progress Bar:**
- Height: 8px
- Background: `$color-surface-elevated`
- Fill: `$color-primary` gradient
- Border radius: `$radius-full`
- Animated fill transition
- Optional glow effect on fill

**Circular Progress (Resume Health Meter):**
- SVG-based circular progress
- Stroke: `$color-primary` gradient
- Background stroke: `$color-surface-elevated`
- Animated stroke-dashoffset
- Center: Score value + label
- Size variants: sm (80px), md (120px), lg (160px)

**Step Progress (Wizard):**
- Horizontal step indicator
- Completed steps: `$color-success` with checkmark
- Current step: `$color-primary-solid` with glow
- Future steps: `$color-text-tertiary`
- Connecting lines between steps
- Step labels below indicators

#### Modal Component

**Structure:**
- Backdrop: rgba(0, 0, 0, 0.8) with backdrop blur
- Modal container: Centered, max-width 600px
- Background: `$color-surface-elevated`
- Border: 1px solid `$color-border`
- Border radius: `$radius-xl`
- Shadow: `$shadow-lg`

**Animation:**
- Fade in backdrop (200ms)
- Scale + fade in modal (250ms, slight bounce)
- Reverse on close

**Sections:**
- Header: Title + close button
- Body: Content area with padding
- Footer: Action buttons (right-aligned)

#### Data Table Component

**Structure:**
- Container: `$color-surface` card
- Header row: `$color-surface-elevated` background
- Rows: Alternating subtle background
- Hover: Row highlight with `$color-surface-elevated`
- Borders: Subtle `$color-border`

**Features:**
- Sortable columns (icon indicator)
- Pagination controls
- Row actions (dropdown menu)
- Empty state
- Loading state (skeleton)

#### Chart Components

**Configuration:**
- Dark theme colors
- Grid lines: `$color-border`
- Tooltips: Dark background with glow
- Legend: `$color-text-secondary`
- Animated data entry
- Responsive sizing

**Chart Types:**
- Line chart (trends)
- Bar chart (comparisons)
- Radar chart (keyword coverage)
- Donut chart (score breakdown)

### Layout Templates

#### Authenticated Layout

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
- Sidebar: Fixed left, collapsible
- Top bar: Fixed top, full width
- Main content: Scrollable, max-width 1400px, centered
- Padding: `$spacing-6` on main content
- Background: `$color-base-bg`

**Responsive Behavior:**
- Desktop (>1024px): Sidebar visible
- Tablet (768-1024px): Sidebar collapsed by default
- Mobile (<768px): Sidebar as overlay drawer

#### Public Layout

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
- Top nav: Transparent over hero, becomes solid on scroll
- Hero: Full viewport height, centered content
- Sections: Max-width 1200px, centered, generous vertical spacing
- Footer: Full width, `$color-surface`, multiple columns

## Data Models

### Design Token Data Structure

The design tokens are implemented as CSS custom properties and SCSS variables. No database models are required for the UI redesign itself, but the token structure is:

```scss
:root {
  // Colors
  --color-base-bg: #0a0a0a;
  --color-surface: #141414;
  // ... (all color tokens)
  
  // Typography
  --font-primary: 'Inter', sans-serif;
  --font-size-base: 1rem;
  // ... (all typography tokens)
  
  // Spacing
  --spacing-1: 0.5rem;
  --spacing-2: 1rem;
  // ... (all spacing tokens)
  
  // Shadows
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
  // ... (all shadow tokens)
  
  // Animation
  --duration-fast: 150ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
  // ... (all animation tokens)
}
```

### Component State Management

For interactive components requiring state (sidebar collapse, modal open/close, wizard step), state is managed via:

1. **CSS Classes**: Toggle classes for state changes (e.g., `.sidebar--collapsed`)
2. **Data Attributes**: Store state in HTML (e.g., `data-step="2"`)
3. **JavaScript State**: For complex interactions (wizard flow, file upload progress)

### Page-Specific Data

Each page continues to use existing Django models (Resume, User, etc.). The redesign only affects presentation, not data structure.



## Page-Specific Designs

### Landing Page

**Hero Section:**
- Full viewport height
- Centered content with max-width 800px
- Large headline (font-size-6xl) with gradient text effect
- Subheadline (font-size-xl) in muted gray
- Two CTA buttons: Primary (Sign Up) + Ghost (Learn More)
- Animated background: Subtle gradient mesh or particle effect
- Scroll indicator at bottom

**Features Section:**
- 3-column grid (responsive to 1 column on mobile)
- Each feature: Icon + Title + Description
- Glass card style
- Hover: Lift effect + glow
- Icons with gradient accent

**Social Proof Section:**
- Statistics: Number of resumes created, average score improvement, user count
- Large numbers with animated count-up on scroll into view
- Testimonial cards with user quotes

**CTA Section:**
- Full-width section with gradient background
- Large headline + CTA button
- Contrasting against dark theme

**Footer:**
- 4-column layout: Product, Company, Resources, Legal
- Social media icons
- Copyright notice
- All links in muted gray, hover to white

### Authentication Pages (Login, Register, Forgot Password)

**Layout:**
- Centered card (max-width 480px)
- Split background: Left side with branding/illustration, right side with form
- On mobile: Stack vertically

**Login Page:**
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

**Register Page:**
- Similar layout to login
- Additional fields: Full name, confirm password
- Terms acceptance checkbox
- Sign up button
- Already have account link

**Forgot Password Page:**
- Simplified form
- Email input
- Send reset link button
- Back to login link

**Validation:**
- Inline validation on blur
- Error states with red glow
- Success states with green glow
- Clear error messages below fields

### Dashboard

**Layout:**
- Grid layout: 3 columns on desktop, 1 column on mobile
- Sections: Welcome header, Resume health, Quick actions, Recent resumes, Activity feed

**Welcome Header:**
- Greeting with user name
- Current date
- Quick stats: Total resumes, average score

**Resume Health Card:**
- Large circular progress meter (center)
- Current ATS score (large number)
- Score trend indicator (up/down arrow + percentage)
- "Improve Score" CTA button below

**Quick Actions:**
- 4 action cards in 2x2 grid
- Icons: Create Resume, Upload PDF, View Analytics, Templates
- Hover: Glow effect
- Click: Navigate to respective page

**Recent Resumes:**
- List of resume cards (3-4 visible)
- Each card: Resume title, last modified date, ATS score badge, thumbnail preview
- Hover: Lift + show action buttons (Edit, Delete, Download)
- "View All" link at bottom

**Activity Feed:**
- Timeline of recent actions
- Icons for action types
- Timestamps in relative format (2 hours ago)
- Scrollable if many items

**Charts Section:**
- Score trend line chart (last 30 days)
- Keyword match radar chart
- Animated on scroll into view

### Resume List Page

**Header:**
- Page title: "My Resumes"
- Create new button (primary, with icon)
- Search input (with icon)
- Filter dropdown (Sort by: Date, Score, Name)

**Resume Grid:**
- Grid layout: 3 columns on desktop, 2 on tablet, 1 on mobile
- Each resume card:
  - Thumbnail preview (top)
  - Resume title (editable on hover)
  - ATS score badge (top-right corner)
  - Last modified date
  - Action buttons: Edit, Duplicate, Download, Delete
  - Hover: Lift effect + show actions

**Empty State:**
- Centered illustration
- "No resumes yet" message
- "Create your first resume" CTA button

**Pagination:**
- Bottom of page
- Page numbers + prev/next buttons
- Current page highlighted

### Resume Builder Wizard

**Layout:**
- Full-screen wizard
- Top: Progress indicator (steps)
- Left: Form section (60% width)
- Right: Live preview (40% width, sticky)
- Bottom: Navigation buttons (Back, Save Draft, Next)

**Progress Indicator:**
- Horizontal step bar at top
- Steps: Personal Info, Experience, Education, Skills, Summary
- Completed steps: Green checkmark
- Current step: Blue glow
- Future steps: Gray
- Connecting lines between steps

**Form Section:**
- Step-specific form fields
- Floating labels
- Inline validation
- Collapsible sections for multiple entries (e.g., multiple jobs)
- Add/Remove buttons for repeatable sections
- Auto-save indicator (top-right): "Saved" with checkmark or "Saving..." with spinner

**Live Preview:**
- Glass card container
- Rendered resume with current data
- Updates in real-time as user types
- Template selector dropdown at top
- Zoom controls

**Step 1: Personal Info**
- Fields: Full name, email, phone, location, LinkedIn, portfolio
- Profile photo upload (optional)

**Step 2: Experience**
- Multiple job entries
- Fields per job: Company, title, dates, description (bullet points)
- Add/Remove job buttons
- Drag to reorder

**Step 3: Education**
- Multiple education entries
- Fields: School, degree, field, dates, GPA (optional)
- Add/Remove buttons

**Step 4: Skills**
- Tag input for skills
- Suggested skills based on experience
- Categorize skills (Technical, Soft, Languages)

**Step 5: Summary**
- Textarea for professional summary
- Character count
- AI suggestion button (generates summary based on experience)

**Navigation:**
- Back button: Returns to previous step
- Save Draft: Saves and returns to dashboard
- Next button: Validates and moves to next step
- On last step: "Finish" button instead of Next

### Resume Preview Page

**Layout:**
- Full-width preview area
- Top toolbar: Template selector, zoom controls, download button, share button
- Resume rendered in selected template
- Print-optimized view

**Toolbar:**
- Left: Back to editor button
- Center: Template dropdown (with thumbnails)
- Right: Zoom slider, Download (PDF/DOCX), Share button

**Preview Area:**
- White background (resume)
- Centered with shadow
- Responsive zoom
- Print styles applied

**Download Modal:**
- Format selection: PDF, DOCX, TXT
- Template selection
- Download button

### ATS Analyzer Page

**Layout:**
- Two-column layout
- Left: Upload section or resume selector
- Right: Analysis results

**Upload Section:**
- Drag-and-drop zone
- File input button
- Supported formats: PDF, DOCX
- File size limit indicator

**Resume Selector:**
- Dropdown to select existing resume
- "Analyze" button

**Analysis Results:**
- Overall ATS score (large circular progress)
- Score breakdown:
  - Keyword match (progress bar)
  - Formatting (progress bar)
  - Section completeness (progress bar)
  - Action verbs (progress bar)
- Missing keywords (tags)
- Suggestions list (expandable items)
- "Fix My Resume" CTA button (navigates to fix comparison)

**Loading State:**
- Animated spinner with "Analyzing..." text
- Progress indicator

### PDF Upload Page

**Layout:**
- Centered upload zone
- Instructions above
- Results below (after upload)

**Upload Zone:**
- Large dashed border with glow on hover
- Drag-and-drop area
- "Click to browse" text
- File icon
- Supported formats text
- Animated border glow on drag-over

**Upload Progress:**
- Progress bar
- Percentage text
- File name
- Cancel button

**Results Section:**
- Fade in after upload completes
- ATS score reveal animation (circular progress animates from 0 to score)
- Parsed sections preview
- Missing keywords tags
- "Fix My Resume" glowing CTA button
- "Edit Manually" secondary button

### Fix Resume Comparison Page

**Layout:**
- Split view: 50/50
- Left: Original version
- Right: Optimized version
- Top: Score comparison (before/after)
- Bottom: Action buttons

**Score Comparison:**
- Two circular progress meters side by side
- Arrow between them showing improvement
- Delta badge (e.g., "+15 points")

**Split View:**
- Synchronized scrolling
- Highlighted differences:
  - Additions: Green left border + light green background
  - Removals: Red left border + light red background
  - Modifications: Blue left border + light blue background
- Hover on change: Show tooltip with explanation

**Change Cards:**
- Each improvement as a card
- Change type badge (Added, Removed, Modified)
- Before/After text
- Reason for change
- Accept/Reject buttons
- Accept: Green checkmark button
- Reject: Red X button

**Action Buttons:**
- Bottom toolbar
- Accept All button
- Reject All button
- Apply Selected button (primary)
- Cancel button

### Resume Version History Page

**Layout:**
- Timeline view on left (30% width)
- Version preview on right (70% width)

**Timeline:**
- Vertical timeline
- Each version: Date, time, score badge, thumbnail
- Current version highlighted
- Click to preview
- Restore button on hover

**Version Preview:**
- Full resume preview
- Top: Version info (date, score, changes summary)
- Compare button (opens comparison view)
- Restore button
- Download button

**Comparison View:**
- Similar to fix comparison
- Shows differences between selected version and current

### Analytics Dashboard

**Layout:**
- Grid of chart cards
- Filters at top: Date range selector

**Charts:**

1. **Score Trend Line Chart**
   - X-axis: Dates
   - Y-axis: ATS score
   - Line with gradient fill
   - Data points on hover

2. **Keyword Coverage Radar Chart**
   - Multiple axes for keyword categories
   - Filled area showing coverage
   - Legend

3. **Version Comparison Bar Chart**
   - Bars for each version
   - Color-coded by score range
   - Hover: Show details

4. **Improvement Areas Donut Chart**
   - Segments for different improvement categories
   - Center: Total improvements
   - Legend with percentages

**Stats Cards:**
- Row of stat cards above charts
- Total resumes, average score, total improvements, time saved
- Animated count-up on load

### Settings Page

**Layout:**
- Sidebar navigation (left): Settings categories
- Content area (right): Settings forms

**Categories:**
- Profile
- Account
- Notifications
- Privacy
- Billing (if applicable)

**Profile Settings:**
- Profile photo upload
- Name, email, phone fields
- Bio textarea
- Save button

**Account Settings:**
- Change password form
- Email preferences
- Language selector
- Timezone selector

**Notification Settings:**
- Toggle switches for notification types
- Email notifications
- Push notifications
- Frequency selector

**Forms:**
- Use standard form design system
- Inline validation
- Success toast on save

### Profile Page

**Layout:**
- Header section with cover photo and profile photo
- Stats row (resumes, score, improvements)
- Tabs: Overview, Resumes, Activity
- Content area based on selected tab

**Header:**
- Cover photo (editable)
- Profile photo (editable, overlaps cover)
- Name and title
- Edit profile button (top-right)

**Stats Row:**
- 3-4 stat cards
- Icons + numbers + labels

**Tabs:**
- Horizontal tab navigation
- Active tab: Blue underline + glow

**Overview Tab:**
- Bio section
- Skills tags
- Recent activity

**Resumes Tab:**
- Grid of resume cards
- Similar to resume list page

**Activity Tab:**
- Timeline of all activities
- Filterable by type

### Admin Panel UI

**Layout:**
- Similar to authenticated layout
- Enhanced sidebar with admin sections
- Data tables for management

**Admin Sections:**
- Users management
- Resumes management
- Analytics overview
- System settings

**Data Tables:**
- Sortable columns
- Search and filters
- Bulk actions
- Row actions (Edit, Delete, View)
- Pagination

**User Management:**
- Table: Name, email, join date, status, actions
- Add user button
- Export button

### Error Pages (404, 500)

**Layout:**
- Centered content
- Full viewport height

**404 Page:**
- Large "404" text with gradient
- "Page not found" headline
- Friendly message
- Search bar (optional)
- "Go to Dashboard" button
- "Go to Home" button

**500 Page:**
- Large error icon
- "Something went wrong" headline
- Friendly message
- "Try again" button
- "Contact support" link

**Illustration:**
- Minimal, abstract illustration
- Matches dark theme
- Subtle animation

### Empty States

**General Pattern:**
- Centered in container
- Icon or illustration (grayscale with accent color)
- Headline (what's empty)
- Description (why it's empty or what to do)
- CTA button (primary action)

**Examples:**

1. **No Resumes:**
   - Icon: Document with plus
   - Headline: "No resumes yet"
   - Description: "Create your first resume to get started"
   - Button: "Create Resume"

2. **No Search Results:**
   - Icon: Magnifying glass
   - Headline: "No results found"
   - Description: "Try adjusting your search terms"
   - Button: "Clear filters"

3. **No Activity:**
   - Icon: Activity graph
   - Headline: "No activity yet"
   - Description: "Your recent actions will appear here"

### Loading States

**Patterns:**

1. **Page Loading:**
   - Full-page spinner with logo
   - Fade in content when loaded

2. **Section Loading:**
   - Skeleton screens matching content structure
   - Pulsing animation
   - Maintains layout (no content shift)

3. **Button Loading:**
   - Spinner replaces button text
   - Button disabled
   - Maintains button size

4. **Inline Loading:**
   - Small spinner next to text
   - "Loading..." text

**Skeleton Screens:**
- Gray rectangles matching content shape
- Subtle shimmer animation
- Used for: Resume cards, data tables, charts

### Toast Notifications

**Position:**
- Top-right corner
- Stack vertically if multiple
- Fixed position

**Structure:**
- Icon (left): Success checkmark, error X, warning triangle, info circle
- Message text (center)
- Close button (right)
- Progress bar at bottom (auto-dismiss timer)

**Variants:**

1. **Success:**
   - Background: `$color-success` with low opacity
   - Border: `$color-success`
   - Icon: Green checkmark
   - Glow: `$glow-success`

2. **Error:**
   - Background: `$color-error` with low opacity
   - Border: `$color-error`
   - Icon: Red X
   - Glow: `$glow-error`

3. **Warning:**
   - Background: `$color-warning` with low opacity
   - Border: `$color-warning`
   - Icon: Amber triangle

4. **Info:**
   - Background: `$color-primary-solid` with low opacity
   - Border: `$color-primary-solid`
   - Icon: Blue info circle

**Animation:**
- Slide in from right (250ms)
- Auto-dismiss after 5 seconds (configurable)
- Slide out on dismiss
- Hover: Pause auto-dismiss

## Responsive Design Strategy

### Breakpoints

```scss
$breakpoint-sm: 640px;   // Mobile
$breakpoint-md: 768px;   // Tablet
$breakpoint-lg: 1024px;  // Desktop
$breakpoint-xl: 1280px;  // Large desktop
$breakpoint-2xl: 1536px; // Extra large
```

### Mobile Adaptations

**Navigation:**
- Sidebar becomes drawer (overlay)
- Hamburger menu button in top bar
- Swipe to open/close

**Grids:**
- Multi-column grids become single column
- Maintain card styling

**Forms:**
- Full-width inputs
- Larger touch targets (min 44px)
- Simplified layouts

**Tables:**
- Horizontal scroll
- Or card-based layout for mobile

**Charts:**
- Responsive sizing
- Simplified on small screens
- Horizontal scroll if needed

**Typography:**
- Slightly smaller font sizes
- Maintain hierarchy

**Spacing:**
- Reduced padding/margins
- Maintain visual breathing room



## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

For this UI/UX redesign, correctness properties focus on verifying that the design system is consistently applied, all required components exist, accessibility standards are met, and the implementation matches the design specifications.

### Property 1: Design Token Completeness

*For any* design token category (colors, typography, spacing, shadows, animations), all required tokens within that category should be defined and accessible in the compiled CSS.

**Validates: Requirements 1.1, 1.2, 1.7, 15.2**

### Property 2: Spacing Grid Consistency

*For any* spacing token value, the value should be a multiple of 8px (the base grid unit).

**Validates: Requirements 1.3**

### Property 3: Border Radius Range Compliance

*For any* border-radius token, the value should fall within the range of 14-20px (or be 0 for no radius, or 9999px for full rounding).

**Validates: Requirements 1.4**

### Property 4: Animation Duration Range Compliance

*For any* animation duration token used for micro-interactions, the value should fall within the range of 150-250ms.

**Validates: Requirements 1.6**

### Property 5: Universal Page Coverage

*For any* page in the application (landing, register, login, forgot password, dashboard, resume list, resume builder, resume preview, ATS analyzer, PDF upload, fix comparison, version history, analytics, settings, profile, admin panel, 404, 500), the page template should include the design system CSS and should not contain legacy style references.

**Validates: Requirements 2.1, 2.3**

### Property 6: Layout Template Inheritance

*For any* authenticated page (dashboard, resume pages, analytics, settings, profile), the page template should extend the authenticated layout template. *For any* public page (landing, login, register, forgot password), the page template should extend the public layout template.

**Validates: Requirements 3.5, 4.6**

### Property 7: Sidebar Responsive Behavior

*For any* authenticated page, when the sidebar collapse state is toggled, the main content area width should adjust accordingly to utilize the available space.

**Validates: Requirements 3.4**

### Property 8: Form System Universal Application

*For any* form in the application (resume builder, login, register, PDF upload, settings, profile edit, admin forms), the form inputs should use the form design system component classes.

**Validates: Requirements 5.7**

### Property 9: Form Input Focus State

*For any* form input, when the input receives focus, the input should display a floating label animation, dark background, and soft border glow.

**Validates: Requirements 5.1, 5.2**

### Property 10: Form Input Error State

*For any* form input with validation errors, the input should display an error state with red border, red glow, and a descriptive error message below the input.

**Validates: Requirements 5.4**

### Property 11: Form Input Success State

*For any* form input that passes validation, the input should display a success state with green border and green glow.

**Validates: Requirements 5.5**

### Property 12: Form Inline Validation

*For any* form with validation, when validation is triggered, validation feedback should appear inline next to the relevant input fields.

**Validates: Requirements 5.3**

### Property 13: Component Library Completeness

*For any* component type in the required list (buttons with 4 variants, cards with 4 variants, alerts, badges, progress bars, circular progress, tabs, accordions, modals, dropdowns, pagination, tooltips, file upload UI, data tables, charts, empty states, sidebar navigation), the component should have corresponding CSS classes or template files defined.

**Validates: Requirements 6.1, 6.2, 6.3**

### Property 14: Interactive Component Hover Feedback

*For any* interactive component (buttons, cards, links, navigation items), when hovered, the component should display micro-interaction feedback through CSS transitions (lift effect, glow, or background change).

**Validates: Requirements 6.4, 10.5**

### Property 15: Component Reusability

*For any* component in the component library, the component should be defined in shared CSS/template files (not page-specific files) to enable reuse across all pages.

**Validates: Requirements 6.6**

### Property 16: Wizard Step Transition Animation

*For any* step transition in the resume builder wizard, the transition should include smooth CSS animations with appropriate duration and easing.

**Validates: Requirements 8.3, 8.7**

### Property 17: File Upload Drag State Feedback

*For any* file upload zone, when a file is dragged over the zone, the border glow intensity should increase compared to the default state.

**Validates: Requirements 9.2**

### Property 18: Upload Progress Indication

*For any* file upload operation, during the upload process, a progress indicator should be displayed and should update to reflect upload progress.

**Validates: Requirements 9.4**

### Property 19: Score Reveal Animation

*For any* completed upload or analysis, the score display should animate from 0 to the actual score value rather than appearing instantly.

**Validates: Requirements 9.5**

### Property 20: Improvement Highlighting

*For any* improvement displayed on the fix comparison page, the improvement should be highlighted with a subtle neon left border using an accent color.

**Validates: Requirements 10.2**

### Property 21: Chart Animation on Load

*For any* chart on the analytics dashboard, when data loads, the chart should animate smoothly into view rather than appearing instantly.

**Validates: Requirements 11.6**

### Property 22: WCAG Contrast Compliance

*For any* text and background color combination used in the UI, the contrast ratio should meet WCAG AA standards (minimum 4.5:1 for normal text, 3:1 for large text).

**Validates: Requirements 13.1**

### Property 23: Keyboard Navigation Support

*For any* interactive element (buttons, links, form inputs, navigation items), the element should be keyboard focusable and should have a proper tab order.

**Validates: Requirements 13.2**

### Property 24: ARIA Label Presence

*For any* interactive element that doesn't have visible text (icon buttons, image links), the element should include proper aria-label or aria-labelledby attributes.

**Validates: Requirements 13.3**

### Property 25: Focus State Visibility

*For any* focusable element, when the element receives keyboard focus, a clearly visible focus indicator (outline or box-shadow) should be displayed.

**Validates: Requirements 13.4**

### Property 26: Redundant Encoding for Color Information

*For any* UI element that uses color to convey information (success/error states, status indicators), the element should also include non-color indicators (icons, text labels, or patterns) for colorblind accessibility.

**Validates: Requirements 13.5**

### Property 27: Unused CSS Removal

*For any* Bootstrap component that is not used in the application, the component's CSS should not be included in the final compiled stylesheet.

**Validates: Requirements 14.2**

### Property 28: Image Lazy Loading

*For any* image element that is not in the initial viewport, the image should have the loading="lazy" attribute to enable lazy loading.

**Validates: Requirements 14.3**

### Property 29: Asset Compression

*For any* static asset file (CSS, JavaScript, images), the production version should be compressed/minified to reduce file size.

**Validates: Requirements 14.4**

## Error Handling

### Design System Loading Errors

**Scenario:** CSS files fail to load or are blocked

**Handling:**
- Implement fallback inline critical CSS for basic layout
- Display user-friendly error message if design system fails to load
- Log error to monitoring system
- Provide "Reload" button to retry

### Component Rendering Errors

**Scenario:** JavaScript-dependent components fail to initialize

**Handling:**
- Ensure core functionality works without JavaScript (progressive enhancement)
- Display fallback static content for dynamic components
- Log component initialization errors
- Provide graceful degradation for animations and interactions

### Browser Compatibility Issues

**Scenario:** Older browsers don't support modern CSS features

**Handling:**
- Use CSS feature detection (@supports)
- Provide fallback styles for unsupported features
- Test on target browsers (last 2 versions of major browsers)
- Display upgrade notice for very old browsers

### Accessibility Errors

**Scenario:** Screen readers or keyboard navigation fails

**Handling:**
- Ensure semantic HTML as foundation
- Test with actual screen readers (NVDA, JAWS, VoiceOver)
- Provide skip links for keyboard navigation
- Include ARIA landmarks for page structure

### Performance Issues

**Scenario:** Animations cause jank or slow page loads

**Handling:**
- Use CSS transforms and opacity for animations (GPU-accelerated)
- Implement lazy loading for below-fold content
- Monitor performance metrics (Core Web Vitals)
- Disable animations on low-end devices (prefers-reduced-motion)

### Theme Loading Race Conditions

**Scenario:** Content flashes with wrong styling before theme loads

**Handling:**
- Inline critical CSS in HTML head
- Use CSS custom properties for instant theme application
- Implement loading screen until critical styles load
- Prevent FOUC (Flash of Unstyled Content)

## Testing Strategy

### Dual Testing Approach

This redesign requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** verify specific examples, edge cases, and error conditions:
- Specific component rendering (e.g., primary button renders correctly)
- Specific page layouts (e.g., dashboard includes all required sections)
- Edge cases (e.g., empty states, error pages)
- Integration points (e.g., form submission, file upload)

**Property-Based Tests** verify universal properties across all inputs:
- Design token consistency across all pages
- Component behavior across all variants
- Accessibility compliance across all interactive elements
- Responsive behavior across all breakpoints

Both testing approaches are complementary and necessary for comprehensive coverage.

### Testing Layers

#### 1. Visual Regression Testing

**Tool:** Percy, Chromatic, or BackstopJS

**Approach:**
- Capture screenshots of all pages in multiple states
- Compare against baseline screenshots
- Flag visual differences for review
- Test across multiple browsers and viewports

**Coverage:**
- All 20+ pages
- Component variants
- Interactive states (hover, focus, active)
- Responsive breakpoints

#### 2. CSS Unit Tests

**Tool:** Jest with jest-styled-components or CSS testing utilities

**Approach:**
- Test that design tokens are defined correctly
- Test that component classes apply correct styles
- Test that responsive styles apply at correct breakpoints
- Test that animations have correct timing

**Example Tests:**
```javascript
// Test design token existence
test('primary color token is defined', () => {
  const styles = getComputedStyle(document.documentElement);
  expect(styles.getPropertyValue('--color-primary-solid')).toBe('#0066ff');
});

// Test spacing grid consistency
test('all spacing tokens are multiples of 8px', () => {
  const spacingTokens = ['--spacing-1', '--spacing-2', '--spacing-3'];
  spacingTokens.forEach(token => {
    const value = parseInt(getComputedStyle(document.documentElement).getPropertyValue(token));
    expect(value % 8).toBe(0);
  });
});
```

#### 3. Component Integration Tests

**Tool:** Django test framework with Selenium or Playwright

**Approach:**
- Test that components render correctly in templates
- Test that interactive components respond to user actions
- Test that forms validate and submit correctly
- Test that navigation works across pages

**Example Tests:**
```python
def test_sidebar_collapse_expands_content(self):
    """Test that collapsing sidebar expands main content area"""
    # Property 7: Sidebar Responsive Behavior
    self.client.login(username='testuser', password='password')
    response = self.client.get('/dashboard/')
    
    # Check that sidebar and main content exist
    self.assertContains(response, 'class="sidebar"')
    self.assertContains(response, 'class="main-content"')
    
    # Test with JavaScript that toggling sidebar changes main content width
    # (This would be done with Selenium/Playwright for full interaction testing)
```

#### 4. Accessibility Tests

**Tool:** axe-core, Pa11y, or WAVE

**Approach:**
- Automated accessibility scanning of all pages
- Test keyboard navigation flows
- Test screen reader compatibility
- Test color contrast ratios

**Example Tests:**
```python
def test_wcag_contrast_compliance(self):
    """Test that text/background combinations meet WCAG AA standards"""
    # Property 22: WCAG Contrast Compliance
    color_combinations = [
        ('#f5f5f5', '#0a0a0a'),  # Primary text on base background
        ('#a3a3a3', '#0a0a0a'),  # Secondary text on base background
    ]
    
    for text_color, bg_color in color_combinations:
        contrast_ratio = calculate_contrast_ratio(text_color, bg_color)
        self.assertGreaterEqual(contrast_ratio, 4.5)  # WCAG AA for normal text

def test_keyboard_navigation(self):
    """Test that all interactive elements are keyboard accessible"""
    # Property 23: Keyboard Navigation Support
    self.client.login(username='testuser', password='password')
    response = self.client.get('/dashboard/')
    
    # Parse HTML and find all interactive elements
    soup = BeautifulSoup(response.content, 'html.parser')
    interactive_elements = soup.find_all(['button', 'a', 'input', 'select', 'textarea'])
    
    for element in interactive_elements:
        # Check that element is focusable (has tabindex or is naturally focusable)
        self.assertTrue(
            element.get('tabindex') is not None or 
            element.name in ['button', 'a', 'input', 'select', 'textarea']
        )
```

#### 5. Performance Tests

**Tool:** Lighthouse, WebPageTest, or custom performance monitoring

**Approach:**
- Test page load times
- Test animation frame rates
- Test asset sizes
- Test Core Web Vitals (LCP, FID, CLS)

**Metrics:**
- First Contentful Paint < 1.8s
- Largest Contentful Paint < 2.5s
- Cumulative Layout Shift < 0.1
- First Input Delay < 100ms
- CSS bundle size < 100KB (gzipped)
- JavaScript bundle size < 200KB (gzipped)

#### 6. Cross-Browser Testing

**Tool:** BrowserStack or Sauce Labs

**Approach:**
- Test on target browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- Test on mobile browsers (iOS Safari, Chrome Mobile)
- Test responsive behavior at standard breakpoints
- Test fallbacks for unsupported features

**Coverage:**
- Desktop: Chrome, Firefox, Safari, Edge
- Mobile: iOS Safari, Chrome Mobile, Samsung Internet
- Breakpoints: 640px, 768px, 1024px, 1280px

### Property-Based Test Configuration

**Library:** Hypothesis (Python)

**Configuration:**
- Minimum 100 iterations per property test
- Each property test references its design document property
- Tag format: `# Feature: nextgencv-ui-redesign, Property {number}: {property_text}`

**Example Property Tests:**

```python
from hypothesis import given, strategies as st

@given(st.sampled_from(['landing', 'dashboard', 'login', 'register', 'resume-list']))
def test_all_pages_include_design_system(page_name):
    """
    Property 5: Universal Page Coverage
    For any page in the application, the page template should include 
    the design system CSS and should not contain legacy style references.
    
    Feature: nextgencv-ui-redesign, Property 5: Universal Page Coverage
    """
    response = client.get(f'/{page_name}/')
    
    # Check that design system CSS is included
    assert 'main.css' in response.content.decode()
    
    # Check that legacy CSS is not included
    assert 'style.css' not in response.content.decode()  # Old style file
    assert 'legacy' not in response.content.decode().lower()

@given(st.sampled_from(['primary', 'ghost', 'outline', 'gradient']))
def test_button_variants_have_hover_effects(variant):
    """
    Property 14: Interactive Component Hover Feedback
    For any interactive component, when hovered, the component should 
    display micro-interaction feedback through CSS transitions.
    
    Feature: nextgencv-ui-redesign, Property 14: Interactive Component Hover Feedback
    """
    # Get computed styles for button variant
    button_class = f'btn-{variant}'
    styles = get_css_rules_for_class(button_class)
    hover_styles = get_css_rules_for_class(f'{button_class}:hover')
    
    # Check that hover state has transition
    assert 'transition' in styles or 'transition' in hover_styles
    
    # Check that hover state changes something (transform, box-shadow, background)
    assert (
        hover_styles.get('transform') != styles.get('transform') or
        hover_styles.get('box-shadow') != styles.get('box-shadow') or
        hover_styles.get('background') != styles.get('background')
    )

@given(st.integers(min_value=1, max_value=16))
def test_spacing_tokens_follow_8px_grid(spacing_level):
    """
    Property 2: Spacing Grid Consistency
    For any spacing token value, the value should be a multiple of 8px.
    
    Feature: nextgencv-ui-redesign, Property 2: Spacing Grid Consistency
    """
    token_name = f'--spacing-{spacing_level}'
    styles = getComputedStyle(document.documentElement)
    token_value = styles.getPropertyValue(token_name)
    
    if token_value:  # Token exists
        # Convert to pixels and check if multiple of 8
        px_value = parse_css_value_to_px(token_value)
        assert px_value % 8 == 0, f'{token_name} = {px_value}px is not a multiple of 8'
```

### Test Execution Strategy

**Development Phase:**
1. Run unit tests on every code change (pre-commit hook)
2. Run visual regression tests on pull requests
3. Run accessibility tests on pull requests
4. Run property-based tests in CI/CD pipeline

**Pre-Release Phase:**
1. Full cross-browser testing
2. Performance testing and optimization
3. Manual QA of all user flows
4. Accessibility audit with real assistive technologies

**Post-Release Phase:**
1. Monitor real user performance metrics
2. Collect user feedback on design
3. A/B test design variations
4. Continuous accessibility monitoring

### Success Criteria

The UI redesign is considered successful when:

1. **All property tests pass** (100% pass rate)
2. **Visual regression tests show no unintended changes** (all changes reviewed and approved)
3. **Accessibility score ≥ 95** (Lighthouse accessibility audit)
4. **Performance score ≥ 90** (Lighthouse performance audit)
5. **Cross-browser compatibility** (all features work on target browsers)
6. **Zero legacy styling** (all old CSS removed)
7. **User feedback positive** (>80% approval in user testing)

## Migration Strategy

### Phase 1: Foundation (Week 1-2)

**Objective:** Establish design system foundation

**Tasks:**
1. Create design token files (SCSS variables and CSS custom properties)
2. Set up SCSS architecture and build process
3. Customize Bootstrap via SCSS overrides
4. Create base layout templates (authenticated, public)
5. Document design system

**Deliverables:**
- `_tokens/` directory with all token files
- `main.scss` with proper import structure
- Base layout templates
- Design system documentation

**Testing:**
- Unit tests for token definitions
- Build process verification

### Phase 2: Component Library (Week 3-4)

**Objective:** Build reusable component library

**Tasks:**
1. Create button components (all variants)
2. Create card components (all variants)
3. Create form components (inputs, labels, validation)
4. Create navigation components (sidebar, top bar)
5. Create feedback components (alerts, toasts, modals)
6. Create data visualization components (charts, progress)
7. Document each component with usage examples

**Deliverables:**
- `_components/` directory with all component files
- Component documentation
- Storybook or style guide (optional)

**Testing:**
- Unit tests for each component
- Visual regression tests for component variants
- Accessibility tests for interactive components

### Phase 3: Page Migration (Week 5-8)

**Objective:** Migrate all pages to new design system

**Priority Order:**
1. **High Priority:** Landing, Login, Register, Dashboard (most visible)
2. **Medium Priority:** Resume List, Resume Builder, PDF Upload (core features)
3. **Low Priority:** Settings, Profile, Admin Panel (less frequently used)

**Approach per Page:**
1. Create new template using layout and components
2. Migrate page-specific logic
3. Remove legacy styles
4. Test functionality
5. Run visual regression tests
6. Get stakeholder approval

**Deliverables:**
- All page templates migrated
- Legacy templates removed
- Page-specific SCSS files (minimal)

**Testing:**
- Integration tests for each page
- Visual regression tests
- User acceptance testing

### Phase 4: Polish and Optimization (Week 9-10)

**Objective:** Refine details and optimize performance

**Tasks:**
1. Add micro-interactions and animations
2. Optimize asset loading (lazy loading, compression)
3. Remove unused CSS
4. Cross-browser testing and fixes
5. Accessibility audit and fixes
6. Performance optimization
7. Final QA

**Deliverables:**
- Polished, production-ready UI
- Performance optimization report
- Accessibility audit report
- Cross-browser compatibility report

**Testing:**
- Full test suite execution
- Performance testing
- Accessibility testing
- Cross-browser testing
- User acceptance testing

### Phase 5: Deployment and Monitoring (Week 11)

**Objective:** Deploy to production and monitor

**Tasks:**
1. Deploy to staging environment
2. Final stakeholder review
3. Deploy to production (gradual rollout if possible)
4. Monitor performance metrics
5. Monitor error logs
6. Collect user feedback
7. Address critical issues

**Deliverables:**
- Production deployment
- Monitoring dashboard
- User feedback collection system

**Testing:**
- Smoke tests in production
- Real user monitoring
- A/B testing (if applicable)

### Rollback Plan

**Trigger Conditions:**
- Critical accessibility issues discovered
- Performance degradation > 50%
- Major functionality broken
- Negative user feedback > 50%

**Rollback Process:**
1. Revert to previous version via version control
2. Communicate issue to stakeholders
3. Analyze root cause
4. Fix issues in development
5. Re-test thoroughly
6. Re-deploy when ready

### Risk Mitigation

**Risk:** Breaking existing functionality during migration

**Mitigation:**
- Comprehensive integration tests before migration
- Gradual page-by-page migration
- Keep legacy templates as backup during transition
- Thorough QA of each migrated page

**Risk:** Performance regression from new CSS/animations

**Mitigation:**
- Performance testing at each phase
- Optimize assets before deployment
- Use CSS transforms for animations (GPU-accelerated)
- Implement lazy loading

**Risk:** Accessibility issues not caught in testing

**Mitigation:**
- Automated accessibility testing in CI/CD
- Manual testing with screen readers
- User testing with people with disabilities
- Accessibility audit by expert

**Risk:** Browser compatibility issues

**Mitigation:**
- Test on target browsers throughout development
- Use feature detection and fallbacks
- Polyfills for unsupported features
- Clear browser support policy

## Conclusion

This design document provides a comprehensive blueprint for transforming NextGenCV into a premium, futuristic, dark-themed SaaS product. The design system approach ensures consistency across all pages while the detailed component specifications enable efficient implementation.

The correctness properties provide clear, testable criteria for validating the implementation, while the testing strategy ensures comprehensive coverage through both unit tests and property-based tests. The migration strategy provides a practical roadmap for executing the redesign in manageable phases with clear deliverables and risk mitigation.

By following this design, NextGenCV will achieve a cohesive, accessible, performant, and visually stunning user interface that matches the quality expectations of a 2026 AI-powered SaaS product.
