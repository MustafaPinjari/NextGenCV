# NextGenCV Design System Documentation

## Overview

The NextGenCV Design System is a comprehensive set of design tokens, components, patterns, and guidelines that define the visual language of the application. It establishes a premium, futuristic, dark-themed SaaS aesthetic that applies consistently across all pages and interactions.

## Design Philosophy

1. **Consistency Over Customization**: Every page follows the same visual language
2. **Premium Feel**: Dark cinematic backgrounds with soft glowing accents create a high-end experience
3. **Clarity Through Hierarchy**: Large typography, generous whitespace, and clear visual hierarchy guide users
4. **Subtle Motion**: Micro-interactions provide feedback without distraction
5. **Accessibility First**: Beautiful design that works for everyone

---

## Design Tokens

Design tokens are the foundational building blocks of the design system. They are reusable design values stored as CSS custom properties and SCSS variables, providing a single source of truth for all visual values.

### Color Palette

#### Base Colors

The foundation of our dark theme uses deep, rich blacks with subtle variations for depth and hierarchy.

| Token Name | Value | Usage |
|------------|-------|-------|
| `$color-base-bg` | `#0a0a0a` | Deep matte black - Main background |
| `$color-surface` | `#141414` | Slightly lighter dark - Card backgrounds |
| `$color-surface-elevated` | `#1a1a1a` | Elevated surfaces - Hover states, modals |

**Usage Guidelines:**
- Use `$color-base-bg` for the main page background
- Use `$color-surface` for card and panel backgrounds
- Use `$color-surface-elevated` for hover states, dropdowns, and modals
- Never use pure black (#000000) - it's too harsh

#### Accent Colors

Vibrant accent colors create visual interest and guide user attention.

| Token Name | Value | Usage |
|------------|-------|-------|
| `$color-primary` | `linear-gradient(135deg, #0066ff 0%, #00ccff 100%)` | Electric blue gradient - Primary actions |
| `$color-primary-solid` | `#0066ff` | Solid blue - Borders, text, icons |
| `$color-secondary` | `#6366f1` | Purple-blue - Secondary actions |
| `$color-secondary-glow` | `rgba(99, 102, 241, 0.3)` | Purple glow effect |

**Usage Guidelines:**
- Use `$color-primary` gradient for primary CTA buttons
- Use `$color-primary-solid` for borders, links, and icons
- Use `$color-secondary` for secondary actions and accents
- Apply glow effects sparingly for emphasis

#### Semantic Colors

Colors that convey meaning and status.

| Token Name | Value | Usage |
|------------|-------|-------|
| `$color-success` | `#10b981` | Soft neon green - Success states |
| `$color-success-glow` | `rgba(16, 185, 129, 0.2)` | Success glow effect |
| `$color-warning` | `#f59e0b` | Amber - Warning states |
| `$color-warning-glow` | `rgba(245, 158, 11, 0.2)` | Warning glow effect |
| `$color-error` | `#ef4444` | Soft red - Error states |
| `$color-error-glow` | `rgba(239, 68, 68, 0.2)` | Error glow effect |

**Usage Guidelines:**
- Always pair semantic colors with icons or text (don't rely on color alone)
- Use glow effects to draw attention to important states
- Maintain consistent meaning across the application

#### Text Colors

Hierarchical text colors for readability and emphasis.

| Token Name | Value | Usage |
|------------|-------|-------|
| `$color-text-primary` | `#f5f5f5` | Soft white - Primary text, headings |
| `$color-text-secondary` | `#a3a3a3` | Muted gray - Secondary text, labels |
| `$color-text-tertiary` | `#737373` | Darker gray - Tertiary text, placeholders |

**Usage Guidelines:**
- Use `$color-text-primary` for headings and important content
- Use `$color-text-secondary` for body text and labels
- Use `$color-text-tertiary` for placeholders and less important text
- Ensure sufficient contrast against backgrounds (WCAG AA minimum)

#### Border Colors

Subtle borders that define boundaries without overwhelming the design.

| Token Name | Value | Usage |
|------------|-------|-------|
| `$color-border` | `rgba(255, 255, 255, 0.08)` | Default borders |
| `$color-border-hover` | `rgba(255, 255, 255, 0.15)` | Hover state borders |
| `$color-border-focus` | `rgba(0, 102, 255, 0.5)` | Focus state borders |

**Usage Guidelines:**
- Use subtle borders to separate content without harsh lines
- Increase opacity on hover for interactive feedback
- Use accent color borders for focus states

---

### Typography

#### Font Families

| Token Name | Value | Usage |
|------------|-------|-------|
| `$font-primary` | `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | Body text, UI elements |
| `$font-display` | `'Space Grotesk', $font-primary` | Headlines, hero text |

**Usage Guidelines:**
- Use `$font-primary` for all body text and UI elements
- Use `$font-display` for large headlines and hero sections
- Always include fallback fonts for reliability

#### Font Sizes

Based on a modular scale for consistent hierarchy.

| Token Name | Value (rem) | Pixels | Usage |
|------------|-------------|--------|-------|
| `$font-size-xs` | 0.75rem | 12px | Small labels, captions |
| `$font-size-sm` | 0.875rem | 14px | Secondary text |
| `$font-size-base` | 1rem | 16px | Body text (default) |
| `$font-size-lg` | 1.125rem | 18px | Large body text |
| `$font-size-xl` | 1.25rem | 20px | Small headings |
| `$font-size-2xl` | 1.5rem | 24px | Section headings |
| `$font-size-3xl` | 1.875rem | 30px | Page headings |
| `$font-size-4xl` | 2.25rem | 36px | Large headings |
| `$font-size-5xl` | 3rem | 48px | Hero headings |
| `$font-size-6xl` | 3.75rem | 60px | Extra large hero text |

**Usage Guidelines:**
- Use `$font-size-base` (16px) as the default body text size
- Maintain clear hierarchy with at least 2-step jumps for headings
- Scale down font sizes on mobile for better readability

#### Font Weights

| Token Name | Value | Usage |
|------------|-------|-------|
| `$font-weight-normal` | 400 | Body text |
| `$font-weight-medium` | 500 | Emphasized text |
| `$font-weight-semibold` | 600 | Subheadings |
| `$font-weight-bold` | 700 | Headings, important text |

**Usage Guidelines:**
- Use normal weight for body text
- Use medium weight for subtle emphasis
- Use semibold for subheadings
- Use bold for main headings and important UI elements

#### Line Heights

| Token Name | Value | Usage |
|------------|-------|-------|
| `$line-height-tight` | 1.25 | Headings, compact text |
| `$line-height-normal` | 1.5 | Body text (default) |
| `$line-height-relaxed` | 1.75 | Long-form content |

**Usage Guidelines:**
- Use tight line height for headings to maintain visual impact
- Use normal line height for most body text
- Use relaxed line height for long-form reading content

#### Letter Spacing

| Token Name | Value | Usage |
|------------|-------|-------|
| `$letter-spacing-tight` | -0.02em | Large headings |
| `$letter-spacing-normal` | 0 | Body text (default) |
| `$letter-spacing-wide` | 0.025em | Small text, labels |
| `$letter-spacing-wider` | 0.05em | Uppercase text, buttons |

**Usage Guidelines:**
- Use tight spacing for large headings to improve readability
- Use normal spacing for body text
- Use wide spacing for small text and uppercase labels

---

### Spacing System

Based on an 8px grid system for consistent rhythm and alignment.

| Token Name | Value (rem) | Pixels | Usage |
|------------|-------------|--------|-------|
| `$spacing-0` | 0 | 0px | No spacing |
| `$spacing-1` | 0.5rem | 8px | Minimal spacing |
| `$spacing-2` | 1rem | 16px | Small spacing |
| `$spacing-3` | 1.5rem | 24px | Medium spacing |
| `$spacing-4` | 2rem | 32px | Large spacing |
| `$spacing-5` | 2.5rem | 40px | Extra large spacing |
| `$spacing-6` | 3rem | 48px | Section spacing |
| `$spacing-8` | 4rem | 64px | Large section spacing |
| `$spacing-10` | 5rem | 80px | Extra large section spacing |
| `$spacing-12` | 6rem | 96px | Hero section spacing |
| `$spacing-16` | 8rem | 128px | Maximum spacing |

**Usage Guidelines:**
- All spacing values must be multiples of 8px
- Use smaller values (1-3) for component internal spacing
- Use medium values (4-6) for component margins
- Use large values (8-16) for section spacing
- Maintain consistent spacing throughout the application

**Common Patterns:**
- Card padding: `$spacing-4` (32px)
- Button padding: `$spacing-2` `$spacing-4` (16px 32px)
- Section margins: `$spacing-8` (64px)
- Page padding: `$spacing-6` (48px)

---

### Shadows

Soft shadows and glows that add depth without harshness.

#### Standard Shadows

| Token Name | Value | Usage |
|------------|-------|-------|
| `$shadow-sm` | `0 2px 8px rgba(0, 0, 0, 0.3)` | Small elevation |
| `$shadow-md` | `0 4px 16px rgba(0, 0, 0, 0.4)` | Medium elevation |
| `$shadow-lg` | `0 8px 32px rgba(0, 0, 0, 0.5)` | Large elevation |

**Usage Guidelines:**
- Use `$shadow-sm` for cards and subtle elevation
- Use `$shadow-md` for dropdowns and popovers
- Use `$shadow-lg` for modals and overlays

#### Glow Effects

| Token Name | Value | Usage |
|------------|-------|-------|
| `$glow-primary` | `0 0 20px rgba(0, 102, 255, 0.3)` | Primary accent glow |
| `$glow-secondary` | `0 0 20px rgba(99, 102, 241, 0.3)` | Secondary accent glow |
| `$glow-success` | `0 0 20px rgba(16, 185, 129, 0.3)` | Success state glow |
| `$glow-error` | `0 0 20px rgba(239, 68, 68, 0.3)` | Error state glow |

**Usage Guidelines:**
- Use glow effects sparingly for emphasis
- Apply to focus states, hover states, and important CTAs
- Combine with border colors for cohesive effects

---

### Border Radius

Rounded corners that soften the interface.

| Token Name | Value (rem) | Pixels | Usage |
|------------|-------------|--------|-------|
| `$radius-sm` | 0.5rem | 8px | Small elements |
| `$radius-md` | 0.875rem | 14px | Medium elements |
| `$radius-lg` | 1rem | 16px | Large elements |
| `$radius-xl` | 1.25rem | 20px | Extra large elements |
| `$radius-full` | 9999px | Full | Circular elements |

**Usage Guidelines:**
- Use values between 14-20px for most components
- Use `$radius-full` for pills, badges, and circular elements
- Maintain consistent radius within component families

---

### Animation

Smooth, subtle animations that provide feedback without distraction.

#### Duration

| Token Name | Value | Usage |
|------------|-------|-------|
| `$duration-fast` | 150ms | Quick micro-interactions |
| `$duration-normal` | 250ms | Standard transitions |
| `$duration-slow` | 350ms | Complex animations |

**Usage Guidelines:**
- Use 150-250ms for micro-interactions (hover, focus)
- Use 250-350ms for page transitions and complex animations
- Never exceed 500ms for UI animations

#### Easing

| Token Name | Value | Usage |
|------------|-------|-------|
| `$easing-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | Standard easing |
| `$easing-in` | `cubic-bezier(0.4, 0, 1, 1)` | Ease in |
| `$easing-out` | `cubic-bezier(0, 0, 0.2, 1)` | Ease out |
| `$easing-bounce` | `cubic-bezier(0.68, -0.55, 0.265, 1.55)` | Bounce effect |

**Usage Guidelines:**
- Use `$easing-default` for most transitions
- Use `$easing-out` for elements entering the view
- Use `$easing-in` for elements leaving the view
- Use `$easing-bounce` sparingly for playful interactions

---

## Responsive Breakpoints

| Breakpoint | Value | Usage |
|------------|-------|-------|
| `$breakpoint-sm` | 640px | Mobile devices |
| `$breakpoint-md` | 768px | Tablets |
| `$breakpoint-lg` | 1024px | Desktop |
| `$breakpoint-xl` | 1280px | Large desktop |
| `$breakpoint-2xl` | 1536px | Extra large screens |

**Usage Guidelines:**
- Design mobile-first, then enhance for larger screens
- Test at all breakpoints during development
- Ensure touch targets are at least 44px on mobile

---

## Implementation

### CSS Custom Properties

Design tokens are implemented as CSS custom properties for runtime access:

```css
:root {
  /* Colors */
  --color-base-bg: #0a0a0a;
  --color-surface: #141414;
  --color-primary-solid: #0066ff;
  
  /* Typography */
  --font-primary: 'Inter', sans-serif;
  --font-size-base: 1rem;
  
  /* Spacing */
  --spacing-4: 2rem;
  
  /* Shadows */
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
  
  /* Animation */
  --duration-normal: 250ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
}
```

### SCSS Variables

Design tokens are also available as SCSS variables for compile-time usage:

```scss
@import 'tokens/colors';
@import 'tokens/typography';
@import 'tokens/spacing';
@import 'tokens/shadows';
@import 'tokens/animations';

.my-component {
  background: $color-surface;
  padding: $spacing-4;
  border-radius: $radius-lg;
  box-shadow: $shadow-md;
  transition: all $duration-normal $easing-default;
}
```

---

## Best Practices

### Do's

✅ Use design tokens for all visual values
✅ Maintain consistent spacing using the 8px grid
✅ Apply glow effects to focus states for accessibility
✅ Use semantic colors with non-color indicators
✅ Test color contrast ratios (WCAG AA minimum)
✅ Keep animations subtle and purposeful
✅ Document any custom values or exceptions

### Don'ts

❌ Don't use arbitrary color values
❌ Don't use spacing values that aren't multiples of 8px
❌ Don't rely on color alone to convey information
❌ Don't use pure black (#000000)
❌ Don't create animations longer than 500ms
❌ Don't override design tokens without good reason
❌ Don't use more than 3 font weights in a single view

---

## Accessibility Considerations

### Color Contrast

All text and background combinations must meet WCAG AA standards:
- Normal text (< 18px): Minimum 4.5:1 contrast ratio
- Large text (≥ 18px): Minimum 3:1 contrast ratio
- UI components: Minimum 3:1 contrast ratio

### Focus States

All interactive elements must have clearly visible focus states:
- Use `$color-border-focus` with `$glow-primary`
- Ensure focus indicators are at least 2px thick
- Never remove focus outlines without providing alternatives

### Motion

Respect user preferences for reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Version History

- **v1.0.0** (2026-02-15): Initial design system documentation
