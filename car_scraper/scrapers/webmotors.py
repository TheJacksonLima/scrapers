from playwright.sync_api import sync_playwright
from .scraper import BaseScraper, BrandDTO
from utils.human import human_delay, human_scroll
from autoscraper.config import settings

class WebmotorsScraper(BaseScraper):
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
            page.wait_for_load_state("networkidle")
            human_scroll(page, 600)

            page.wait_for_selector("button.filters-make-select-picker_Button__2ESw5", timeout=20000)
            page.click("button.filters-make-select-picker_Button__2ESw5")

            page.wait_for_selector(".filters-make-select-list_BodyListItem__XTOEv", timeout=20000)
            itens = page.locator(".filters-make-select-list_BodyListItem__XTOEv")
            marcas: list[BrandDTO] = []
            for i in range(itens.count()):
                li = itens.nth(i)
                name = li.text_content().strip()
                href = li.locator("a").get_attribute("href")
                marcas.append(BrandDTO(name=name, href=href, surce="webmotors"))
                human_delay(0.2, 0.6)

            browser.close()
            return marcas
