import datetime
import logging
import re
from contextlib import contextmanager
from typing import Iterator, List, Optional

from playwright.sync_api import sync_playwright, Page, BrowserContext
from car_scraper.db.entity.WebmotorsCarAd import WebmotorsCarAd
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.dto.CarDownloadInfoDTO import CarDownloadInfoDTO
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.scrapers.scraper import BaseScraper
from car_scraper.utils.config import PROJECT_ROOT
from car_scraper.utils.config import settings
from car_scraper.utils.human import human_delay, human_scroll, human_scroll_to_bottom

logger = logging.getLogger(__name__)
tmp_dir = PROJECT_ROOT / "tmp"
BTN_BRANDS = "button.filters-make-select-picker_Button__2ESw5"
LI_BRAND = ".filters-make-select-list_BodyListItem__XTOEv"
MAIN_READY = "main.search-result_Container__zDYhq a[href] h2"
MAIN_AD_READY = "main"
DIV_INNER = "div._Inner_nv1r7_20"
SKELETON = "[data-testid='skeleton-0']"
TOTAL_ADS = 'p[data-qa="research_container"]'
AD_DETAILS = "VehicleBasicInformation"
AD_IMAGES = "img.DetailCarousel__container__items__photo"
STATUS_HEADER = "h1.StatusHeader__header__title"
VENDIDO = "Veeeennndeeeeuuu"
VEHICLE_DETAILS = "VehicleCharacteristic"

LOC_SELLER_NAME = "#VehicleSellerInformationName"
LOC_SELLER_LOCATION = "#VehicleSellerInformationState"
LOC_SELLER_PHONE = "#VehicleSellerInformationPhone_"
LOC_SELLER_PHONE_DDD = "#VehicleSellerInformationPhone_ small"
LOC_SELLER_CODE = ".CardSeller__code__connection__number"
LOC_SELLER_STOCK = "#VehicleSellerInformationStock"
LOC_CONTAINER = "#VehicleSellerInformation"
LOC_NAME = "#VehicleSellerInformationName"
LOC_PRIVATE_NAME = "#VehicleSellerPrivateName"
LOC_LOCATION = "#VehicleSellerInformationState"
LOC_PRIVATE_LOCATION = "#VehicleSellerPrivateState"
LOC_PHONE = "#VehicleSellerInformationPhone_"
LOC_STORE_WRAPPER = ".CardSeller--dealership"
LOC_CODE = ".CardSeller__code__connection__number"
LOC_STOCK = "#VehicleSellerInformationStock"
LOC_PRIVATE_WRAPPER = ".CardSeller--private"

WAIT_SHORT = 5_000
WAIT_STD = 20_000

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

VIEWPORT = {"width": 1366, "height": 768}
HDRS = {"Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"}


class Webmotors_Scraper(BaseScraper):
    ADS_PER_PAGE = 47

    def __init__(self, url_base: Optional[str] = None, headless: bool = False):
        self.url_base = (url_base or settings.WEBMOTORS_URL).rstrip("/") + "/carros-usados"
        self.headless = headless
        self._re_num = re.compile(r"([\d\.,]+)")

    # -------------------------
    # Infra compartilhada (DRY)
    # -------------------------
    @contextmanager
    def _page(self, url: Optional[str] = None) -> Iterator[Page]:
        #proxy_cfg = proxy_manager.get_proxy()

        with sync_playwright() as p:
            # browser = p.chromium.launch(headless=self.headless, args=["--disable-blink-features=AutomationControlled"])
            browser = p.chromium.launch(headless=self.headless,
         #                               proxy=proxy_cfg,
                                        args=[ "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox", "--disable-extensions", "--disable-gpu" ], )
            context: BrowserContext = browser.new_context(
                user_agent=UA,
                locale="pt-BR",
                viewport=VIEWPORT,
                extra_http_headers=HDRS
            )
            page = context.new_page()
            try:
                if url:
                    page.goto(url, wait_until="domcontentloaded")
                yield page

            except Exception as e:
                logger.error(f"Error while loading page with proxy {proxy}: {e}")
                raise e

            finally:
                context.close()
                browser.close()

    def _wait_results_ready(self, page: Page) -> None:
        try:
            page.wait_for_selector(SKELETON, timeout=WAIT_SHORT)
        except Exception:
            pass  # pode não aparecer

        page.wait_for_function(
            "selector => !document.querySelector(selector)",
            arg=SKELETON,
            timeout=WAIT_STD
        )

        page.wait_for_selector(MAIN_READY, timeout=WAIT_STD)

    # -------------------------
    # Métodos principais
    # -------------------------
    def get_brands(self) -> List[BrandDTO]:
        with self._page(self.url_base) as page:
            human_scroll(page, 600)

            page.wait_for_selector(BTN_BRANDS, timeout=WAIT_STD)
            page.click(BTN_BRANDS)

            page.wait_for_selector(LI_BRAND, timeout=WAIT_STD)
            itens = page.locator(LI_BRAND)

            logger.info("getting brand links and name")
            brands: List[BrandDTO] = []
            count = itens.count()
            for i in range(count):
                li = itens.nth(i)
                name = (li.text_content() or "").strip()
                href = li.locator("a").get_attribute("href")
                if not name or not href:
                    continue
                logger.info(f"{name} : {href}")
                brands.append(BrandDTO(name=name, href=href, source=JobSource.WEBMOTORS))
                human_delay(0.2, 0.6)

            return brands

    def get_total_ads(self, brand: BrandDTO) -> Optional[int]:
        if not brand.href:
            return None

        with self._page(brand.href) as page:
            self._wait_results_ready(page)
            human_scroll_to_bottom(page)

            page.wait_for_selector(DIV_INNER, timeout=WAIT_STD)
            page.wait_for_selector(TOTAL_ADS, timeout=WAIT_STD)

            text = page.locator(TOTAL_ADS).first.inner_text().strip()
            m = self._re_num.search(text)
            return int(m.group(1).replace(".", "")) if m else None

    def get_cars_from_brand(self, brand: BrandDTO, job_id: int, page_num: int) -> list[CarDownloadInfoDTO]:
        if not brand.href:
            return []

        logger.info(f"Getting adds from: {brand.href}")
        with self._page(brand.href) as page:
            self._wait_results_ready(page)
            human_scroll_to_bottom(page)
            page.wait_for_selector(DIV_INNER, timeout=WAIT_STD)

            inners = page.locator(DIV_INNER)
            count = inners.count()
            logger.info(f"Ads on the page: {count}")

            cars: list[CarDownloadInfoDTO] = []

            for i in range(count):
                inner = inners.nth(i)
                first_child = inner.locator("> div").first

                a_tag = first_child.locator("a")
                img_tag = a_tag.locator("img")

                href = a_tag.get_attribute("href")
                alt = img_tag.get_attribute("alt")
                src = (img_tag.get_attribute("src") or "").replace("\\", "/").strip()

                if href and alt and src:
                    cars.append(
                        CarDownloadInfoDTO(
                            job_id=job_id,
                            href=href,
                            car_desc=alt,
                            image=src,
                            brand_id=brand.id if hasattr(brand, "id") else None,
                            status=JobStatus.PENDING,
                            page=page_num
                        )
                    )

        return cars

    def is_ad_sold(self, href: str) -> bool:
        with self._page(href) as page:
            try:
                page.wait_for_selector(STATUS_HEADER, timeout=WAIT_SHORT)
                text = page.inner_text(STATUS_HEADER)

                return VENDIDO in text
            except Exception:
                return False

    def get_car_ad_via_api(self, car_info: CarDownloadInfoDTO) -> WebmotorsCarAd | None:
        """
        Captura os detalhes completos do anúncio usando a chamada interna
        da API /api/detail/car/{id}, evitando scraping e evitando captcha.
        Funciona em qualquer Playwright Sync.
        """
        if not car_info.href:
            return None

        logger.info(f"Interceptando API interna do anúncio: {car_info.href}")

        api_json = None

        with self._page(car_info.href) as page:

            def on_response(response):
                nonlocal api_json
                url = response.url
                if "api/detail/car" in url and response.status == 200:
                    try:
                        api_json = response.json()
                    except Exception as e:
                        logger.error(f"Erro ao ler JSON da API: {e}")

            page.on("response", on_response)

            try:
                page.wait_for_selector("main", timeout=WAIT_STD)
            except:
                pass

            page.wait_for_timeout(4000)

            if not api_json:
                ad_id = car_info.href.rstrip("/").split("/")[-1]
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"{tmp_dir}/error_screen_{ad_id}_{timestamp}.png"
                page.screenshot(path=screenshot_path)
                logger.error(f"Failed to capture internal API call for ad ID: {ad_id}. Screenshot saved at: {screenshot_path}")
                return None

            return api_json