from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "stitch-migration-products-update"
VK_URL = "https://vk.ru/evergold1"


class VkFooterTests(unittest.TestCase):
    def test_generators_and_static_pages_include_the_vk_entry(self):
        expected = (
            f'href="{VK_URL}"',
            'class="footer-social-link footer-vk-link"',
            'target="_blank"',
            'rel="noopener noreferrer"',
        )

        generators = (
            ROOT / "scripts" / "generate_stitch_products_update.py",
            ROOT / "scripts" / "generate_russian_site.py",
        )
        pages = tuple(
            path for path in SITE.rglob("*.html")
            if "assets" not in path.relative_to(SITE).parts
        )

        self.assertGreater(len(pages), 0)
        for path in (*generators, *pages):
            content = path.read_text(encoding="utf-8")
            for value in expected:
                with self.subTest(path=path, value=value):
                    self.assertIn(value, content)
            with self.subTest(path=path, value="VK precedes product navigation"):
                footer_links = content[content.index('<div class="footer-links">'):]
                product_label = (
                    '>Продукция</a>'
                    if path.name == "generate_russian_site.py" or "/ru/" in path.as_posix()
                    else '>Products</a>'
                )
                self.assertLess(
                    footer_links.index(f'href="{VK_URL}"'),
                    footer_links.index(product_label),
                )

    def test_vk_icon_and_footer_styles_exist(self):
        icon = SITE / "assets" / "icons" / "vk.svg"
        styles = (SITE / "styles.css").read_text(encoding="utf-8")

        self.assertTrue(icon.is_file())
        self.assertIn(".footer-social-link", styles)
        self.assertIn(".footer-vk-link", styles)


if __name__ == "__main__":
    unittest.main()
