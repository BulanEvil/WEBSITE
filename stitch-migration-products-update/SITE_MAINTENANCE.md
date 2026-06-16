# Evergold Static Site Maintenance

Current live working copy:

`stitch-migration-products-update/`

Preview URL:

`http://127.0.0.1:8765/stitch-migration-products-update/index.html`

## Top-Level Pages

- `index.html` - homepage.
- `products.html` - full product listing.
- `about.html` - company and global supply map page.
- `contact.html` - RFQ contact page with Annie and Joe QR codes.
- `styles.css` - shared layout, typography, header, product, contact, and QR popover styles.

## Product Pages

- `products/*.html` - individual product detail pages and category pages.
- Product detail pages load shared assets with `../assets/...`.
- Root pages load shared assets with `assets/...`.

## Contact Assets

Published QR assets live in:

`assets/contact/`

Current published files:

- `annie-whatsapp-cropped.jpg`
- `annie-wechat-cropped.jpg`
- `joe-whatsapp-cropped.jpg`
- `joe-wechat-cropped.png`

Original QR source files are kept outside the publish copy in:

`../contact/`

If replacing a QR code, crop the source first and update only the corresponding published file in `assets/contact/`.

## Shared JavaScript

- `assets/js/contact-qr-modal.js` - header WhatsApp / WeChat QR popover.

The header popover currently shows Annie's QR codes. The contact page shows Annie and Joe.

## Product Assets

- `assets/products/` - original selected product images grouped by part number.
- `assets/generated/` - AI-edited catalog images used by product cards and details.
- `assets/images/` - page-level images such as the CG260 promo and global route map.
- `assets/icons/` - header and contact icons.
- `assets/company/` - logo and company visual assets.

## Data Sources

Primary data files remain in the workspace `data/` folder:

- `data/selected-products.json` - selected website product data.
- `data/assets.json` and `data/assets.csv` - source asset inventory.
- `data/fitment_research.json` - part fitment and usage research.
- `data/image_edit_records.json` - generated image records.
- `data/exports/website-selected-products-table.csv` - selected product table export.

## Site Generation Scripts

Primary scripts live in `scripts/`:

- `generate_stitch_products_update.py` - regenerates product listing, detail, and category pages for this copy.
- `complete_remaining_products.py` - previous product selection completion helper.
- `apply_fitment_research.py` - applies fitment research fields.
- `record_latest_generated_image.py` - records generated image output.

Before running a generator, check whether it overwrites manually edited shared layout, scripts, or page-specific HTML.

## Current Structure Scan

- Top-level HTML files in current site: 4 root pages plus product pages.
- `products/`: 71 HTML files.
- `assets/contact/`: 4 published cropped QR files.
- `assets/js/`: 1 shared QR popover script.
- `assets/generated/`: generated product catalog images.
- `assets/products/`: grouped source product images.

## Safe Editing Notes

- Keep `stitch-migration/` as the baseline copy.
- Apply public-facing changes to `stitch-migration-products-update/`.
- Keep old site copies under `整理文件夹/` unless there is a confirmed cleanup request.
- Do not write to `\\10.0.0.254`.
- For cache busting after CSS changes, update the `styles.css?v=...` value in every HTML file.
