from playwright.sync_api import sync_playwright
from car_scraper.scrapers.scraper import BaseScraper, BrandDTO
from car_scraper.utils.human import human_delay, human_scroll, human_scroll_to_bottom, show_html
from car_scraper.utils.config import settings
import re
import logging

logger = logging.getLogger(__name__)


class Webmotors_Scraper(BaseScraper):
    def __init__(self, url_base: str | None = None):
        self.url_base = (url_base or settings.WEBMOTORS_URL).rstrip("/") + "/carros-usados"

    def get_brands(self) -> list[BrandDTO]:

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
                locale="pt-BR", viewport={"width": 1366, "height": 768},
                extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"}
            )
            page = context.new_page()
            page.goto(self.url_base, wait_until="domcontentloaded")
            human_scroll(page, 600)

            page.wait_for_selector("button.filters-make-select-picker_Button__2ESw5", timeout=20000)
            page.click("button.filters-make-select-picker_Button__2ESw5")

            page.wait_for_selector(".filters-make-select-list_BodyListItem__XTOEv", timeout=20000)
            itens = page.locator(".filters-make-select-list_BodyListItem__XTOEv")
            list_brands: list[BrandDTO] = []

            logger.info("getting brand links and name")
            for i in range(itens.count()):
                li = itens.nth(i)
                name = li.text_content().strip()
                href = li.locator("a").get_attribute("href")
                logger.info(f"{name} : {href}")
                list_brands.append(BrandDTO(name=name, href=href, source="webmotors"))
                human_delay(0.2, 0.6)

            browser.close()
            return list_brands

    def get_total_ads(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
                locale="pt-BR", viewport={"width": 1366, "height": 768},
                extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"}
            )
            page = context.new_page()
            page.goto(brand.href, wait_until="domcontentloaded")

            try:
                page.wait_for_selector("[data-testid='skeleton-0']", timeout=5000)
            except:
                pass

            page.wait_for_function("() => !document.querySelector('[data-testid=\"skeleton-0\"]')", timeout=20000)
            page.wait_for_selector("main.search-result_Container__zDYhq a[href] h2", timeout=20000)
            human_scroll_to_bottom(page)

            page.wait_for_selector("div._Inner_nv1r7_20", timeout=20000)
            page.wait_for_selector('p[data-qa="research_container"]', timeout=10000)
            element = page.locator('p[data-qa="research_container"]').first
            print(f"Element: {element} type{type(element)}")
        
            text = element.inner_text().strip()
            match = re.search(r"([\d\.,]+)", text)
            if match:
                return match.group(1)
            else:
                return None


    def get_cars_from_brand(self, brand: BrandDTO):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
                locale="pt-BR", viewport={"width": 1366, "height": 768},
                extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"}
            )
            page = context.new_page()
            page.goto(brand.href, wait_until="domcontentloaded")

            try:
                page.wait_for_selector("[data-testid='skeleton-0']", timeout=5000)
            except:
                pass

            page.wait_for_function("() => !document.querySelector('[data-testid=\"skeleton-0\"]')", timeout=20000)
            page.wait_for_selector("main.search-result_Container__zDYhq a[href] h2", timeout=20000)
            human_scroll_to_bottom(page)

            page.wait_for_selector("div._Inner_nv1r7_20", timeout=20000)

            inners = page.locator("div._Inner_nv1r7_20")
            count = inners.count()
            print(f"Ads on the page {count} divs _Inner_nv1r7_20")
            cars = []
            for i in range(count):
                inner = inners.nth(i)
                first_child = inner.locator("> div").first

                a_tag = first_child.locator("a")
                img_tag = a_tag.locator("img")

                href = a_tag.get_attribute("href")
                alt = img_tag.get_attribute("alt")
                src = (img_tag.get_attribute("src") or "").replace("\\", "/").strip()

                if href and alt and src:
                    cars.append({
                        "href": href,
                        "car_desc": alt,
                        "image": src
                    })
