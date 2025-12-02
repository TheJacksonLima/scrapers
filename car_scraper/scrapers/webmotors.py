import logging
import re

from car_scraper.db.entity.WebmotorsCarAd import WebmotorsCarAd
from car_scraper.db.models.dto.CarDownloadInfoDTO import CarDownloadInfoDTO
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.dto.CarAdInfoDTO import CarAdInfoDTO
from car_scraper.db.models.dto.SellerInfoDTO import SellerInfoDTO
from contextlib import contextmanager
from typing import Iterator, List, Optional, Tuple
from playwright.sync_api import sync_playwright, Page, BrowserContext
from car_scraper.scrapers.scraper import BaseScraper
from car_scraper.utils.human import human_delay, human_scroll, human_scroll_to_bottom, save_page_to_file, show_html
from car_scraper.utils.config import settings
from car_scraper.utils.my_time_now import my_time_now
from car_scraper.db.models.enums.JobStatus import JobStatus

logger = logging.getLogger(__name__)

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
    def __init__(self, url_base: Optional[str] = None, headless: bool = False):
        self.url_base = (url_base or settings.WEBMOTORS_URL).rstrip("/") + "/carros-usados"
        self.headless = headless
        self._re_num = re.compile(r"([\d\.,]+)")

    # -------------------------
    # Infra compartilhada (DRY)
    # -------------------------
    @contextmanager
    def _page(self, url: Optional[str] = None) -> Iterator[Page]:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, args=["--disable-blink-features=AutomationControlled"])
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
                brands.append(BrandDTO(name=name, href=href, source="webmotors"))
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

    def extract_ad_info(self, items: list[str]) -> CarAdInfoDTO:
        car_ad_info = CarAdInfoDTO()
        for raw in items:
            if "\n" in raw:
                key, value = raw.strip().split("\n", 1)
                key = key.strip()
                value = value.strip()
            else:
                key = "Optional"
                value = raw.strip()

            match key:
                case "Cidade":
                    car_ad_info.city = value
                case "Ano":
                    car_ad_info.year = value
                case "KM":
                    try:
                        car_ad_info.km = int(value.replace(".", "").replace(" km", "").strip())
                    except ValueError:
                        pass
                case "Câmbio":
                    car_ad_info.transmission = value
                case "Carroceria":
                    car_ad_info.type = value
                case "Cor":
                    car_ad_info.color = value
                case "Aceita troca":
                    car_ad_info.trade_in = value.lower() == "sim"
                case "Único dono":
                    car_ad_info.status = value.lower() == "sim"
                case "IPVA pago":
                    car_ad_info.ipva = value.lower() == "sim"
                case "Licenciado":
                    car_ad_info.license = value.lower() == "sim"
                case "Optional":
                    if car_ad_info.items is None:
                        car_ad_info.items = []
                    car_ad_info.items.append(value)

        return car_ad_info

    def get_seller_info(self, page) -> SellerInfoDTO | None:
        page.wait_for_selector(LOC_CONTAINER)
        container = page.locator(LOC_CONTAINER)

        is_store = container.locator(LOC_STORE_WRAPPER).count() > 0
        is_private = container.locator(LOC_PRIVATE_WRAPPER).count() > 0
        seller_name = None
        seller_location = None
        contact_code = None
        stock_url = None
        phone_num = None

        if is_private:
            seller_name = container.locator(LOC_PRIVATE_NAME).text_content().strip()
            seller_location = container.locator(LOC_PRIVATE_LOCATION).text_content().strip()

        elif is_store:
            seller_name = container.locator(LOC_NAME).text_content().strip()
            seller_location = container.locator(LOC_LOCATION).text_content().strip()
            code_loc = container.locator(LOC_CODE)
            if code_loc.count() > 0:
                contact_code = code_loc.text_content().strip()

            stock_path = container.locator(LOC_STOCK).get_attribute("href")
            phone_locator = container.locator(LOC_PHONE)
            if phone_locator.count() > 0:
                phone_num = phone_locator.text_content().strip()

            if stock_path:
                stock_url = f"https://www.webmotors.com.br{stock_path}"

        if seller_name is not None:
            seller_dto = SellerInfoDTO(
                name=seller_name,
                location=seller_location,
                phone=phone_num,
                contact_code=contact_code,
                stock_url=stock_url,
                is_private=is_private,
            )
        else:
            seller_dto = None

        logger.info(f"{seller_dto}")
        return seller_dto


    def parse_api_json_to_entity(api_json: dict) -> WebmotorsCarAd:
        """
        Converte o JSON bruto da API interna do Webmotors
        para a entidade WebmotorsCarAd (SQLAlchemy ORM).
        """

        spec = api_json.get("Specification", {})
        seller = api_json.get("Seller", {})
        media = api_json.get("Media", {})

        # Valores básicos
        unique_id = api_json.get("UniqueId")

        # Preços
        prices = api_json.get("Prices", {})
        price = float(prices.get("Price", 0)) if prices.get("Price") else None
        search_price = float(prices.get("SearchPrice", 0)) if prices.get("SearchPrice") else None

        # Fotos
        photos_list = media.get("Photos", [])
        photos = [{"url": p.get("PhotoPath"), "order": p.get("Order")} for p in photos_list]

        # Conversões defensivas
        def to_int(x: Optional[str]):
            if x is None:
                return None
            try:
                return int(x)
            except:
                return None

        # Criar entidade ORM
        entity = WebmotorsCarAd(
            unique_id=unique_id,

            price=price,
            search_price=search_price,

            make=spec.get("Make", {}).get("Value"),
            model=spec.get("Model", {}).get("Value"),
            version=spec.get("Version", {}).get("Value"),

            year_fabrication=to_int(spec.get("YearFabrication")),
            year_model=to_int(spec.get("YearModel")),
            odometer=to_int(spec.get("Odometer")),
            transmission=spec.get("Transmission"),
            fuel=spec.get("Fuel"),
            body_type=spec.get("BodyType"),

            color=spec.get("Color", {}).get("Primary"),
            final_plate=spec.get("FinalPlate"),
            armored=(spec.get("Armored") == "S"),

            # JSON fields
            optionals=spec.get("Optionals", []),
            lifestyle=spec.get("LifeStyle", []),
            vehicle_attributes=spec.get("VehicleAttributes", []),

            # Seller
            seller_type=seller.get("SellerType"),
            seller_name=seller.get("FantasyName"),
            seller_city=seller.get("City"),
            seller_state=seller.get("State"),
            seller_cnpj=seller.get("CNPJ"),
            seller_phones=seller.get("Phones", []),
            seller_localization=seller.get("Localization", []),

            photos=photos,

            # Datas (ISO strings sem conversão)
            created_date_api=api_json.get("CreatedDate"),
            published_date_api=spec.get("DatePublished"),
        )

        return entity

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

            # Listener para todas responses
            def on_response(response):
                nonlocal api_json
                url = response.url
                if "api/detail/car" in url and response.status == 200:
                    try:
                        api_json = response.json()
                    except Exception as e:
                        logger.error(f"Erro ao ler JSON da API: {e}")

            page.on("response", on_response)

            # Carrega a página e espera o HTML básico (garante que a SPA carregou)
            try:
                page.wait_for_selector("main", timeout=WAIT_STD)
            except:
                pass

            # Dá tempo para a API disparar automaticamente
            page.wait_for_timeout(4000)

            if not api_json:
                logger.error("Não foi possível capturar a chamada da API interna.")
                return None

            return self.parse_api_json_to_entity(api_json)

    def get_car_ad(self, car_info: CarDownloadInfoDTO) -> tuple[CarAdInfoDTO, SellerInfoDTO] | None:
        if not car_info.href:
            return None

        logger.info(f"Getting adds from: {car_info.href}")
        with self._page(car_info.href) as page:
            page.wait_for_selector(MAIN_AD_READY, timeout=WAIT_STD)
            human_scroll_to_bottom(page)
            ad_details = page.locator("main ul >> li")
            items = ad_details.all_inner_texts()
            ad_info = self.extract_ad_info(items)

            ad_images = page.query_selector_all(AD_IMAGES)
            ad_info.ad_images_links = []
            for image_src in [img.get_attribute("src") for img in ad_images]:
                ad_info.ad_images_links.append(image_src)

            basicInformation = page.locator("#VehicleBasicInformationTitle")
            ad_info.name = basicInformation.text_content()
            ad_info.desc = page.locator("#VehicleBasicInformationDescription").text_content()

            price_selector = page.locator("#vehicleSendProposalPrice")
            price_text = price_selector.text_content()

            if price_text:
                cleaned = (
                    price_text.replace("R$", "")
                    .replace(".", "")
                    .replace(",", ".")
                    .strip()
                )
                try:
                    ad_info.price = float(cleaned)
                except ValueError:
                    ad_info.price = None
            else:
                ad_info.price = None

            ad_info.ad_link = car_info.href
            ad_info.qty_images = len(ad_info.ad_images_links) + 1
            ad_info.brand_id = car_info.brand_id
            ad_info.job_id = car_info.job_id
            ad_info.created_at = my_time_now()
            ad_info.updated_at = my_time_now()

            seller = self.get_seller_info(page)
            logger.info(f"{ad_info}")

            return ad_info, seller
