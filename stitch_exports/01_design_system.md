---
name: Technical Obsidian
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#bcc9cd'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#869397'
  outline-variant: '#3d494c'
  surface-tint: '#4cd7f6'
  primary: '#4cd7f6'
  on-primary: '#003640'
  primary-container: '#06b6d4'
  on-primary-container: '#00424f'
  inverse-primary: '#00687a'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb873'
  on-tertiary: '#4b2800'
  tertiary-container: '#e89337'
  on-tertiary-container: '#5b3200'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#acedff'
  primary-fixed-dim: '#4cd7f6'
  on-primary-fixed: '#001f26'
  on-primary-fixed-variant: '#004e5c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdcbf'
  tertiary-fixed-dim: '#ffb873'
  on-tertiary-fixed: '#2d1600'
  on-tertiary-fixed-variant: '#6a3b00'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
  surface-base: '#050505'
  surface-elevated: '#0D0D0F'
  surface-overlay: '#18181B'
  border-subtle: rgba(255, 255, 255, 0.08)
  border-strong: '#27272A'
  text-primary: '#FFFFFF'
  text-secondary: '#A1A1AA'
  text-tertiary: '#71717A'
typography:
  display:
    fontFamily: Geist
    fontSize: 3.5rem
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: Geist
    fontSize: 2.25rem
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.03em
  headline-lg-mobile:
    fontFamily: Geist
    fontSize: 1.75rem
    fontWeight: '600'
    lineHeight: '1.25'
    letterSpacing: -0.025em
  headline-md:
    fontFamily: Geist
    fontSize: 1.5rem
    fontWeight: '500'
    lineHeight: '1.3'
    letterSpacing: -0.02em
  headline-sm:
    fontFamily: Geist
    fontSize: 1.25rem
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: -0.015em
  body-lg:
    fontFamily: Geist
    fontSize: 1.125rem
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: -0.01em
  body-md:
    fontFamily: Geist
    fontSize: 0.9375rem
    fontWeight: '400'
    lineHeight: '1.55'
    letterSpacing: -0.005em
  body-sm:
    fontFamily: Geist
    fontSize: 0.8125rem
    fontWeight: '400'
    lineHeight: '1.5'
    letterSpacing: '0'
  label-md:
    fontFamily: Geist
    fontSize: 0.8125rem
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Geist
    fontSize: 0.6875rem
    fontWeight: '500'
    lineHeight: '1.2'
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 2rem
  margin: 1rem
  margin-tablet: 2rem
  margin-desktop: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
  space-2xl: 4rem
---

## Brand & Style

This design system embodies the ethos of precision engineering, technical craftsmanship, and high-density developer infrastructure. Tailored for specialized cloud environments and next-generation software development tooling, the visual language merges absolute minimalism with tactile instrument panels.

The aesthetic channels deep, low-luminance canvas architectures—anchored by pitch black surfaces, glassmorphic atmospheric depth, hairline delineation, and high-precision typographic rhythm. The experience should evoke the sensation of operating a finely tuned console: silent, responsive, razor-sharp, and unencumbered by gratuitous ornamentation. Interactivity is signaled via micro-glows, muted slate metadata layers, and targeted electric cyan feedback points that illuminate key operations without breaking cognitive focus.

## Colors

The color architecture is built around a pitch-black foundation (`#050505`), engineered to minimize eye strain during intensive technical workflows and maximize the contrast of monochromatic hierarchies. 

- **Primary Accent (`#06B6D4`)**: Electric cyan serves as the functional beacon. It is reserved for focused states, critical triggers, and active system signals.
- **Secondary Accent (`#10B981`)**: Precision emerald denotes system health, operational uptime, and affirmative deployment signals.
- **Neutral & Surface Structure**: The canvas relies on `surface-base` (`#050505`) transitioning to `surface-elevated` (`#0D0D0F`) and frosted backdrops (`rgba(15, 15, 15, 0.65)`).
- **Hairline Alpha Borders**: Structural division rejects heavy solid fills; boundaries are defined using `rgba(255, 255, 255, 0.08)` to yield featherlight edges that recede under ambient lighting.
- **Text Layers**: Primary content uses pure optical white (`#FFFFFF`), supporting text uses neutral zinc (`#A1A1AA`), and metadata/labels utilize deep slate (`#71717A`).

## Typography

Typography balances Swiss geometric purity with strict developer utility. The system relies on **Geist** across all primary prose, structural headers, and interface labels.

### Structural Tracking & Kerning
Geist features tight, technical letter-spacing at display and headline scales to maintain high visual mass without requiring bold weight inflation. As font size decreases into metadata tiers, tracking opens subtly to maintain scannability in dark viewports.

### Monospace Integration
While Geist anchors all typographic roles, paired monospaced treatments (such as Geist Mono or JetBrains Mono) must be deployed for all execution metrics, commit hashes, latency figures, environment paths, and code snippets at the same size scales as `body-sm` and `label-sm`.

## Layout & Spacing

The spatial architecture adheres to a rigorous 4px baseline grid, creating consistent metric alignment across dense dashboard frames and expansive documentation views.

### Grid Dynamics
- **Desktop (1200px+)**: 12-column dynamic grid with `2rem` gutters and max-width bounded at `1440px`. Edge margins are fixed at `3rem` or auto-centered.
- **Tablet (768px - 1199px)**: 8-column layout with `1.5rem` gutters and `2rem` outer padding. Sidebar navigation transitions to collapsible panels.
- **Mobile (<768px)**: 4-column flow with `1rem` gutters and `1rem` margins. Structural splits collapse into vertical stacks with unified card widths.

Component interiors enforce strict visual density: operational metadata pairs utilize `space-xs` and `space-sm` for immediate contextual cohesion, while decoupled system panels separate using `space-lg` to `space-xl`.

## Elevation & Depth

Elevation eschews heavy, diffuse dropshadows in favor of **structural illumination, glassmorphism, and low-contrast alpha outlines**. Depth is communicated through stacked transparency and ambient light transmission.

1. **Canvas (Base Level)**: Solid `#050505`. Absorbent, dark, infinite ground.
2. **Frosted Panel Tier**: Background `rgba(15, 15, 15, 0.65)` layered with `backdrop-filter: blur(16px) saturate(180%)`. Border rendered via `1px solid rgba(255, 255, 255, 0.08)`.
3. **Floating Controls & Modals**: Background `rgba(24, 24, 27, 0.85)` with `backdrop-blur-xl`, reinforced by a sharp outer perimeter: `0 0 0 1px rgba(255, 255, 255, 0.12)` and a tight occlusion shadow: `0 12px 32px -4px rgba(0, 0, 0, 0.6)`.
4. **Accent Glow**: Active cards and focused interactive controls cast a localized cyan ambient aura using `0 0 20px -4px rgba(6, 182, 212, 0.15)`.

## Shapes

The interface embraces a disciplined, soft-geometric shape profile (`roundedness: 1`). Radii are deliberately constrained to evoke hardware components, instrument displays, and modern CLI windows.

- **Micro Controls & Badges**: `0.25rem` (`4px`) border radius. Maintains sharp definition at low pixel volumes.
- **Containers, Cards & Inputs**: `0.5rem` (`8px`) border radius (`rounded-lg`). Creates structured modules that nest logically within the 4px spatial rhythm.
- **Dialogs & Overlay Modals**: `0.75rem` (`12px`) border radius (`rounded-xl`). Offers subtle softening for elevated floating planes without veering into playful or consumer pill forms.
- **Nested Geometry Rule**: Any inner container nested within an outer panel must feature a corner radius equal to or smaller than the parent radius minus the intervening padding.

## Components

### Buttons
- **Primary**: Background `#FFFFFF`, text `#050505`, font weight `500`. Hover brings high-contrast opacity to `90%` and a subtle cyan rim glow.
- **Secondary / Ghost**: Background `rgba(255, 255, 255, 0.04)`, border `1px solid rgba(255, 255, 255, 0.08)`, text `#FFFFFF`. Hover introduces background `rgba(255, 255, 255, 0.08)` and border `rgba(255, 255, 255, 0.15)`.
- **Destructive**: Background `rgba(239, 68, 68, 0.1)`, border `1px solid rgba(239, 68, 68, 0.2)`, text `#F87171`.

### Input Fields
- **Default**: Height `40px`, background `rgba(15, 15, 15, 0.6)`, border `1px solid rgba(255, 255, 255, 0.08)`, text `#FFFFFF`, placeholder `#71717A`. Radius is `4px`.
- **Focus**: Border shifts to `#06B6D4` with `box-shadow: 0 0 0 1px #06B6D4, 0 0 16px -4px rgba(6, 182, 212, 0.3)`.

### Cards & Panels
- Constructed with backdrop blur (`blur(16px)`), background `rgba(15, 15, 15, 0.65)`, and border `1px solid rgba(255, 255, 255, 0.08)`. Padding strictly adheres to `1.5rem` (`space-lg`). Hover states lighten the border to `rgba(255, 255, 255, 0.15)`.

### Chips & Status Badges
- **Status Chips**: Height `24px`, padding `0 8px`, font size `0.6875rem`, monospace tracking.
- **Online / Running**: Dot indicator `#10B981` with pulse ring, background `rgba(16, 185, 129, 0.08)`, border `1px solid rgba(16, 185, 129, 0.2)`, text `#34D399`.
- **Syncing / Active**: Dot indicator `#06B6D4`, background `rgba(6, 182, 212, 0.08)`, border `1px solid rgba(6, 182, 212, 0.2)`, text `#67E8F9`.

### Selection Controls (Checkboxes & Radios)
- Dimension `16px x 16px`, background `rgba(255, 255, 255, 0.05)`, border `1px solid rgba(255, 255, 255, 0.15)`. Checked state fills `#06B6D4` with a dark `#050505` glyph.

### Terminal & Code Blocks
- Full bleed or panel-inset with background `#0A0A0C`, hair-thin top border `rgba(255, 255, 255, 0.06)`, and syntax highlighting calibrated against cyan, emerald, and muted slate accents.