from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "stitch-migration-products-update"
SELECTED = ROOT / "data" / "selected-products.json"
IMAGE_RECORDS = ROOT / "data" / "image_edit_records.json"


CATEGORIES = [
    {
        "key": "construction-machinery",
        "name": "Engineering / Construction Machinery",
        "eyebrow": "Engineering / Construction Machinery",
        "title": "Construction Machinery Parts",
        "summary": "Hydraulic, drivetrain, cooling, mirror, and service parts for jobsite equipment and repair workshops.",
        "tile_class": "category-construction",
    },
    {
        "key": "engine-parts",
        "name": "Engine Parts",
        "eyebrow": "Engine Parts",
        "title": "Diesel Engine Parts",
        "summary": "Engine overhaul, filtration, cooling, valve-train, turbocharger, ignition, and service parts for diesel and gas engines.",
        "tile_class": "category-engine",
    },
    {
        "key": "engine-generator-sets",
        "name": "Engine Assembly / Generator Sets",
        "eyebrow": "Engine Assembly / Generator Sets",
        "title": "Engine Assembly / Generator Sets",
        "summary": "Complete diesel and gas engine assemblies, generator sets, and packaged power units for industrial and power-system applications.",
        "tile_class": "category-engine-generator",
    },
    {
        "key": "mining-machine-parts",
        "name": "Mining Machine Parts",
        "eyebrow": "Mining Machine Parts",
        "title": "Mining Machine Parts",
        "summary": "Heavy-duty replacement parts for mining fleets, trucks, and high-load equipment.",
        "tile_class": "category-mining",
    },
    {
        "key": "generator-set-parts",
        "name": "Generator Set Parts",
        "eyebrow": "Generator Set Parts",
        "title": "Generator Set Parts",
        "summary": "Controllers, radiators, cooling pieces, and supporting replacement parts for generator-set service.",
        "tile_class": "category-generator",
    },
]


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-").replace("--", "-")


def mailto(subject: str, body: str = "") -> str:
    from urllib.parse import quote

    href = f"mailto:sales@evergold.sg?subject={quote(subject)}"
    if body:
        href += f"&body={quote(body)}"
    return href


def load_image_records() -> dict[str, dict]:
    if not IMAGE_RECORDS.exists():
        return {}
    records = json.loads(IMAGE_RECORDS.read_text(encoding="utf-8"))
    usable: dict[str, dict] = {}
    for record in records:
        if record.get("status") != "candidate_generated":
            continue
        part = record.get("part_number")
        generated_path = record.get("generated_path")
        if part and generated_path and (ROOT / generated_path).exists():
            usable[part] = record
    return usable


def product_description(product: dict) -> str:
    return (
        product.get("customer_usage")
        or product.get("product_description")
        or product.get("cat_fitment_summary")
        or product.get("visual_description")
        or "Selected part-number item for Evergold export RFQ support."
    )


def prepare_products() -> list[dict]:
    image_records = load_image_records()
    products = json.loads(SELECTED.read_text(encoding="utf-8"))
    prepared: list[dict] = []
    for product in products:
        product = dict(product)
        part = product.get("part_number") or "Part"
        product["slug"] = slug(part)
        record = image_records.get(part)
        generated = record.get("generated_path") if record else product.get("generated_path")
        image = generated or product.get("web_asset_path") or "assets/images/industrial-parts-warehouse.png"
        product["display_image_path"] = image
        product["display_category"] = product.get("category") or "CATERPILLAR Genuine Parts"
        prepared.append(product)
    return prepared


def header(active: str, prefix: str = "") -> str:
    links = [
        ("Home", "index.html"),
        ("Products", "products.html"),
        ("About", "about.html"),
        ("Contact", "contact.html"),
    ]
    nav = "\n".join(
        f'<a class="{"active" if label == active else ""}" href="{prefix}{href}">{label}</a>'
        for label, href in links
    )
    return f"""<header class="site-header">
      <a class="brand" href="{prefix}index.html" aria-label="Evergold home">
        <img src="{prefix}assets/company/evergold-logo.png" alt="" />
        <span class="brand-copy"><strong>Evergold</strong><small>EVERGOLD TECHNOLOGY PTE. LTD.</small></span>
      </a>
      <nav class="nav" aria-label="Primary navigation">
        {nav}
      </nav>
      <div class="header-quick-actions" aria-label="Quick contact">
        <a class="header-icon-button whatsapp" data-qr-type="whatsapp" href="{prefix}contact.html" aria-label="WhatsApp contact" title="WhatsApp">
          <img src="{prefix}assets/icons/whatsapp.svg" alt="" loading="lazy" />
        </a>
        <a class="header-icon-button wechat" data-qr-type="wechat" href="{prefix}contact.html" aria-label="WeChat contact" title="WeChat">
          <img src="{prefix}assets/icons/wechat.svg" alt="" loading="lazy" />
        </a>
        <a class="header-icon-button email" href="{mailto('RFQ from Evergold website')}" aria-label="Email sales" title="Email sales">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16v12H4V6Zm1.7 1.8 6.3 5 6.3-5H5.7Zm12.6 8.4V9.9l-6.3 5-6.3-5v6.3h12.6Z"/></svg>
        </a>
      </div>
      <a class="header-cta" href="{mailto('RFQ from Evergold website')}">Request for Quote</a>
    </header>"""


def footer(prefix: str = "") -> str:
    return f"""<footer class="site-footer">
      <div>
        <strong>EVERGOLD TECHNOLOGY PTE. LTD.</strong>
        <span>CATERPILLAR genuine industrial parts supply for global buyers.</span>
      </div>
      <div class="footer-links">
        <a href="{prefix}products.html">Products</a>
        <a href="{prefix}about.html">About</a>
        <a href="{prefix}contact.html">Contact</a>
        <a href="mailto:sales@evergold.sg">sales@evergold.sg</a>
      </div>
      <p class="legal-note">CATERPILLAR, CAT, and related marks are trademarks of their respective owners. Evergold supplies genuine CATERPILLAR parts through sourcing and trading channels and does not imply official dealership, authorization, or affiliation unless expressly documented.</p>
    </footer>"""


def page(title: str, description: str, body: str, active: str = "Products", prefix: str = "", body_class: str = "") -> str:
    cls = f' class="{body_class}"' if body_class else ""
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}" />
    <link rel="stylesheet" href="{prefix}styles.css?v=copy-audit-1" />
  </head>
  <body{cls}>
    {header(active, prefix)}
    {body}
    {footer(prefix)}
    <script src="{prefix}assets/js/contact-qr-modal.js?v=qr-type-1" defer></script>
  </body>
</html>
"""


def product_card(product: dict, prefix: str = "") -> str:
    part = product.get("part_number") or "Part"
    image = product["display_image_path"]
    return f"""<article class="product-card">
  <a class="product-image-link" href="{prefix}products/{esc(product['slug'])}.html">
    <img src="{prefix}{esc(image)}" alt="{esc(part)} CATERPILLAR genuine industrial part" loading="lazy" />
  </a>
  <div class="product-card-body">
    <span>{esc(product['display_category'])}</span>
    <h3><a href="{prefix}products/{esc(product['slug'])}.html">{esc(part)}</a></h3>
    <p>{esc(product_description(product))}</p>
  </div>
</article>"""


def category_tile(category: dict) -> str:
    return f"""<a class="category-tile {esc(category['tile_class'])} rb-spotlight rb-reveal" href="products/{esc(category['key'])}.html">
  <span>{esc(category['eyebrow'])}</span>
  <strong>{esc(category['title'])}</strong>
</a>"""


def products_script() -> str:
    return """<script>
      const params = new URLSearchParams(window.location.search);
      const query = (params.get("q") || "").trim().toLowerCase();
      const cards = Array.from(document.querySelectorAll(".catalog-product-grid .product-card"));
      const note = document.querySelector(".catalog-query-note");
      const empty = document.querySelector(".catalog-empty");
      const searchAliases = {
        "injector": ["injector", "injectors", "injection", "fuel", "nozzle", "engine parts"],
        "injectors": ["injector", "injectors", "injection", "fuel", "nozzle", "engine parts"],
        "spark plug": ["spark plug", "spark plugs", "ignition", "plug"],
        "spark plugs": ["spark plug", "spark plugs", "ignition", "plug"],
        "generator": ["generator", "genset", "power unit", "engine assembly"],
        "engine assembly": ["engine assembly", "generator sets", "packaged power"],
        "c15": ["c15"],
        "c32": ["c32"],
        "mwm": ["mwm", "tcg"],
        "g3606": ["g3606", "g36"]
      };

      const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (!reduceMotion) {
        document.querySelectorAll(".rb-spotlight").forEach((card) => {
          card.addEventListener("pointermove", (event) => {
            const rect = card.getBoundingClientRect();
            card.style.setProperty("--mx", `${event.clientX - rect.left}px`);
            card.style.setProperty("--my", `${event.clientY - rect.top}px`);
          });
        });

        const revealObserver = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              revealObserver.unobserve(entry.target);
            }
          });
        }, { threshold: 0.16 });

        document.querySelectorAll(".rb-reveal, .catalog-product-grid .product-card").forEach((item) => {
          revealObserver.observe(item);
        });
      }

      if (query) {
        const terms = searchAliases[query] || [query];
        let visibleCount = 0;
        cards.forEach((card) => {
          const searchableText = card.textContent.toLowerCase();
          const isVisible = terms.some((term) => searchableText.includes(term));
          card.hidden = !isVisible;
          if (isVisible) visibleCount += 1;
        });
        note.hidden = false;
        note.textContent = `Showing results for "${params.get("q")}".`;
        empty.hidden = visibleCount !== 0;
      }
    </script>"""


def write_products_page(products: list[dict]) -> None:
    cards = "\n\n".join(product_card(product) for product in products)
    tiles = "\n\n".join(category_tile(category) for category in CATEGORIES)
    body = f"""
<main>
  <section class="page-hero products-hero rb-spotlight rb-reveal">
    <div class="container products-hero-inner">
      <div class="products-hero-copy">
        <p class="market-line">Product range</p>
        <h1>CATERPILLAR genuine parts organized for export RFQ.</h1>
      </div>
      <p class="lead">Browse 66 selected part-number products across five supply categories, with clear application details for export RFQ preparation.</p>
    </div>
  </section>
  <section class="category-strip-section" aria-label="Product categories">
    <div class="category-grid">
{tiles}
    </div>
  </section>
  <section class="section">
    <div class="section-intro">
      <h2>Selected part-number products</h2>
      <p>Use the product pages to prepare RFQs with quantity, destination country, and machine or engine information.</p>
    </div>
    <p class="catalog-query-note" hidden></p>
    <div class="product-grid catalog-product-grid">
{cards}
    </div>
    <p class="catalog-empty" hidden>No matching products in this selected set. Send the part number to sales@evergold.sg for RFQ support.</p>
  </section>
</main>
{products_script()}"""
    (TARGET / "products.html").write_text(
        page(
            "Products | Evergold CATERPILLAR Genuine Industrial Parts",
            "Browse 66 Evergold CATERPILLAR genuine construction machinery parts, diesel engine parts, engine-generator assemblies, mining equipment parts, and generator set parts.",
            body,
            body_class="react-bits-enhanced products-page",
        ),
        encoding="utf-8",
    )


def write_category_pages(products: list[dict]) -> None:
    out = TARGET / "products"
    out.mkdir(exist_ok=True)
    for category in CATEGORIES:
        category_products = [product for product in products if product.get("category") == category["name"]]
        cards = "\n\n".join(product_card(product, prefix="../").replace('href="../products/', 'href="') for product in category_products)
        body = f"""
<main>
  <section class="page-hero compact category-hero">
    <div>
      <p class="market-line">CATERPILLAR genuine supply category</p>
      <h1>{esc(category['title'])}</h1>
      <p class="lead">{esc(category['summary'])}</p>
    </div>
    <a class="button primary large" href="../products.html">View all products</a>
  </section>
  <section class="section">
    <div class="product-grid">
{cards}
    </div>
  </section>
</main>"""
        (out / f"{category['key']}.html").write_text(
            page(f"{category['title']} | Evergold", category["summary"], body, prefix="../"),
            encoding="utf-8",
        )


def write_product_detail_pages(products: list[dict]) -> None:
    out = TARGET / "products"
    out.mkdir(exist_ok=True)
    for product in products:
        part = product.get("part_number") or "Part"
        image = product["display_image_path"]
        category = product["display_category"]
        application = product.get("customer_usage") or product_description(product)
        body = f"""
<main>
  <section class="product-detail">
    <div class="detail-image">
      <img src="../{esc(image)}" alt="{esc(part)} CATERPILLAR genuine industrial part" />
    </div>
    <div class="detail-copy">
      <p class="market-line">{esc(category)}</p>
      <h1>{esc(part)}</h1>
      <p class="lead">{esc(product_description(product))}</p>
      <dl class="spec-list">
        <div><dt>Part number</dt><dd>{esc(part)}</dd></div>
        <div><dt>Category</dt><dd>{esc(category)}</dd></div>
        <div><dt>Application</dt><dd>{esc(category)}</dd></div>
      </dl>
      <div class="notice">
        <strong>Application / Usage</strong>
        <p>{esc(application)}</p>
      </div>
      <a class="button primary large" href="{mailto(f'RFQ for {part}', f'Hello Evergold,\\n\\nPlease quote {part}.\\n\\nCompany:\\nCountry:\\nQuantity:\\nMachine / engine model:\\nAdditional notes:\\n')}">Request quote for {esc(part)}</a>
    </div>
  </section>
</main>"""
        (out / f"{product['slug']}.html").write_text(
            page(
                f"{part} | Evergold CATERPILLAR Genuine Part",
                f"Request a quote for {part}, a CATERPILLAR genuine industrial part supplied by Evergold.",
                body,
                prefix="../",
            ),
            encoding="utf-8",
        )


def sync_assets() -> None:
    generated_src = ROOT / "assets" / "generated"
    generated_dst = TARGET / "assets" / "generated"
    generated_dst.mkdir(parents=True, exist_ok=True)
    if generated_src.exists():
        for image in generated_src.glob("*"):
            if image.is_file():
                shutil.copy2(image, generated_dst / image.name)


def main() -> None:
    if not TARGET.exists():
        raise RuntimeError(f"Missing target copy: {TARGET}")
    sync_assets()
    products = prepare_products()
    write_products_page(products)
    write_category_pages(products)
    write_product_detail_pages(products)
    print(f"Updated {TARGET.name}: {len(products)} products, {len(CATEGORIES)} category pages")


if __name__ == "__main__":
    main()
