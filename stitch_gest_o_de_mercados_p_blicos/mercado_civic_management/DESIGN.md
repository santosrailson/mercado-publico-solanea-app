# Design System Strategy: The Civic Ledger

## 1. Overview & Creative North Star
This design system is built upon the Creative North Star of **"The Civic Ledger."** In the context of a public market—a place of tradition, commerce, and community—the digital interface must act as a sophisticated, authoritative anchor. We are moving away from the "cluttered admin dashboard" aesthetic toward a **High-End Editorial** experience. 

The goal is to provide a sense of "Institutional Fluidity." We achieve this through a "No-Line" philosophy, where the architecture of the page is defined by light, shadow, and tonal depth rather than rigid strokes. By utilizing intentional asymmetry in dashboard layouts and high-contrast typographic scales, we transform mundane management tasks into a premium oversight experience.

## 2. Colors & Surface Architecture
The palette is rooted in the "Navy & Emerald" tradition of financial institutions but executed with a modern, layered depth.

### The "No-Line" Rule
Traditional management systems rely on 1px borders to separate data. In this system, **borders are prohibited for sectioning.** Boundaries must be defined through:
- **Background Color Shifts:** Use `surface-container-low` for secondary sections sitting on a `surface` background.
- **Tonal Transitions:** Define high-priority areas using the `surface-container-highest` token to naturally pull the eye toward the most critical data.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of premium cardstock. 
- **Base Layer:** `surface` (#f7f9fc) for the main application background.
- **Secondary Containers:** `surface-container-low` (#f2f4f7) for sidebars or grouping related widgets.
- **Interactive Layers:** `surface-container-lowest` (#ffffff) for primary data cards and input forms to provide maximum "pop" against the grey background.

### The "Glass & Gradient" Rule
To elevate the "Institutional" feel into something "Premium":
- **Signature Textures:** For primary call-to-actions or header backgrounds, use a subtle linear gradient from `primary` (#00113a) to `primary_container` (#002366). This adds a "soul" to the navy blue that flat color cannot replicate.
- **Floating Glass:** Use `surface_container_lowest` with an 80% opacity and a `20px` backdrop-blur for floating navigation or top-level alerts.

## 3. Typography: The Editorial Scale
We utilize **Inter** to create a typographic hierarchy that feels like a modern financial report.

*   **Display (The Headline Metric):** Use `display-md` or `display-lg` for total revenue or market occupancy rates. This creates a "Display-First" impact that immediately signals authority.
*   **Headlines & Titles:** `headline-sm` should be used for section titles (e.g., "Vendor Compliance"), providing a clear, bold entry point.
*   **The Body:** Use `body-md` for general data and `label-md` for metadata. 
*   **Contrast as Navigation:** We use the `on_surface_variant` (#444650) for secondary labels and `on_surface` (#191c1e) for primary data values. This high-contrast ratio ensures high readability for market administrators.

## 4. Elevation & Depth
Depth in this system is achieved through **Tonal Layering**, not structural boxes.

*   **The Layering Principle:** Place a `surface-container-lowest` card on top of a `surface-container-low` background. This creates a soft, natural lift without the need for heavy-handed shadows.
*   **Ambient Shadows:** For floating elements (Modals, Dropdowns), use a shadow with a blur of `24px` and an opacity of `6%`. The shadow color must be a tinted version of `on_surface` (a deep navy tint) to mimic natural light passing through glass.
*   **The "Ghost Border" Fallback:** If a border is required for accessibility, use the `outline_variant` token at **15% opacity**. This creates a "Ghost Border" that guides the eye without cluttering the visual field.

## 5. Components

### Dashboard Cards
Cards must never use dividers. Separate the "Header" from the "Content" using a vertical spacing of `2rem` (from the spacing scale). Use `surface_container_lowest` for the card body and a `primary_fixed` subtle top-accent bar (2px) to denote "Trust/Active" status.

### Data Tables
Tables are the heart of a market management system. 
- **Row Styling:** No horizontal lines. Use alternating background shifts between `surface` and `surface-container-low` on hover.
- **Typography:** Column headers must be `label-sm` in all-caps with `0.05em` letter spacing for an institutional look.

### Status Badges
Status is communicated through "Quiet Color":
- **Active/Paid:** `secondary_container` (#9af2b9) background with `on_secondary_container` (#0e7143) text.
- **Overdue:** `error_container` (#ffdad6) background with `on_error_container` (#93000a) text.
- **Warning:** `tertiary_fixed` (#ffdbd0) background with `on_tertiary_fixed_variant` (#783018) text.
*Badges should use `full` (9999px) roundedness for a soft, professional pill shape.*

### Buttons
- **Primary:** Linear gradient from `primary` to `primary_container`. High-contrast `on_primary` text.
- **Secondary:** `surface_container_high` background with `on_surface` text. No border.
- **Tertiary:** Text-only using `primary` color, with an `underline` appearing only on hover.

### Market-Specific Components
- **Stall Occupancy Map:** Use `surface-container-highest` for vacant stalls and `secondary` (Emerald) for occupied stalls.
- **Fiscal Health Sparklines:** Use `secondary` for the stroke color to represent growth and financial success.

## 6. Do's and Don'ts

### Do:
- **Use White Space as a Separator:** If two elements feel too close, increase the padding rather than adding a line.
- **Lean into Emerald:** Use `secondary` for success states and "High-Status" metrics to reinforce the "Financial Success" brand pillar.
- **Align to a Soft Grid:** Ensure all elements align to a `0.5rem` (8px) base unit, but allow for asymmetrical hero sections to maintain the editorial feel.

### Don't:
- **No 100% Black:** Never use `#000000`. Use `on_surface` (#191c1e) for deep blacks to maintain the institutional "Navy" tint.
- **No Default Drop Shadows:** Never use the standard `0px 2px 4px` shadow. It looks "template-like." Always use the Ambient Shadow specification.
- **No Cluttered Lists:** Avoid using dividers in lists. Use a `1.5rem` vertical gap between list items to let the data breathe.