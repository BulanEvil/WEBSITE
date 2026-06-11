# Design

## Overview

Evergold is a B2B international trade website for industrial equipment parts and generator sets. The design should communicate supply reliability, export readiness, and product clarity for global buyers.

The visual direction is international trade: clean, structured, practical, and confident. It should look more like a professional supplier and less like a generic SaaS landing page.

## Visual Theme

- Brand feel: professional, international, dependable.
- Visual language: industrial precision, clear product hierarchy, restrained confidence.
- Primary surfaces: light, fast, readable pages with strong structure.
- Density: moderately information-rich, but never crowded.
- Motion: minimal and purposeful. Hover states and small transitions are enough.

## Color

Use a restrained industrial palette with warm trade accents.

- Background: near-white, cool gray, or very light blue-gray.
- Surface: white or subtle cool neutral.
- Text: deep charcoal, not pure black.
- Primary accent: deep teal or marine green for trust and industrial reliability.
- Secondary accent: muted amber, brass, or copper for trade warmth and emphasis.
- Lines: low-contrast cool gray.
- Avoid: AI-purple gradients, neon cyber colors, beige-heavy palettes, dark blue/slate dominance, and decorative bokeh/orb backgrounds.

Suggested starting tokens:

```css
:root {
  --bg: #f5f7f8;
  --surface: #ffffff;
  --ink: #172026;
  --muted: #5e6a72;
  --line: #dbe3e7;
  --accent: #176b6f;
  --accent-strong: #0d4649;
  --trade-warm: #b8793a;
}
```

Future redesigns may convert these to OKLCH, but the visible direction should remain stable.

## Typography

Use legible, globally available sans-serif typography. The first production pass can use system fonts for speed and reliability.

- Base font: Arial, Helvetica, or a system sans stack.
- Headings: confident, compact, and readable.
- Body copy: short lines, practical language, no dense marketing paragraphs.
- Labels: use sparingly. Avoid repeating tiny uppercase kickers above every section.
- Avoid: decorative serif editorial styling, excessive mono type, and fashion-magazine typography.

## Layout

The site should be built for scanning and RFQ conversion.

- Header: clear brand name, product categories, about/company, contact/RFQ.
- Hero: show the actual supply focus immediately, not a vague slogan.
- Product categories: construction machinery parts, diesel engine parts, mining equipment parts, generator sets.
- Trust section: export support, product sourcing, quote response, global shipping language.
- Contact/RFQ section: email, WhatsApp if available, short RFQ path.
- Footer: company name, contact email, product categories, legal basics.

Use full-width sections with constrained inner content. Avoid stacking card inside card. Cards are acceptable for product categories, proof points, or repeated items.

## Components

### Buttons

- Primary CTA: RFQ or Email Sales.
- Secondary CTA: View Products or Company Information.
- Radius: 6-8px.
- Text should be concrete: "Email Sales", "Send RFQ", "View Product Categories".

### Cards

Use cards for repeated product categories and compact proof points. Keep them flat and sharp enough for B2B work. Avoid glossy glassmorphism.

### Forms

RFQ forms should be simple:

- Name
- Company
- Email
- Country
- Product or part number
- Message

Every field needs a visible label. Errors should be clear and practical.

### Imagery

The final website should use real or credible industrial imagery. Prefer product, warehouse, engine, machinery, generator, mining, and logistics visuals over generic abstract backgrounds.

Do not use dark blurred stock photos where parts cannot be inspected. If imagery is unavailable, use clean structured layouts and product category blocks rather than fake placeholders.

## Interaction

- Keep animation subtle: hover, focus, small reveal, or button state changes.
- Respect reduced motion.
- Do not use heavy scroll choreography or decorative motion systems.
- Mobile navigation should be simple and predictable.

## SEO And Content

Pages should support search and international buyers:

- Clear page titles and meta descriptions.
- Product category headings with practical keywords.
- English-first content, written plainly for global readers.
- Future multilingual expansion should preserve structure.

## Quality Bar

Before publishing a page:

- The first viewport clearly says what Evergold supplies.
- The main CTA is visible without hunting.
- Mobile text does not overflow or overlap.
- Product categories are scannable.
- Email contact is correct: sales@evergold.sg.
- The page avoids generic AI visual defaults.
- The site remains static and deploys cleanly through Cloudflare Pages.
