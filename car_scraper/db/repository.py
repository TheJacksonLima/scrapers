import logging
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from car_scraper.db.models import CarDownloadInfo
from car_scraper.db.models.brand import Brand
from car_scraper.scrapers.scraper import BrandDTO
from car_scraper.utils.human import show_sql

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_brands(self, source: str) -> List[Brand]:
        stmt = select(Brand).where(Brand.source == source)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_source_and_name(self, source: str, name: str) -> Brand | None:
        stmt = select(Brand).where(Brand.name == name, Brand.source == source)
        return self.db.execute(stmt).scalar_one_or_none()

    def save(self, dto: BrandDTO) -> Brand:
        brand = self.get_by_source_and_name(dto.name, dto.source)
        if brand is None:
            brand = Brand(
                name=dto.name,
                source=dto.source,
                url=dto.href,
            )
            self.db.add(brand)
        else:
            brand.url = dto.href
        return brand

    def update_total_ads(self, brand_input: BrandDTO, total_ads: int) -> Optional[Brand]:
        brand = self.get_by_source_and_name(brand_input.source, brand_input.name)
        if brand:
            brand.total_ads = total_ads
            self.db.add(brand)
            self.db.commit()
            self.db.refresh(brand)
            return brand
        return None

    def get_car_download_info_by_href(self, href: str):
        stmt = select(CarDownloadInfo).where(CarDownloadInfo.href == href)
        return self.db.execute(stmt).scalar_one_or_none()

    def save_car_download_info(self, car_download_info: CarDownloadInfo):
        existing = self.get_car_download_info_by_href(car_download_info.href)
        #logger.info(f"Found: {existing}")
        if existing:
            changed = False
            if existing.car_desc != car_download_info.car_desc:
                existing.car_desc = car_download_info.car_desc
                changed = True
            if existing.image != car_download_info.image:
                existing.image = car_download_info.image
                changed = True
            if existing.brand_id != car_download_info.brand_id:
                existing.brand_id = car_download_info.brand_id
                changed = True

            if changed:
                self.db.add(existing)
                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Updated existing ad: {existing.href}")
            #else:
                #logger.info(f"No changes detected for car_download_info: {existing.href}")

            return existing

        self.db.add(car_download_info)
        self.db.commit()
        self.db.refresh(car_download_info)
        logger.info(f"Inserted new car_download_info: {car_download_info.href}")
        return car_download_info
