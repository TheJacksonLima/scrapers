import logging
from abc import ABC
from typing import List, Optional

import unicodedata, re
import requests
import re
import json
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.dto.CarDownloadInfoDTO import CarDownloadInfoDTO
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.scrapers import BaseScraper
from car_scraper.utils.config import settings, PROJECT_ROOT

logger = logging.getLogger(__name__)
tmp_dir = PROJECT_ROOT / "tmp"

BASE = settings.MOBIAUTO_URL
IMAGE_BASE = "https://image1.mobiauto.com.br/images/api/images/v1.0/"
IMAGE_BASE_SUFIX = "/transform/fl_progressive,f_webp,q_100,w_72"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


class MobiAuto_Scrapper(BaseScraper):
    ADS_PER_PAGE = 24

    @staticmethod
    def slugify(text):
        text = text.lower()
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')

    def build_mobiauto_ad_url(self, deal) -> str:
        d = deal["deal"]

        state = self.slugify(d["dealer"]["location"]["state"])
        city = self.slugify(d["dealer"]["location"]["city"])
        make = self.slugify(d["trim"]["make"]["name"])
        model = self.slugify(d["trim"]["model"]["name"])
        year = d["trim"]["productionYear"]
        trim = self.slugify(d["trim"]["name"])
        car_id = d["id"]

        return (
            f"`{BASE}/comprar/carros/"
            f"{state}-{city}/{make}/{model}/{year}/{trim}/detalhes/{car_id}?page=detail"
        )

    def get_brands(self) -> List[BrandDTO]:
        logger.info("Getting brand links and names")

        brands: List[BrandDTO] = []
        list_page = f"{BASE}/comprar/carros-usados/brasil"
        build_id = self.get_build_id(list_page)
        logger.debug(f"Build ID: {build_id}")

        url = (
            f"{BASE}/comprar/_next/data/{build_id}/carros-usados/brasil.json"
            f"?params=carros-usados&params=brasil"
        )

        logger.info(f"Fetching brands from: {url}")
        resp = requests.get(url, headers=HEADERS)

        if resp.status_code != 200:
            logger.error(f"Failed to fetch brand list: {resp.status_code}")
            return brands

        data = resp.json()

        try:
            makes = data.get("pageProps", {}).get("makes", [])
        except Exception as e:
            logger.exception("Error parsing brand list JSON")
            return brands

        for idx, item in enumerate(makes, start=1):
            name = item.get("name")
            icon_url = IMAGE_BASE + str(item.get("imageId")) + IMAGE_BASE_SUFIX
            slug = self.slugify(name)
            total_ads = 0

            href = f"{settings.MOBIAUTO_URL}/comprar/carros/brasil/{slug}"

            brand = BrandDTO(
                id=idx,
                name=name,
                href=href,
                icon_url=icon_url,
                total_ads=total_ads,
                source=JobSource.MOBIAUTO
            )

            brands.append(brand)

        logger.info(f"Found {len(brands)} brands on Mobiauto")
        return brands

    def get_build_id(self, href: str) -> str:
        html = requests.get(href, headers=HEADERS).text
        return re.search(r'"buildId":"(.*?)"', html).group(1)

    def get_total_ads(self, brand: BrandDTO) -> Optional[int]:

        build_id = self.get_build_id(brand.href)
        slug = brand.name.lower().replace(" ", "-")


        json_url = f"{BASE}/comprar/_next/data/{build_id}/carros/brasil/{slug}.json"

        logger.info(f"Fetching total ads from: {json_url}")

        resp = requests.get(json_url, headers=HEADERS)

        if resp.status_code != 200:
            logger.error(f"Error fetching total ads JSON: {resp.status_code}")
            return 0

        try:
            data = resp.json()
        except Exception as e:
            logger.exception("Could not decode JSON for brand")
            return 0

        try:
            total_ads = (
                data.get("pageProps", {})
                .get("deals", {})
                .get("numResults", 0)
            )
        except Exception as e:
            logger.exception("Error parsing total ads JSON")
            return 0

        logger.info(f"Total ads available for {brand.name}: {total_ads}")
        return total_ads

    def get_cars_from_brand(self, brand: BrandDTO, job_id: int, page_num: int) -> list[CarDownloadInfoDTO]:
        build_id = self.get_build_id(brand.href)

        if page_num == 1:
            url = f"{BASE}/comprar/_next/data/{build_id}/carros/brasil/{brand.name}.json"
        else:
            url = f"{BASE}/comprar/_next/data/{build_id}/carros/brasil/{brand.name}/{page_num}.json"

        logger.info(f"Getting ads from Mobiauto: {url}")

        resp = requests.get(url, headers=HEADERS)

        if resp.status_code != 200:
            logger.error(f"Error fetching ads list: HTTP {resp.status_code}")
            return []

        data = resp.json()

        deals = data.get("pageProps", {}).get("dealsWithAds", [])

        results: list[CarDownloadInfoDTO] = []

        for item in deals:
            deal = item.get("deal")
            if not deal:
                continue

            deal_id = deal["id"]

            href = f"https://www.mobiauto.com.br/anuncio/{deal_id}"

            trim = deal.get("trim", {})
            make = trim.get("make", {}).get("name", "")
            model = trim.get("model", {}).get("name", "")
            version = trim.get("name", "")
            year = trim.get("productionYear", "")

            car_desc = f"{make} {model} {version} {year}".strip()

            images = deal.get("images", [])
            image_url = None
            if images:
                img_id = images[0]["imageId"]
                image_url = f"https://cdn.mobiauto.com.br/{img_id}"

            dto = CarDownloadInfoDTO(
                href=href,
                car_desc=car_desc,
                image=image_url,
                brand_id=brand.id,
                job_id=job_id,
                status=JobStatus.PENDING,
                page=page_num
            )

            results.append(dto)

        return results
