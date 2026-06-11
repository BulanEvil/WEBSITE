from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "selected-products.json"
PRODUCT_DIR = ROOT / "products"

EMAIL = "sales@evergold.sg"

CATEGORIES = [
    {
        "key": "construction-machinery",
        "name": "Engineering / Construction Machinery",
        "title": "Construction Machinery Parts",
        "summary": "CAT-compatible parts for excavators, loaders, graders, bulldozers, compactors, and heavy equipment fleets.",
    },
    {
        "key": "engine-parts",
        "name": "Engine Parts",
        "title": "Diesel Engine Parts",
        "summary": "Engine assemblies, injectors, pumps, filters, gaskets, cylinder heads, valves, and overhaul components.",
    },
    {
        "key": "mining-machine-parts",
        "name": "Mining Machine Parts",
        "title": "Mining Machine Parts",
        "summary": "Heavy-duty replacement parts for mining fleets, jobsite support, trucks, and high-load equipment.",
    },
    {
        "key": "generator-set-parts",
        "name": "Generator Set Parts",
        "title": "Generator Set Parts",
        "summary": "Diesel generator sets and replacement parts for industrial, commercial, and standby power needs.",
    },
]


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-").replace("--", "-")


def load_products() -> list[dict]:
    products = json.loads(DATA.read_text(encoding="utf-8"))
    for product in products:
        part = product.get("part_number") or "Unidentified"
        product["slug"] = slug(part)
        product["title"] = f"{part} CAT-Compatible Part"
        if product.get("category") == "Needs Review":
            product["display_category"] = "CAT-Compatible Parts"
        else:
            product["display_category"] = product.get("category")
    return products


def category_for_key(key: str) -> dict:
    return next(category for category in CATEGORIES if category["key"] == key)


def product_description(product: dict) -> str:
    part = product.get("part_number") or "This part"
    category = product.get("display_category") or "CAT-compatible parts"
    if product.get("cat_fitment_summary"):
        fitment = product["cat_fitment_summary"]
    else:
        fitment = "Compatibility is confirmed by part number, equipment model, engine model, and serial-number information before quotation."
    return (
        f"Evergold supplies {part} as a {category.lower()} item for CAT-compatible sourcing. "
        f"{fitment}"
    )


def mailto(subject: str, body: str = "") -> str:
    import urllib.parse

    url = f"mailto:{EMAIL}?subject={urllib.parse.quote(subject)}"
    if body:
        url += f"&body={urllib.parse.quote(body)}"
    return url


def layout(title: str, description: str, active: str, body: str) -> str:
    nav = [
        ("Home", "index.html", "home"),
        ("Products", "products.html", "products"),
        ("About", "about.html", "about"),
        ("Contact", "contact.html", "contact"),
    ]
    nav_html = "\n".join(
        f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>' for label, href, key in nav
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}" />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <header class="site-header">
      <a class="brand" href="index.html" aria-label="Evergold home">
        <img src="assets/company/evergold-logo.png" alt="" />
        <span>Evergold</span>
      </a>
      <nav class="nav" aria-label="Primary navigation">
        {nav_html}
      </nav>
      <a class="header-cta" href="{mailto('RFQ from Evergold website')}">Email Sales</a>
    </header>
    {body}
    <footer class="site-footer">
      <div>
        <strong>Evergold</strong>
        <span>CAT-compatible industrial parts supply for global buyers.</span>
      </div>
      <div class="footer-links">
        <a href="products.html">Products</a>
        <a href="about.html">About</a>
        <a href="contact.html">Contact</a>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
      </div>
      <p class="legal-note">CATERPILLAR, CAT, and related marks are trademarks of their respective owners. Evergold supplies compatible replacement parts and does not imply official affiliation unless expressly documented.</p>
    </footer>
  </body>
</html>
"""


def product_card(product: dict) -> str:
    part = product.get("part_number") or "Part"
    image = product.get("web_asset_path") or "assets/images/industrial-parts-warehouse.png"
    category = product.get("display_category") or "CAT-Compatible Parts"
    return f"""
<article class="product-card">
  <a class="product-image-link" href="products/{esc(product['slug'])}.html">
    <img src="{esc(image)}" alt="{esc(part)} CAT-compatible industrial part" loading="lazy" />
  </a>
  <div class="product-card-body">
    <span>{esc(category)}</span>
    <h3><a href="products/{esc(product['slug'])}.html">{esc(part)}</a></h3>
    <p>{esc(product_description(product))}</p>
  </div>
</article>"""


def category_links() -> str:
    items = "\n".join(
        f"""
<a class="category-tile" href="products/{category['key']}.html">
  <span>{esc(category['name'])}</span>
  <strong>{esc(category['title'])}</strong>
  <p>{esc(category['summary'])}</p>
</a>"""
        for category in CATEGORIES
    )
    return f'<div class="category-grid">{items}</div>'


def write_index(products: list[dict]) -> None:
    featured = "\n".join(product_card(product) for product in products[:6])
    body = f"""
<main>
  <section class="hero hero-home">
    <img class="hero-image" src="assets/images/industrial-parts-warehouse.png" alt="Industrial warehouse with diesel engines, generator sets, and machinery parts" />
    <div class="hero-overlay"></div>
    <div class="hero-content">
      <p class="market-line">CATERPILLAR / CAT-compatible parts supply</p>
      <h1>CAT-compatible parts for heavy equipment, engines, mining fleets, and power systems.</h1>
      <p class="lead">Evergold helps global distributors, repair workshops, procurement companies, and industrial end users source practical replacement parts by part number, model, and application.</p>
      <div class="hero-actions">
        <a class="button primary" href="{mailto('RFQ for CAT-compatible parts')}">Send RFQ</a>
        <a class="button secondary" href="products.html">View products</a>
      </div>
    </div>
  </section>
  <section class="section">
    <div class="section-intro">
      <h2>Product range built around CAT-compatible sourcing.</h2>
      <p>Browse the main supply categories or send a part list directly to sales. Fitment is checked by part number and machine or engine details before quotation.</p>
    </div>
    {category_links()}
  </section>
  <section class="section muted-section">
    <div class="section-intro">
      <h2>Featured part-number products</h2>
      <p>Selected product entries are organized by visible part number and image quality. Send the part number, quantity, and equipment details for confirmation before quotation.</p>
    </div>
    <div class="product-grid">{featured}</div>
  </section>
  <section class="section rfq-panel">
    <div>
      <h2>Send your RFQ with part numbers, quantities, and destination country.</h2>
      <p>Photos, equipment models, engine models, and serial-number references help confirm compatibility before quotation.</p>
    </div>
    <a class="button primary large" href="{mailto('RFQ from Evergold website', 'Hello Evergold,\\n\\nPlease quote the following CAT-compatible parts:\\n\\nCompany:\\nCountry:\\nPart numbers / models:\\nQuantities:\\nAdditional notes:\\n')}">Email {EMAIL}</a>
  </section>
</main>"""
    (ROOT / "index.html").write_text(
        layout(
            "Evergold | CAT-Compatible Parts for Heavy Equipment and Engines",
            "Evergold supplies CATERPILLAR / CAT-compatible construction machinery parts, diesel engine parts, mining equipment parts, and generator set parts.",
            "home",
            body,
        ),
        encoding="utf-8",
    )


def write_products(products: list[dict]) -> None:
    cards = "\n".join(product_card(product) for product in products)
    body = f"""
<main>
  <section class="page-hero">
    <p class="market-line">Product range</p>
    <h1>CAT-compatible parts organized for export RFQ.</h1>
    <p class="lead">Browse selected part-number products and main supply categories. Final compatibility is confirmed before quotation.</p>
  </section>
  <section class="section">
    {category_links()}
  </section>
  <section class="section">
    <div class="section-intro">
      <h2>Selected part-number products</h2>
      <p>Use the product pages as a starting point for RFQ. Include quantity, destination country, and machine or engine information when available.</p>
    </div>
    <div class="product-grid">{cards}</div>
  </section>
</main>"""
    (ROOT / "products.html").write_text(
        layout(
            "Products | Evergold CAT-Compatible Industrial Parts",
            "Browse Evergold CAT-compatible construction machinery parts, diesel engine parts, mining equipment parts, and generator set parts.",
            "products",
            body,
        ),
        encoding="utf-8",
    )


def write_category_pages(products: list[dict]) -> None:
    PRODUCT_DIR.mkdir(parents=True, exist_ok=True)
    for category in CATEGORIES:
        if category["name"] == "Engineering / Construction Machinery":
            filtered = [p for p in products if p.get("category") == category["name"] or p.get("category") == "Needs Review"]
        else:
            filtered = [p for p in products if p.get("category") == category["name"]]
        if not filtered:
            filtered = products[:8]
        cards = "\n".join(product_card(product) for product in filtered[:18])
        body = f"""
<main>
  <section class="page-hero compact">
    <p class="market-line">CAT-compatible supply category</p>
    <h1>{esc(category['title'])}</h1>
    <p class="lead">{esc(category['summary'])}</p>
  </section>
  <section class="section">
    <div class="product-grid">{cards}</div>
  </section>
</main>"""
        (PRODUCT_DIR / f"{category['key']}.html").write_text(
            layout(
                f"{category['title']} | Evergold",
                category["summary"],
                "products",
                body,
            ).replace('href="styles.css"', 'href="../styles.css"')
            .replace('href="index.html"', 'href="../index.html"')
            .replace('href="products.html"', 'href="../products.html"')
            .replace('href="about.html"', 'href="../about.html"')
            .replace('href="contact.html"', 'href="../contact.html"')
            .replace('src="assets/', 'src="../assets/')
            .replace('href="products/', 'href="'),
            encoding="utf-8",
        )


def write_product_detail_pages(products: list[dict]) -> None:
    PRODUCT_DIR.mkdir(parents=True, exist_ok=True)
    for product in products:
        part = product.get("part_number") or "Part"
        image = product.get("web_asset_path") or "assets/images/industrial-parts-warehouse.png"
        category = product.get("display_category") or "CAT-Compatible Parts"
        body = f"""
<main>
  <section class="product-detail">
    <div class="detail-image">
      <img src="../{esc(image)}" alt="{esc(part)} CAT-compatible industrial part" />
    </div>
    <div class="detail-copy">
      <p class="market-line">{esc(category)}</p>
      <h1>{esc(part)}</h1>
      <p class="lead">{esc(product_description(product))}</p>
      <dl class="spec-list">
        <div><dt>Part number</dt><dd>{esc(part)}</dd></div>
        <div><dt>Category</dt><dd>{esc(category)}</dd></div>
        <div><dt>Fitment</dt><dd>Confirm before quotation</dd></div>
        <div><dt>Image quality</dt><dd>{esc(product.get('image_quality'))}</dd></div>
      </dl>
      <div class="notice">
        <strong>Fitment note</strong>
        <p>Confirm compatibility by part number, equipment model, engine model, and serial-number information before ordering.</p>
      </div>
      <a class="button primary large" href="{mailto('RFQ for ' + part, 'Hello Evergold,\\n\\nPlease quote ' + part + '.\\n\\nCompany:\\nCountry:\\nQuantity:\\nMachine / engine model:\\nAdditional notes:\\n')}">Request quote for {esc(part)}</a>
    </div>
  </section>
</main>"""
        (PRODUCT_DIR / f"{product['slug']}.html").write_text(
            layout(
                f"{part} | Evergold CAT-Compatible Part",
                f"Request a quote for {part}, a CAT-compatible industrial part supplied by Evergold.",
                "products",
                body,
            ).replace('href="styles.css"', 'href="../styles.css"')
            .replace('href="index.html"', 'href="../index.html"')
            .replace('href="products.html"', 'href="../products.html"')
            .replace('href="about.html"', 'href="../about.html"')
            .replace('href="contact.html"', 'href="../contact.html"')
            .replace('src="assets/', 'src="../assets/'),
            encoding="utf-8",
        )


def write_about() -> None:
    body = """
<main>
  <section class="page-hero compact">
    <p class="market-line">About Evergold</p>
    <h1>International supply support for CAT-compatible industrial parts.</h1>
    <p class="lead">Evergold focuses on practical sourcing for construction machinery parts, diesel engine parts, mining equipment parts, and generator set parts for global B2B buyers.</p>
  </section>
  <section class="section split-section">
    <div>
      <h2>Built for overseas distributors, repair workshops, procurement teams, and industrial operators.</h2>
    </div>
    <div class="text-stack">
      <p>The website is structured for clear international RFQ communication. Product images, part numbers, and contact paths are organized to help buyers confirm requirements quickly.</p>
      <p>Company registration and trust documents can be shared with buyers during RFQ review.</p>
      <a class="button secondary dark" href="assets/company/trustbar-registration.pdf">View registration document</a>
    </div>
  </section>
</main>"""
    (ROOT / "about.html").write_text(
        layout(
            "About Evergold | CAT-Compatible Parts Supply",
            "Learn about Evergold, a supplier of CAT-compatible industrial parts for global B2B buyers.",
            "about",
            body,
        ),
        encoding="utf-8",
    )


def write_contact() -> None:
    body = f"""
<main>
  <section class="page-hero compact">
    <p class="market-line">Request a quote</p>
    <h1>Send part numbers, quantities, and application details.</h1>
    <p class="lead">The fastest RFQ includes part numbers, equipment or engine models, photos if available, quantity, delivery country, and target lead time.</p>
  </section>
  <section class="section contact-grid">
    <div class="contact-card">
      <span>Email</span>
      <h2>{EMAIL}</h2>
      <p>Use email for part-number lists, photos, and attachment-based RFQs.</p>
      <a class="button primary" href="{mailto('RFQ from Evergold website')}">Email Sales</a>
    </div>
    <div class="contact-card muted">
      <span>RFQ checklist</span>
      <ul>
        <li>Company and country</li>
        <li>Part numbers and quantities</li>
        <li>Machine, engine, or generator model</li>
        <li>Photos or reference files</li>
        <li>Target delivery country</li>
      </ul>
    </div>
  </section>
</main>"""
    (ROOT / "contact.html").write_text(
        layout(
            "Contact Evergold | RFQ for CAT-Compatible Parts",
            "Contact Evergold sales for CAT-compatible construction machinery parts, diesel engine parts, mining equipment parts, and generator set parts.",
            "contact",
            body,
        ),
        encoding="utf-8",
    )


def write_styles() -> None:
    css = r""":root {
  --bg: #f5f7f8;
  --surface: #ffffff;
  --ink: #172026;
  --muted: #52616b;
  --line: #d8e2e7;
  --accent: #176b6f;
  --accent-strong: #0d4649;
  --trade-warm: #b8793a;
  --warm-soft: #f4ebe1;
  --cool-soft: #eaf2f3;
  --dark: #10181c;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: Arial, Helvetica, sans-serif;
  line-height: 1.55;
}
a { color: inherit; }
img { max-width: 100%; display: block; }

.site-header,
main,
.site-footer {
  width: min(1180px, calc(100% - 36px));
  margin: 0 auto;
}

.site-header {
  min-height: 76px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 24px;
}

.brand,
.nav,
.hero-actions,
.site-footer,
.footer-links {
  display: flex;
  align-items: center;
}

.brand {
  gap: 12px;
  font-weight: 800;
  text-decoration: none;
}
.brand img {
  width: 42px;
  height: 42px;
  object-fit: contain;
  border-radius: 8px;
}
.nav {
  justify-content: center;
  gap: 24px;
  color: var(--muted);
  font-size: 14px;
}
.nav a,
.header-cta,
.button,
.footer-links a,
.product-card a,
.category-tile {
  text-decoration: none;
}
.nav a.active,
.nav a:hover,
.footer-links a:hover {
  color: var(--accent-strong);
}
.header-cta {
  min-height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--accent-strong);
  border-radius: 7px;
  padding: 0 14px;
  color: var(--accent-strong);
  font-size: 14px;
  font-weight: 700;
}

.hero {
  position: relative;
  left: 50%;
  width: 100vw;
  min-height: min(760px, calc(100vh - 76px));
  margin-left: -50vw;
  overflow: hidden;
  display: grid;
  align-items: end;
  padding: clamp(120px, 18vh, 190px) max(18px, calc((100vw - 1180px) / 2)) 70px;
  background: var(--dark);
}
.hero-image,
.hero-overlay { position: absolute; inset: 0; }
.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.hero-overlay {
  background:
    linear-gradient(90deg, rgba(9, 16, 19, 0.88), rgba(9, 16, 19, 0.58) 46%, rgba(9, 16, 19, 0.12)),
    linear-gradient(0deg, rgba(9, 16, 19, 0.82), transparent 46%);
}
.hero-content {
  position: relative;
  z-index: 1;
  max-width: 880px;
  color: #fff;
}
.market-line {
  max-width: 760px;
  margin: 0 0 18px;
  color: #e7c597;
  font-size: clamp(14px, 2vw, 18px);
  font-weight: 800;
}
h1, h2, h3, p { margin-top: 0; }
h1 {
  margin-bottom: 24px;
  font-size: clamp(46px, 7.6vw, 88px);
  line-height: 0.99;
  letter-spacing: -0.024em;
  text-wrap: balance;
}
h2 {
  margin-bottom: 16px;
  font-size: clamp(32px, 4.5vw, 54px);
  line-height: 1.05;
  letter-spacing: -0.018em;
  text-wrap: balance;
}
h3 {
  margin-bottom: 12px;
  font-size: 21px;
  line-height: 1.18;
}
.lead {
  max-width: 68ch;
  color: rgba(255, 255, 255, 0.86);
  font-size: clamp(18px, 2vw, 21px);
}
.page-hero .lead { color: var(--muted); }
.hero-actions {
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 32px;
}
.button {
  min-height: 46px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--accent-strong);
  border-radius: 7px;
  padding: 0 18px;
  font-weight: 800;
}
.button.primary {
  background: var(--accent-strong);
  color: #fff;
}
.button.secondary {
  border-color: rgba(255, 255, 255, 0.72);
  color: #fff;
}
.button.secondary.dark {
  border-color: var(--accent-strong);
  color: var(--accent-strong);
}
.button.large {
  min-height: 54px;
  padding: 0 22px;
}

.page-hero {
  padding: clamp(70px, 11vw, 130px) 0 56px;
}
.page-hero.compact {
  max-width: 940px;
}
.page-hero h1 {
  color: var(--ink);
}
.section {
  padding: clamp(64px, 9vw, 108px) 0;
  border-top: 1px solid var(--line);
}
.muted-section {
  background: transparent;
}
.section-intro {
  display: grid;
  grid-template-columns: minmax(0, 0.82fr) minmax(280px, 0.48fr);
  gap: clamp(28px, 6vw, 72px);
  align-items: end;
  margin-bottom: 34px;
}
.section-intro p,
.rfq-panel p,
.rfq-section p,
.capability-list p,
.product-card p,
.category-tile p,
.text-stack p,
.contact-card p,
.legal-note {
  color: var(--muted);
}
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 14px;
}
.category-tile {
  min-height: 230px;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--line);
  border-radius: 9px;
  padding: 24px;
  background: var(--surface);
}
.category-tile span {
  color: var(--trade-warm);
  font-size: 13px;
  font-weight: 800;
}
.category-tile strong {
  margin-top: auto;
  margin-bottom: 10px;
  color: var(--ink);
  font-size: 22px;
  line-height: 1.15;
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
.product-card {
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--surface);
}
.product-image-link {
  display: block;
  aspect-ratio: 4 / 3;
  background: #e9eef1;
}
.product-image-link img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 14px;
}
.product-card-body {
  padding: 20px;
}
.product-card-body span {
  color: var(--trade-warm);
  font-size: 12px;
  font-weight: 800;
}
.product-card h3 {
  margin-top: 14px;
}
.capability-section,
.split-section,
.rfq-panel,
.rfq-section,
.contact-grid,
.product-detail {
  display: grid;
  grid-template-columns: minmax(0, 0.78fr) minmax(320px, 0.58fr);
  gap: clamp(32px, 7vw, 82px);
  align-items: start;
}
.capability-list article {
  border-top: 1px solid var(--line);
  padding: 22px 0;
}
.capability-list h3 {
  color: var(--accent-strong);
}
.rfq-panel,
.rfq-section {
  align-items: center;
  border-bottom: 1px solid var(--line);
}
.detail-image {
  border: 1px solid var(--line);
  border-radius: 10px;
  background: #edf2f4;
  padding: 20px;
}
.detail-image img {
  width: 100%;
  max-height: 620px;
  object-fit: contain;
}
.detail-copy {
  position: sticky;
  top: 24px;
}
.spec-list {
  display: grid;
  gap: 0;
  margin: 28px 0;
}
.spec-list div {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 18px;
  border-top: 1px solid var(--line);
  padding: 14px 0;
}
.spec-list dt {
  color: var(--muted);
  font-weight: 700;
}
.spec-list dd {
  margin: 0;
  font-weight: 800;
}
.notice,
.contact-card {
  border: 1px solid var(--line);
  border-radius: 9px;
  background: var(--surface);
  padding: 24px;
}
.contact-card.muted {
  background: var(--cool-soft);
}
.contact-card span {
  color: var(--trade-warm);
  font-size: 13px;
  font-weight: 800;
}
.contact-card ul {
  margin: 18px 0 0;
  padding-left: 20px;
  color: var(--muted);
}
.text-stack {
  display: grid;
  gap: 14px;
}
.site-footer {
  min-height: 180px;
  align-items: start;
  justify-content: space-between;
  gap: 24px;
  border-top: 1px solid var(--line);
  padding: 34px 0;
  color: var(--muted);
  font-size: 14px;
}
.site-footer div:first-child {
  display: grid;
  gap: 8px;
}
.site-footer strong {
  color: var(--ink);
  font-size: 18px;
}
.footer-links {
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 16px;
}
.legal-note {
  max-width: 1180px;
  grid-column: 1 / -1;
  margin: 0;
  font-size: 12px;
}

@media (max-width: 900px) {
  .site-header { grid-template-columns: 1fr auto; }
  .nav { display: none; }
  .section-intro,
  .capability-section,
  .split-section,
  .rfq-panel,
  .rfq-section,
  .contact-grid,
  .product-detail {
    grid-template-columns: 1fr;
  }
  .hero { min-height: 680px; }
  .detail-copy { position: static; }
}
@media (max-width: 620px) {
  .site-header,
  main,
  .site-footer {
    width: min(100% - 28px, 1180px);
  }
  .site-header {
    min-height: auto;
    padding: 18px 0;
    gap: 12px;
  }
  .header-cta { display: none; }
  .hero {
    min-height: 640px;
    padding-top: 92px;
    padding-bottom: 48px;
  }
  .hero-overlay {
    background:
      linear-gradient(90deg, rgba(9, 16, 19, 0.9), rgba(9, 16, 19, 0.62)),
      linear-gradient(0deg, rgba(9, 16, 19, 0.82), transparent 50%);
  }
  h1 { font-size: clamp(42px, 13vw, 62px); }
  .hero-actions,
  .site-footer,
  .footer-links {
    display: grid;
    grid-template-columns: 1fr;
  }
  .button { width: 100%; }
  .section { padding: 58px 0; }
  .spec-list div {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; }
}
"""
    (ROOT / "styles.css").write_text(css, encoding="utf-8")


def main() -> None:
    products = load_products()
    write_index(products)
    write_products(products)
    write_category_pages(products)
    write_product_detail_pages(products)
    write_about()
    write_contact()
    write_styles()
    print(f"Generated site pages for {len(products)} selected products.")


if __name__ == "__main__":
    main()
