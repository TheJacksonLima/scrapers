from playwright.sync_api import sync_playwright
from car_scraper.scrapers.scraper import BaseScraper, BrandDTO
from car_scraper.utils.human import human_delay, human_scroll, human_scroll_to_bottom, show_html
from car_scraper.utils.config import settings
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

            page.wait_for_selector("main.search-result_Container__zDYhq", timeout=20000)
            container = page.locator("main.search-result_Container__zDYhq")

            human_scroll_to_bottom(page)
            show_html(container)

            elements = container.locator("> *")

            count = elements.count()
            print(f"Total de elementos dentro de #search-container: {count}")

            items = []
            for i in range(count):
               el = elements.nth(i)
               html = el.inner_html()
               tag_name = el.evaluate("el => el.tagName")
               items.append({"index": i, "tag": tag_name, "content": html})
               print(f"Elemento {i + 1}: <{tag_name}>")

