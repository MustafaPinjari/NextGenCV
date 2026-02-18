# NextGenCV Design System - SCSS Architecture

This directory contains the SCSS source files for the NextGenCV design system. The architecture follows a modular, token-based approach for maintainability and consistency.

## Directory Structure

```
scss/
├── tokens/           # Design tokens (colors, typography, spacing, etc.)
│   ├── _colors.scss
│   ├── _typography.scss
│   ├── _spacing.scss
│   ├── _shadows.scss
│   ├── _animations.scss
│   └── _borders.scss
├── base/            # Base styles and resets
│   ├── _reset.scss
│   └── _global.scss
├── utilities/       # Mixins and helper functions
│   └── _mixins.scss
├── components/      # Component styles (to be added)
├── layouts/         # Layout templates (to be added)
├── pages/          # Page-specific styles (to be added)
└── main.scss       # Main entry point
```

## Design Tokens

Design tokens are the foundation of the design system. They define all visual values (colors, spacing, typography, etc.) in a single source of truth.

### Token Categories

1. **Colors** (`tokens/_colors.scss`)
   - Base colors (backgrounds, surfaces)
   - Accent colors (primary, secondary)
   - Semantic colors (success, warning, error)
   - Text colors
   - Border colors

2. **Typography** (`tokens/_typography.scss`)
   - Font families
   - Font sizes (xs to 6xl)
   - Font weights
   - Line heights
   - Letter spacing

3. **Spacing** (`tokens/_spacing.scss`)
   - 8px grid system
   - Spacing scale (0 to 16)

4. **Shadows** (`tokens/_shadows.scss`)
   - Soft shadows (sm, md, lg)
   - Glow effects (primary, secondary, success, error)

5. **Animations** (`tokens/_animations.scss`)
   - Duration values (fast, normal, slow)
   - Easing functions

6. **Borders** (`tokens/_borders.scss`)
   - Border radius values (sm to xl, full)

## CSS Custom Properties

All design tokens are exported as CSS custom properties (CSS variables) for runtime theming. This allows for:

- Dynamic theme switching
- Easy customization
- Better browser DevTools support

Example usage:
```css
.my-component {
  background-color: var(--color-surface);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}
```

## Compilation

### Prerequisites

Install libsass:
```bash
pip install libsass
```

### Compile SCSS

**Single compilation:**
```bash
python compile_scss.py
```

**Watch mode (development):**
```bash
python compile_scss.py --watch
```

**Production build (minified):**
```bash
python compile_scss.py --production
```

### Output

Compiled CSS is output to: `static/css/design-system.css`

## Usage in Django Templates

Include the compiled CSS in your base template:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/design-system.css' %}">
```

## Best Practices

1. **Use Design Tokens**: Always use design tokens (SCSS variables or CSS custom properties) instead of hardcoded values.

2. **Follow BEM Naming**: Use BEM (Block Element Modifier) methodology for component class names.
   ```scss
   .card { }
   .card__header { }
   .card__header--highlighted { }
   ```

3. **Use Mixins**: Leverage utility mixins for common patterns.
   ```scss
   .my-component {
     @include hover-lift;
     @include glass-effect;
   }
   ```

4. **Responsive Design**: Use responsive mixins for breakpoints.
   ```scss
   .my-component {
     padding: var(--spacing-2);
     
     @include md {
       padding: var(--spacing-4);
     }
   }
   ```

5. **Avoid Nesting Too Deep**: Keep nesting to 3 levels maximum for maintainability.

6. **Component Isolation**: Each component should be self-contained and reusable.

## Adding New Components

When adding new components:

1. Create a new file in `components/` directory: `_component-name.scss`
2. Import it in `main.scss`
3. Use design tokens and mixins
4. Follow BEM naming convention
5. Document component variants and usage

Example:
```scss
// components/_button.scss
.btn {
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-lg);
  font-weight: var(--font-weight-medium);
  @include transition(all);
  
  &--primary {
    background: var(--color-primary-solid);
    color: white;
    
    &:hover {
      @include glow(var(--color-primary-solid));
    }
  }
}
```

## Maintenance

- Keep design tokens in sync with the design document
- Update CSS custom properties when tokens change
- Recompile after any SCSS changes
- Test across all supported browsers
- Validate accessibility (contrast ratios, focus states)

## Resources

- [SCSS Documentation](https://sass-lang.com/documentation)
- [BEM Methodology](http://getbem.com/)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
