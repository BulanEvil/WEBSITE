from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "stitch-migration-products-update"
RU = SITE / "ru"
PRODUCTS_JSON = ROOT / "data" / "selected-products.json"


CATEGORIES = [
    {
        "key": "engine-parts",
        "name_en": "Engine Parts",
        "name": "Детали дизельных двигателей",
        "title": "Детали дизельных двигателей",
        "summary": "Детали для ремонта двигателей, фильтрации, охлаждения, клапанного механизма, турбокомпрессоров и сервисного обслуживания.",
        "tile_class": "category-engine",
    },
    {
        "key": "construction-machinery",
        "name_en": "Engineering / Construction Machinery",
        "name": "Детали строительной техники",
        "title": "Детали строительной техники",
        "summary": "Гидравлические, трансмиссионные, кабинные, зеркальные и управляющие компоненты для тяжелой техники.",
        "tile_class": "category-construction",
    },
    {
        "key": "mining-machine-parts",
        "name_en": "Mining Machine Parts",
        "name": "Детали горной техники",
        "title": "Детали горной техники",
        "summary": "Усиленные запасные части для карьерных самосвалов, бульдозеров и тяжелых режимов работы.",
        "tile_class": "category-mining",
    },
    {
        "key": "generator-set-parts",
        "name_en": "Generator Set Parts",
        "name": "Детали генераторных установок",
        "title": "Детали генераторных установок",
        "summary": "Контроллеры, радиаторы, элементы охлаждения и сервисные компоненты для генераторных установок.",
        "tile_class": "category-generator",
    },
    {
        "key": "engine-generator-sets",
        "name_en": "Engine Assembly / Generator Sets",
        "name": "Двигатели в сборе / генераторные установки",
        "title": "Двигатели в сборе / генераторные установки",
        "summary": "Дизельные и газовые двигатели в сборе, генераторные установки и комплектные энергетические блоки для промышленных объектов.",
        "tile_class": "category-engine-generator",
    },
]


CATEGORY_BY_EN = {category["name_en"]: category for category in CATEGORIES}
CATEGORY_BY_KEY = {category["key"]: category for category in CATEGORIES}


PRODUCT_USAGE_RU = {
    "3412E": "Дизельный двигатель 3412E в сборе для генераторных установок, промышленных энергетических объектов и замены двигателя.",
    "C15": "Дизельная платформа Caterpillar C15 для тяжелых автомобилей, техники и промышленных двигателей.",
    "C32B": "Высокомощная дизельная платформа Caterpillar C32B V12 для морских, тяжелых и промышленных применений.",
    "107-7330": "Коромысло двигателя или компонент клапанного механизма.",
    "175-7852": "Желтый гидравлический клапан или блок управления.",
    "183-2264": "Обработанная металлическая ступица, фланец или вращающийся компонент трансмиссии.",
    "1R1808": "Фильтр CAT или комплект фильтрующих элементов для сервисного обслуживания двигателя.",
    "20R-0472": "Восстановленный топливный насос Cat Reman для обслуживания топливной системы двигателя.",
    "2176290": "Компонент для строительной техники.",
    "227-1204": "Прокладка головки блока цилиндров двигателя или комплект прокладок.",
    "243-4291": "Свеча зажигания CAT с фирменной упаковкой.",
    "2490713": "Топливная форсунка / группа форсунок для обслуживания двигателей CAT, включая контексты C11/C13.",
    "2701528": "Комплект уплотнений / O-ring для сервисного обслуживания оборудования CAT и двигателей.",
    "2701533": "Комплект O-ring / уплотнений для сервисных работ CAT и обслуживания двигателей.",
    "277-3259": "Картридж / сердцевина турбокомпрессора в сборе.",
    "290-2041": "Компонент двигателя, связанный с поршнем, гильзой или цилиндровой втулкой.",
    "3190678": "Топливная форсунка / гидравлический насос-форсунка для обслуживания двигателей CAT.",
    "3200680": "Группа топливных форсунок для обслуживания дизельных двигателей CAT, включая контексты C4.4/C6.6.",
    "335-6220": "Головка блока цилиндров двигателя или головка блока в сборе.",
    "337-7048": "Синий гидравлический клапан или блок управления.",
    "375-8345": "Натяжитель в фирменной упаковке CAT для сервисного обслуживания двигателя.",
    "383-1388": "Длинная прокладка или уплотнительный компонент с упаковкой CAT.",
    "388-1307": "Датчик регулирования давления газа / датчик давления для обслуживания двигателей CAT или генераторных установок.",
    "418-4861": "Светло-зеленый вал, ротор или компонент, связанный с насосом, для обслуживания строительной техники.",
    "438-5682": "Трансформатор зажигания 108 В для генераторов CAT и газовых генераторных установок.",
    "455-7266": "Поршень или компонент цилиндровой втулки с фирменными коробками CAT.",
    "488-1675": "Блок цилиндров, головка блока или компонент двигателя с несколькими отверстиями.",
    "497-5606": "Цилиндровая втулка или гильза для сервисного обслуживания двигателя.",
    "4N8220": "Складская позиция ремней или шлангов для сервисного обслуживания двигателя.",
    "500-8527": "Выпускной клапан с упаковкой CAT.",
    "541-1441": "Черная крыльчатка вентилятора охлаждения двигателя в сборе.",
    "5577633": "Группа топливных форсунок для обслуживания двигателей CAT, включая контексты C9.",
    "567-5160": "Воздушный компрессор или насос в сборе с упаковкой CAT для обслуживания двигателя.",
    "589-7674": "Желтый гидроцилиндр, актуатор или насосный узел.",
    "592-5156": "Электронная панель управления или дисплей контроллера с упаковкой CAT для обслуживания генераторных установок.",
    "6027619": "Свеча зажигания для обслуживания системы зажигания газовых двигателей CAT.",
    "620-1336": "Кабельный датчик в сборе с упаковкой CAT.",
    "6G0490": "Радиатор или теплообменный сердечник для обслуживания генераторных установок.",
    "6I-2358": "Гидравлический или клапанный блок управления.",
    "8T2287": "Боковое зеркало или зеркало заднего вида с упаковкой CAT для обслуживания строительной техники.",
    "9Y0015": "Крышка коромысел, клапанная крышка или серый крышечный компонент с упаковкой CAT.",
    "263-5055": "Головка блока цилиндров C15 или головка двигателя в сборе.",
    "CG260-16": "Газовая генераторная платформа Cat CG260-16 для промышленной выработки электроэнергии.",
    "4P-9638": "Группа кондиционера охлаждающей жидкости / компонент обслуживания системы охлаждения для оборудования CAT.",
    "573-6694": "Круглая пластина, крышка или ступичный компонент для обслуживания строительной техники.",
    "MWM TCG 3016 V16": "Газовый двигатель MWM TCG 3016 V16 для природного газа, биогаза и когенерационных энергетических применений.",
    "MWM TCG 3020 V20": "Газовая двигательная платформа MWM TCG 3020 V20 для промышленной электро- и теплогенерации.",
    "TCG 3016 V16 / TCG 3020 V20": "Газовые двигательные платформы MWM TCG 3016 V16 и TCG 3020 V20 для промышленной энергетики и когенерации.",
    "C32B / C15": "Дизельные двигатели Caterpillar C32B и C15 в сборе для тяжелых промышленных и машинных применений.",
    "3016 V16": "Газовый двигатель 3016 V16 в сборе для природного газа и когенерационной выработки электроэнергии.",
    "3020 V20": "Газовый двигатель 3020 V20 в сборе для промышленной электро- и теплогенерации.",
    "3412": "Позиция семейства двигателей и генераторных установок Caterpillar 3412 для промышленной энергетики.",
    "4385682": "Трансформатор зажигания 108 В для генераторов CAT и газовых генераторных установок.",
    "C32": "Дизельная платформа Caterpillar C32 V12 для горной техники, морских, железнодорожных и энергетических применений.",
    "G36": "Материалы газового двигателя серии Caterpillar G3600 для двигатель-генераторных и энергетических систем.",
    "G3606": "Газовый двигатель Caterpillar G3606 для газовой компрессии и энергетических систем.",
    "8N-1412": "Тяжелая круглая дорожка качения или подшипниковый компонент для обслуживания трансмиссии или тормозной системы.",
    "340-6409": "Клапан управления тормозом / клапанная группа для обслуживания тормозной системы тяжелой техники CAT.",
    "455-8833": "Поршневой компонент для сервисного обслуживания двигателя.",
    "118-7579": "Гидравлический / управляющий клапанный блок для обслуживания строительной техники.",
    "156-0026": "Трубка для рабочей жидкости в сборе для обслуживания машины или двигателя CAT.",
    "3S-4384": "Шестеренный компонент для обслуживания машины или двигателя CAT.",
    "244-1339": "Насос, мотор или вращающийся узел для обслуживания тяжелой техники.",
    "381-9250": "Компонент корпуса поршня двигателя.",
    "9Y-4124": "Поршень / корпус поршня для обслуживания двигателей CAT серии 3500.",
    "315-9959": "Трансмиссия в сборе / компоновка для силовой передачи гусеничного трактора CAT и обслуживания строительной техники.",
}


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def slug(value: str) -> str:
    value = str(value or "").strip()
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-").replace("--", "-")


def mailto(subject: str, body: str = "") -> str:
    href = f"mailto:sales@evergold.sg?subject={quote(subject)}"
    if body:
        href += f"&body={quote(body)}"
    return href


def rel_from_ru(path: str, depth: int) -> str:
    return ("../" * depth) + path


def english_href(path: str, depth: int) -> str:
    return ("../" * depth) + path


def russian_href_for_english(file_path: Path) -> str:
    rel = file_path.relative_to(SITE).as_posix()
    return f"../ru/{rel}" if rel.startswith("products/") else f"ru/{rel}"


def category_for(product: dict) -> dict:
    return CATEGORY_BY_EN.get(product.get("category", ""), CATEGORY_BY_KEY["engine-parts"])


def product_usage(product: dict) -> str:
    part = product.get("part_number", "")
    return PRODUCT_USAGE_RU.get(part, f"{part} - позиция для запроса коммерческого предложения Evergold.")


def prepare_products() -> list[dict]:
    products = json.loads(PRODUCTS_JSON.read_text(encoding="utf-8"))
    prepared: list[dict] = []
    for product in products:
        product = dict(product)
        part = product.get("part_number") or "Part"
        product["slug"] = slug(part)
        product["display_image_path"] = product.get("generated_path") or product.get("web_asset_path") or "assets/images/industrial-parts-warehouse.png"
        product["display_category_ru"] = category_for(product)["name"]
        product["usage_ru"] = product_usage(product)
        prepared.append(product)
    return prepared


def header(active: str, current_path: str, depth: int = 1) -> str:
    links = [
        ("Главная", "index.html", "Home"),
        ("Продукция", "products.html", "Products"),
        ("О компании", "about.html", "About"),
        ("Контакты", "contact.html", "Contact"),
    ]
    nav = "\n".join(
        f'<a class="{"active" if key == active else ""}" href="{rel_from_ru(href, 0)}">{label}</a>'
        for label, href, key in links
    )
    if depth == 2:
        nav = nav.replace('href="index.html"', 'href="../index.html"')
        nav = nav.replace('href="products.html"', 'href="../products.html"')
        nav = nav.replace('href="about.html"', 'href="../about.html"')
        nav = nav.replace('href="contact.html"', 'href="../contact.html"')
    asset_prefix = "../" if depth == 1 else "../../"
    root_prefix = "" if depth == 1 else "../"
    en_link = english_href(current_path, depth)
    return f"""<header class="site-header">
      <a class="brand" href="{root_prefix}index.html" aria-label="Evergold главная">
        <img src="{asset_prefix}assets/company/evergold-logo.png" alt="" />
        <span class="brand-copy"><strong>Evergold</strong><small>EVERGOLD TECHNOLOGY PTE. LTD.</small></span>
      </a>
      <nav class="nav" aria-label="Основная навигация">
        {nav}
      </nav>
      <div class="header-quick-actions" aria-label="Быстрая связь">
        <a class="header-icon-button whatsapp" data-qr-type="whatsapp" href="{root_prefix}contact.html" aria-label="Связаться в WhatsApp" title="WhatsApp">
          <img src="{asset_prefix}assets/icons/whatsapp.svg" alt="" loading="lazy" />
        </a>
        <a class="header-icon-button wechat" data-qr-type="wechat" href="{root_prefix}contact.html" aria-label="Связаться в WeChat" title="WeChat">
          <img src="{asset_prefix}assets/icons/wechat.svg" alt="" loading="lazy" />
        </a>
        <a class="header-icon-button email" href="{mailto('RFQ from Evergold website')}" aria-label="Написать в отдел продаж" title="Email">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16v12H4V6Zm1.7 1.8 6.3 5 6.3-5H5.7Zm12.6 8.4V9.9l-6.3 5-6.3-5v6.3h12.6Z"/></svg>
        </a>
      </div>
      <div class="language-switch" aria-label="Выбор языка">
        <a href="{en_link}" lang="en">EN</a>
        <span aria-current="page">RU</span>
      </div>
      <a class="header-cta" href="{mailto('RFQ for CATERPILLAR genuine parts')}">Запросить цену</a>
    </header>"""


def footer(depth: int = 1) -> str:
    root_prefix = "" if depth == 1 else "../"
    return f"""<footer class="site-footer">
      <div>
        <strong>EVERGOLD TECHNOLOGY PTE. LTD.</strong>
        <span>Поставка оригинальных промышленных деталей CATERPILLAR для международных покупателей.</span>
      </div>
      <div class="footer-links">
        <a href="{root_prefix}products.html">Продукция</a>
        <a href="{root_prefix}about.html">О компании</a>
        <a href="{root_prefix}contact.html">Контакты</a>
        <a href="mailto:sales@evergold.sg">sales@evergold.sg</a>
      </div>
      <p class="legal-note">CATERPILLAR, CAT и связанные обозначения являются товарными знаками соответствующих правообладателей. Evergold поставляет оригинальные детали CATERPILLAR через каналы поиска и торговли; это не означает официальный дилерский статус, авторизацию или аффилированность, если это не указано отдельно.</p>
    </footer>"""


def page(title: str, description: str, body: str, active: str, current_path: str, depth: int = 1, body_class: str = "") -> str:
    asset_prefix = "../" if depth == 1 else "../../"
    cls = f' class="{body_class}"' if body_class else ""
    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}" />
    <link rel="stylesheet" href="{asset_prefix}styles.css?v=ru-i18n-1" />
  </head>
  <body{cls}>
    {header(active, current_path, depth)}
    {body}
    {footer(depth)}
    <script src="{asset_prefix}assets/js/contact-qr-modal.js?v=qr-type-1" defer></script>
  </body>
</html>
"""


def product_card(product: dict, depth: int = 1) -> str:
    part = product.get("part_number") or "Part"
    asset_prefix = "../" if depth == 1 else "../../"
    href_prefix = "products/" if depth == 1 else ""
    return f"""<article class="product-card">
  <a class="product-image-link" href="{href_prefix}{esc(product['slug'])}.html">
    <img src="{asset_prefix}{esc(product['display_image_path'])}" alt="{esc(part)} оригинальная промышленная деталь CATERPILLAR" loading="lazy" />
  </a>
  <div class="product-card-body">
    <span>{esc(product['display_category_ru'])}</span>
    <h3><a href="{href_prefix}{esc(product['slug'])}.html">{esc(part)}</a></h3>
    <p>{esc(product['usage_ru'])}</p>
  </div>
</article>"""


def category_tile(category: dict) -> str:
    return f"""<a class="category-tile {esc(category['tile_class'])} rb-spotlight rb-reveal" href="products/{esc(category['key'])}.html">
  <span>{esc(category['name'])}</span>
  <strong>{esc(category['title'])}</strong>
</a>"""


def spotlight_script() -> str:
    return """<script>
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
        document.querySelectorAll(".rb-reveal, .service-card, .quick-card, .supply-card, .product-card").forEach((item) => {
          revealObserver.observe(item);
        });
      }
    </script>"""


def products_script() -> str:
    return """<script>
      const params = new URLSearchParams(window.location.search);
      const query = (params.get("q") || "").trim().toLowerCase();
      const cards = Array.from(document.querySelectorAll(".catalog-product-grid .product-card"));
      const note = document.querySelector(".catalog-query-note");
      const empty = document.querySelector(".catalog-empty");
      const searchAliases = {
        "injector": ["injector", "форсун", "топлив", "engine parts", "детали дизельных"],
        "spark plug": ["spark", "свеч", "зажиган"],
        "generator": ["generator", "генератор", "энергет"],
        "engine assembly": ["engine assembly", "двигател", "генератор"],
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
        note.textContent = `Показаны результаты по запросу "${params.get("q")}".`;
        empty.hidden = visibleCount !== 0;
      }
    </script>"""


def write_index(products: list[dict]) -> None:
    featured = {product["part_number"]: product for product in products}
    body = f"""
<main>
  <section class="stitch-hero">
    <img class="stitch-hero-image" src="../assets/images/industrial-parts-warehouse.png" alt="Склад промышленных деталей, двигателей и генераторного оборудования" />
    <div class="stitch-hero-pattern" aria-hidden="true"></div>
    <div class="container hero-inner rb-hero-grid">
      <div class="hero-copy rb-reveal">
        <p class="label-gold">Промышленный поиск поставок</p>
        <h1>Поставка оригинальных деталей CATERPILLAR</h1>
        <p class="hero-lead">Поиск и поставка деталей CATERPILLAR для двигателей, техники, горного оборудования и генераторных установок по номеру детали, модели и применению.</p>
        <div class="hero-actions">
          <a class="button rfq" href="{mailto('RFQ for CATERPILLAR genuine parts')}">Отправить RFQ</a>
          <a class="button outline-light" href="products.html">Смотреть продукцию</a>
        </div>
      </div>
      <form class="rb-search-panel rb-spotlight rb-reveal" action="products.html" method="get">
        <label for="hero-part-search">Поиск по номеру детали</label>
        <div class="rb-search-input">
          <input id="hero-part-search" name="q" type="search" placeholder="Номер детали, C15, контроллер, гидравлика" autocomplete="off" />
          <button type="submit">Поиск</button>
        </div>
        <p>Для точного предложения укажите количество, модель машины или двигателя, серийный номер и страну поставки.</p>
        <div class="rb-quick-tags" aria-label="Примеры RFQ">
          <a href="products.html?q=injector">форсунки</a>
          <a href="products.html?q=spark%20plug">свечи зажигания</a>
          <a href="products.html?q=C15">C15</a>
          <a href="products.html?q=C32">C32</a>
        </div>
      </form>
    </div>
  </section>
  <section class="service-strip">
    <div class="container service-grid">
      <article class="service-card">
        <div class="service-icon cat-mark"><img src="https://www.cat.com/content/dam/catDotCom/global-selector-/Cat-logo.png" alt="Логотип CAT" /></div>
        <h2>RFQ по номеру детали</h2>
        <p>Отправьте номера деталей, количество, страну назначения и данные машины или двигателя для коммерческого предложения.</p>
        <a href="{mailto('RFQ from Evergold website')}">Начать запрос</a>
      </article>
      <article class="service-card">
        <div class="service-icon cat-mark"><img src="https://www.cat.com/content/dam/catDotCom/global-selector-/Cat-logo.png" alt="Логотип CAT" /></div>
        <h2>Оригинальные детали CATERPILLAR</h2>
        <p>Поставка оригинальных деталей CATERPILLAR через каналы поиска и торговли.</p>
        <a href="products.html">Открыть каталог</a>
      </article>
      <article class="quick-card">
        <h2>Чек-лист RFQ</h2>
        <ul>
          <li>Номер детали и количество</li>
          <li>Модель машины или двигателя</li>
          <li>Серийный номер</li>
          <li>Фотографии старой детали</li>
        </ul>
      </article>
    </div>
  </section>
  <section class="section supply-section">
    <div class="container">
      <div class="section-heading"><h2>Пять групп поставок</h2><span></span></div>
      <div class="supply-grid">
        {supply_card('products/engine-parts.html', '../assets/generated/visual-edit-c15-ig_080986152c4cac36016a2aa965a73c81909e4a0100f4573888.png', 'Группа 01', 'Детали дизельных двигателей', 'Детали для ремонта двигателей, фильтрации, охлаждения, клапанного механизма, турбокомпрессоров и сервисного обслуживания.')}
        {supply_card('products/construction-machinery.html', '../assets/generated/visual-edit-175-7852-ig_080986152c4cac36016a2aac2f96c88190a284842e832f3e20.png', 'Группа 02', 'Детали строительной техники', 'Гидравлические, трансмиссионные, кабинные, зеркальные и управляющие компоненты для тяжелой техники.')}
        {supply_card('products/mining-machine-parts.html', '../assets/generated/visual-edit-c32b-ig_080986152c4cac36016a2aab0c9f288190bda6062e17ebc0d4.png', 'Группа 03', 'Детали горной техники', 'Усиленные детали для карьерных самосвалов, бульдозеров и высоких нагрузок.')}
        {supply_card('products/generator-set-parts.html', '../assets/generated/visual-edit-3412e-ig_080986152c4cac36016a2aa82b88548190ac39439494058a6d.png', 'Группа 04', 'Детали генераторных установок', 'Контроллеры, радиаторы, элементы охлаждения и сервисные детали для генераторных установок.')}
        {supply_card('products/engine-generator-sets.html', '../assets/products/CG260-16/CG260-16.jpg', 'Группа 05', 'Двигатели в сборе / генераторные установки', 'Дизельные и газовые двигатели в сборе, генераторные установки и комплектные энергетические блоки.', featured=True)}
        <a class="supply-promo-card" href="products/cg260-16.html">
          <div class="promo-image"><img src="../assets/images/cg260-early-2027-delivery.jpg" alt="Генераторная установка CG260 доступна к поставке в начале 2027 года" /></div>
          <div class="promo-copy">
            <span>Доступная единица CG260</span>
            <h3>Поставка CG260 со склада в начале 2027 года</h3>
            <p>Крупная газовая генераторная установка для промышленных энергетических проектов с глобальным поиском поставок, экспортными платежами и быстрым ответом на RFQ.</p>
          </div>
        </a>
      </div>
    </div>
  </section>
  <section class="section process-section">
    <div class="container process-grid">
      <div class="process-copy">
        <h2>Глобальный объем поставок</h2>
        <div class="process-list">
          <article><span>01</span><div><h3>Детали CAT и комплектные единицы</h3><p>Поставка охватывает детали двигателей, строительной техники, горного оборудования, генераторных установок, а также двигатели и энергетические блоки в сборе.</p></div></article>
          <article><span>02</span><div><h3>Глобальная сеть поиска</h3><p>Международные складские каналы помогают закрывать редкие позиции, сменные узлы, комплектные энергетические блоки и трансграничные промышленные закупки.</p></div></article>
          <article><span>03</span><div><h3>Международная оплата и быстрый расчет</h3><p>Поддержка международных платежей, экспортная коммуникация и быстрый ответ на RFQ помогают перейти от номера детали к плану поставки.</p></div></article>
        </div>
      </div>
      <div class="process-image">
        <img src="../assets/images/global-cat-parts-supply-warehouse.png" alt="Склад промышленных деталей, двигателей и генераторных установок для глобальной поставки" />
        <div class="process-badge"><span>Глобальная поставка</span><strong>Детали, двигатели и генераторные установки</strong></div>
      </div>
    </div>
  </section>
  <section class="section featured-section">
    <div class="container">
      <div class="section-heading"><h2>Рекомендуемые позиции по номеру детали</h2><span></span></div>
      <div class="product-grid">
        {product_card(featured['3412E'])}
        {product_card(featured['C15'])}
        {product_card(featured['497-5606'])}
        {product_card(featured['592-5156'])}
      </div>
    </div>
  </section>
  <section class="final-cta rb-spotlight rb-reveal">
    <div class="container final-cta-inner">
      <h2>Готовы отправить RFQ по деталям CATERPILLAR?</h2>
      <p>Передайте номера деталей, количество, страну назначения и данные модели для коммерческого предложения.</p>
      <div class="hero-actions center">
        <a class="button rfq" href="{mailto('RFQ from Evergold website')}">Отправить RFQ</a>
        <a class="button outline-light" href="contact.html">Связаться с продажами</a>
      </div>
    </div>
  </section>
</main>
{spotlight_script()}"""
    (RU / "index.html").write_text(
        page(
            "Evergold | Поставка оригинальных деталей CATERPILLAR",
            "Evergold поставляет оригинальные промышленные детали CATERPILLAR для двигателей, техники, горного оборудования и генераторных установок.",
            body,
            active="Home",
            current_path="index.html",
            body_class="react-bits-enhanced",
        ),
        encoding="utf-8",
    )


def supply_card(href: str, image: str, group: str, title: str, text: str, featured: bool = False) -> str:
    cls = "supply-card supply-card-feature" if featured else "supply-card"
    return f"""<a class="{cls}" href="{href}">
          <div class="supply-image">
            <img src="{image}" alt="{esc(title)}" />
            <span>{esc(group)}</span>
          </div>
          <div><h3>{esc(title)}</h3><p>{esc(text)}</p></div>
        </a>"""


def write_products(products: list[dict]) -> None:
    tiles = "\n\n".join(category_tile(category) for category in CATEGORIES)
    cards = "\n\n".join(product_card(product) for product in products)
    body = f"""
<main>
  <section class="page-hero products-hero rb-spotlight rb-reveal">
    <div class="container products-hero-inner">
      <div class="products-hero-copy">
        <p class="market-line">Ассортимент продукции</p>
        <h1>Оригинальные детали CATERPILLAR, организованные для экспортных RFQ.</h1>
      </div>
      <p class="lead">66 выбранных позиций по номерам деталей в пяти группах поставок с понятным описанием применения для подготовки экспортного RFQ.</p>
    </div>
  </section>
  <section class="category-strip-section" aria-label="Категории продукции">
    <div class="category-grid">{tiles}</div>
  </section>
  <section class="section">
    <div class="section-intro">
      <h2>Выбранные позиции по номеру детали</h2>
      <p>Используйте страницы продукции для подготовки RFQ с количеством, страной назначения и информацией о машине или двигателе.</p>
    </div>
    <p class="catalog-query-note" hidden></p>
    <div class="product-grid catalog-product-grid">{cards}</div>
    <p class="catalog-empty" hidden>В выбранном наборе нет совпадающих позиций. Отправьте номер детали на sales@evergold.sg для поддержки RFQ.</p>
  </section>
</main>
{products_script()}"""
    (RU / "products.html").write_text(
        page(
            "Продукция | Evergold CATERPILLAR",
            "66 выбранных позиций Evergold по оригинальным деталям CATERPILLAR для строительной техники, двигателей, генераторных установок и горного оборудования.",
            body,
            active="Products",
            current_path="products.html",
            body_class="react-bits-enhanced products-page",
        ),
        encoding="utf-8",
    )


def write_category_pages(products: list[dict]) -> None:
    out = RU / "products"
    out.mkdir(parents=True, exist_ok=True)
    for category in CATEGORIES:
        category_products = [product for product in products if category_for(product)["key"] == category["key"]]
        cards = "\n\n".join(product_card(product, depth=2) for product in category_products)
        body = f"""
<main>
  <section class="page-hero compact category-hero">
    <div>
      <p class="market-line">Категория поставок CATERPILLAR</p>
      <h1>{esc(category['title'])}</h1>
      <p class="lead">{esc(category['summary'])}</p>
    </div>
    <a class="button primary large" href="../products.html">Все продукты</a>
  </section>
  <section class="section">
    <div class="product-grid">{cards}</div>
  </section>
</main>"""
        (out / f"{category['key']}.html").write_text(
            page(f"{category['title']} | Evergold", category["summary"], body, "Products", f"products/{category['key']}.html", depth=2),
            encoding="utf-8",
        )


def write_product_pages(products: list[dict]) -> None:
    out = RU / "products"
    out.mkdir(parents=True, exist_ok=True)
    for product in products:
        part = product.get("part_number") or "Part"
        category = category_for(product)["name"]
        image = "../../" + product["display_image_path"]
        usage = product["usage_ru"]
        body = f"""
<main>
  <section class="product-detail">
    <div class="detail-image">
      <img src="{esc(image)}" alt="{esc(part)} оригинальная промышленная деталь CATERPILLAR" />
    </div>
    <div class="detail-copy">
      <p class="market-line">{esc(category)}</p>
      <h1>{esc(part)}</h1>
      <p class="lead">{esc(usage)}</p>
      <dl class="spec-list">
        <div><dt>Номер детали</dt><dd>{esc(part)}</dd></div>
        <div><dt>Категория</dt><dd>{esc(category)}</dd></div>
        <div><dt>Применение</dt><dd>{esc(category)}</dd></div>
      </dl>
      <div class="notice">
        <strong>Применение</strong>
        <p>{esc(usage)}</p>
      </div>
      <a class="button primary large" href="{mailto(f'RFQ for {part}', f'Hello Evergold,\\n\\nPlease quote {part}.\\n\\nCompany:\\nCountry:\\nQuantity:\\nMachine / engine model:\\nAdditional request details:\\n')}">Запросить цену на {esc(part)}</a>
    </div>
  </section>
</main>"""
        (out / f"{product['slug']}.html").write_text(
            page(
                f"{part} | Evergold CATERPILLAR",
                f"Запрос коммерческого предложения на {part}, оригинальную промышленную деталь CATERPILLAR от Evergold.",
                body,
                "Products",
                f"products/{product['slug']}.html",
                depth=2,
            ),
            encoding="utf-8",
        )


def write_about() -> None:
    body = """
<main class="about-page">
  <section class="about-hero">
    <div class="about-hero-inner">
      <div class="about-hero-copy">
        <div class="about-title-block">
          <p class="market-line">О компании Evergold</p>
          <h1>Международная поддержка поставок оригинальных промышленных деталей CATERPILLAR.</h1>
          <p class="lead">Evergold занимается практическим поиском поставок для строительной техники, дизельных двигателей, горного оборудования, генераторных установок и комплектных энергетических блоков для глобальных B2B-покупателей.</p>
        </div>
        <div class="about-proof-grid" aria-label="Возможности поставки">
          <div><strong>Глобальный поиск</strong><span>Детали CAT и комплектные единицы из международных складских каналов.</span></div>
          <div><strong>Быстрый ответ на RFQ</strong><span>Поддержка коммерческих предложений по номеру детали для закупочных команд.</span></div>
          <div><strong>Экспортная координация</strong><span>Поддержка платежей и логистики для трансграничных промышленных заказов.</span></div>
        </div>
      </div>
      <figure class="about-route-map">
        <img src="../assets/images/cat-global-routes-map-only-canada-top-4x.png" width="5040" height="2982" alt="Карта глобальных маршрутов поставки с выделенным источником в Канаде" />
        <figcaption>Глобальные маршруты поставок деталей CAT и энергетических блоков.</figcaption>
      </figure>
    </div>
  </section>
  <section class="section about-supply-section">
    <div class="section-intro">
      <h2>Для зарубежных дистрибьюторов, ремонтных мастерских, закупочных команд и промышленных операторов.</h2>
      <p>Сайт помогает быстро подготовить международный RFQ: изображения продукции, номера деталей и контакты организованы так, чтобы покупатель мог сразу собрать полную информацию для запроса.</p>
    </div>
  </section>
</main>"""
    (RU / "about.html").write_text(
        page(
            "О компании Evergold | Поставка деталей CATERPILLAR",
            "Информация о Evergold, поставщике оригинальных промышленных деталей CATERPILLAR для глобальных B2B-покупателей.",
            body,
            "About",
            "about.html",
        ),
        encoding="utf-8",
    )


def write_contact() -> None:
    body = f"""
<main class="contact-page">
  <section class="page-hero compact">
    <p class="market-line">Запрос коммерческого предложения</p>
    <h1>Отправьте номера деталей, количество и данные применения.</h1>
    <p class="lead">Самый быстрый RFQ включает номера деталей, модели оборудования или двигателя, фотографии, количество, страну поставки и желаемый срок.</p>
  </section>
  <section class="section contact-grid">
    <div class="contact-card">
      <span>Email</span>
      <h2>sales@evergold.sg</h2>
      <p>Используйте email для списков номеров деталей, фотографий и RFQ с вложениями.</p>
      <a class="button primary" href="{mailto('RFQ for CATERPILLAR genuine parts')}">Запросить цену</a>
    </div>
    <div class="contact-card muted">
      <span>Чек-лист RFQ</span>
      <ul>
        <li>Компания и страна</li>
        <li>Номера деталей и количество</li>
        <li>Модель машины, двигателя или генератора</li>
        <li>Фотографии продукции или файлы вложений</li>
        <li>Страна доставки</li>
      </ul>
    </div>
    <div class="contact-card contact-qr-card">
      <span>Прямые QR-контакты</span>
      <div class="contact-qr-grid" aria-label="QR-коды прямых контактов">
        <figure class="contact-qr-item"><img src="../assets/contact/annie-whatsapp-cropped.jpg" alt="QR-код WhatsApp Annie" loading="lazy" /><figcaption><strong>Annie</strong><small>WhatsApp</small></figcaption></figure>
        <figure class="contact-qr-item"><img src="../assets/contact/annie-wechat-cropped.jpg" alt="QR-код WeChat Annie" loading="lazy" /><figcaption><strong>Annie</strong><small>WeChat</small></figcaption></figure>
        <figure class="contact-qr-item"><img src="../assets/contact/joe-whatsapp-cropped.jpg" alt="QR-код WhatsApp Joe" loading="lazy" /><figcaption><strong>Joe</strong><small>WhatsApp</small></figcaption></figure>
        <figure class="contact-qr-item"><img src="../assets/contact/joe-wechat-cropped.png" alt="QR-код WeChat Joe" loading="lazy" /><figcaption><strong>Joe</strong><small>WeChat</small></figcaption></figure>
      </div>
    </div>
  </section>
</main>"""
    (RU / "contact.html").write_text(
        page(
            "Контакты Evergold | RFQ на детали CATERPILLAR",
            "Свяжитесь с отделом продаж Evergold для запроса оригинальных деталей CATERPILLAR для техники, двигателей, горного оборудования и генераторных установок.",
            body,
            "Contact",
            "contact.html",
        ),
        encoding="utf-8",
    )


def add_english_language_switch() -> None:
    for html_file in [SITE / "index.html", SITE / "products.html", SITE / "about.html", SITE / "contact.html", *sorted((SITE / "products").glob("*.html"))]:
        text = html_file.read_text(encoding="utf-8")
        text = re.sub(r'\s*<div class="language-switch".*?</div>\s*', "\n", text, flags=re.S)
        ru_href = russian_href_for_english(html_file)
        switch = f"""
      <div class="language-switch" aria-label="Language selection">
        <span aria-current="page">EN</span>
        <a href="{ru_href}" lang="ru">RU</a>
      </div>"""
        text = text.replace("\n      <a class=\"header-cta\"", f"{switch}\n      <a class=\"header-cta\"", 1)
        html_file.write_text(text, encoding="utf-8")


def main() -> None:
    if not SITE.exists():
        raise RuntimeError(f"Missing site directory: {SITE}")
    if RU.exists():
        shutil.rmtree(RU)
    RU.mkdir(parents=True)
    products = prepare_products()
    write_index(products)
    write_products(products)
    write_category_pages(products)
    write_product_pages(products)
    write_about()
    write_contact()
    add_english_language_switch()
    print(f"Generated Russian site: {len(products)} products, {len(CATEGORIES)} categories")


if __name__ == "__main__":
    main()
