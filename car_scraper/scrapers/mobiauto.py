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
from car_scraper.scrapers import BaseScraper
from car_scraper.utils.config import settings, PROJECT_ROOT

logger = logging.getLogger(__name__)
tmp_dir = PROJECT_ROOT / "tmp"

BASE = settings.MOBIAUTO_URL
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


class MobiAuto_Scrapper(BaseScraper):
    def get_cars_from_brand(self, brand: BrandDTO) -> list[CarDownloadInfoDTO] | Optional[dict]:
        pass

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
            slug = self.slugify(name)
            total_ads = 0

            href = f"{settings.MOBIAUTO_URL}/comprar/brasil/{slug}"

            brand = BrandDTO(
                id=idx,
                name=name,
                href=href,
                total_ads=total_ads,
                source=JobSource.MOBIAUTO
            )

            brands.append(brand)

        logger.info(f"Found {len(brands)} brands on Mobiauto")
        return brands

    def get_build_id(self, href: str) -> str:
        html = requests.get(href, headers=HEADERS).text
        return re.search(r'"buildId":"(.*?)"', html).group(1)

    def get_cars_from_brand_test(self, brand: BrandDTO, job_id: int, page_num: int) -> list[CarDownloadInfoDTO] | \
                                                                                       Optional[dict]:
        #html = requests.get("https://www.mobiauto.com.br/comprar/brasil/audi", headers=HEADERS).text
        build_id = self.get_build_id(brand.href)

        logger.debug("Build ID:", build_id)

        if page_num == 1:
            url = f"{BASE}/comprar/_next/data/{build_id}/carros/brasil/{brand.name}.json"
        else:
            url = f"{BASE}/comprar/_next/data/{build_id}/carros/brasil/{brand.name}/{page_num}.json"

        params = {
            "params": ["carros", "brasil", "\"" + {brand.name} + "\""],
            "page": page_num
        }

        logger.info(f"Getting adds from: {url}")
        resp = requests.get(url, headers=HEADERS, params=params)

        logger.info("Status:", resp.status_code)

        return resp.json()
