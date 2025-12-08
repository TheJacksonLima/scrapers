import logging
from datetime import datetime
from typing import List, Optional, Sequence
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from car_scraper.db.entity import JobDownloadControl, CarDownloadInfo
from car_scraper.db.entity.car_ad_info import CarAdInfo
from car_scraper.db.entity.car_download_info import CarDownloadInfo
from car_scraper.db.entity.brand import Brand
from car_scraper.db.entity.seller_info import SellerInfo
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType
from car_scraper.scrapers.scraper import BrandDTO
from car_scraper.utils.human import show_sql
from sqlalchemy import and_
from car_scraper.utils.my_time_now import my_time_now

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_brands(self, source: JobSource) -> List[Brand]:
        stmt = select(Brand).where(Brand.source == source)
        show_sql(stmt)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_source_and_name(self, source: JobSource, name: str) -> Brand | None:
        stmt = select(Brand).where(Brand.name == name, Brand.source == source)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_batch_by_job_id(self, job_id):
        stmt = select(JobDownloadControl).where(JobDownloadControl.job_id == job_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def update_brand(self, dto: BrandDTO) -> Brand:

        brand = self.get_by_source_and_name(dto.source, dto.name)

        if brand is None:
            brand = Brand(
                name=dto.name,
                source=dto.source,
                url=dto.href,
                icon_url=dto.icon_url,
                total_ads=dto.total_ads,
            )
            self.db.add(brand)
            self.db.commit()
            self.db.refresh(brand)
            logger.info(f"Inserted new brand: {brand.name} ({brand.source})")
            return brand

        changed = False

        if brand.url != dto.href:
            brand.url = dto.href
            changed = True

        if brand.icon_url != dto.icon_url:
            brand.icon_url = dto.icon_url
            changed = True

        if brand.total_ads != dto.total_ads:
            brand.total_ads = dto.total_ads
            changed = True

        if brand.name != dto.name:
            brand.name = dto.name
            changed = True

        if changed:
            self.db.commit()
            self.db.refresh(brand)
            logger.info(f"Updated brand: {brand.name} ({brand.source})")

        return brand

    def update_total_ads(self, brand_input: BrandDTO, total_ads: int, qty_ads: int) -> Optional[Brand]:
        brand = self.get_by_source_and_name(brand_input.source, brand_input.name)
        if brand:
            brand.total_ads = total_ads
            brand.qty_ads = qty_ads
            self.db.add(brand)
            self.db.commit()
            self.db.refresh(brand)
            return brand
        return None

    def get_car_download_info_by_href(self, href: str):
        stmt = select(CarDownloadInfo).where(CarDownloadInfo.href == href)
        return self.db.execute(stmt).scalar_one_or_none()

    def update_car_download_info(self, car_download_info: CarDownloadInfo):
        existing = self.get_car_download_info_by_href(car_download_info.href)
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

            if existing.status != car_download_info.status:
                existing.status = car_download_info.status
                changed = True

            if changed:
                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Updated existing ad: {existing.href}")

            return existing

        self.db.add(car_download_info)
        self.db.commit()
        self.db.refresh(car_download_info)
        logger.info(f"Inserted new car_download_info: {car_download_info.href}")
        return car_download_info

    def create_batch(self, batch: JobDownloadControl):
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return self.get_batch_by_job_id(batch.job_id)

    def update_batch(self, batch: JobDownloadControl) -> JobDownloadControl | None:
        existing_batch = self.get_batch_by_job_id(batch.job_id)
        if existing_batch:
            existing_batch.status = batch.status
            existing_batch.error_message = batch.error_message
            existing_batch.last_page = batch.last_page
            existing_batch.total_pages = batch.total_pages
            existing_batch.attempts = batch.attempts

            if batch.status == JobStatus.COMPLETED:
                existing_batch.finished_at = datetime.now()

            self.db.commit()
            self.db.refresh(existing_batch)
            logger.info(f"Updated batch id: {existing_batch.job_id}")
            return existing_batch
        return None

    def get_last_batch(self, brand: Brand, job_type: JobType) -> JobDownloadControl | None:
        stmt = (
            select(JobDownloadControl)
            .where(
                JobDownloadControl.brand_id == brand.id,
                JobDownloadControl.job_type == job_type
            )
            .order_by(JobDownloadControl.created_at.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_car_ads(self, max_ads: int, status: JobStatus) -> List[CarDownloadInfo]:
        stmt = (
            select(CarDownloadInfo)
            .where(
                CarDownloadInfo.status == status
            )
            .order_by(CarDownloadInfo.created_at.asc())
            .limit(max_ads)
        )
        #show_sql(stmt)
        return self.db.execute(stmt).scalars().all()

    def get_count(self, status) -> int | None:
        stmt = (
            select(func.count(CarDownloadInfo.id))
            .where(
                CarDownloadInfo.status == status
            )
        )
        return self.db.execute(stmt).scalar_one()

    def get_ad_by_link(self, ad_info: CarAdInfo) -> CarAdInfo | None:
        stmt = select(CarAdInfo).where(CarAdInfo.ad_link == ad_info.ad_link)
        return self.db.execute(stmt).scalar_one_or_none()

    def save_or_update_car_ad_info(self, ad_info: CarAdInfo) -> CarAdInfo | None:
        existing_ad = self.get_ad_by_link(ad_info)
        if existing_ad:
            existing_ad.name = ad_info.name
            existing_ad.desc = ad_info.desc
            existing_ad.ad_images_links = ad_info.ad_images_links or []
            existing_ad.qty_images = ad_info.qty_images
            existing_ad.city = ad_info.city
            existing_ad.year = ad_info.year
            existing_ad.km = ad_info.km
            existing_ad.price = ad_info.price
            existing_ad.transmission = ad_info.transmission
            existing_ad.type = ad_info.type
            existing_ad.color = ad_info.color
            existing_ad.trade_in = ad_info.trade_in
            existing_ad.status = ad_info.status
            existing_ad.ipva = ad_info.ipva
            existing_ad.license = ad_info.license
            existing_ad.items = ad_info.items or []
            existing_ad.brand_id = ad_info.brand_id
            existing_ad.job_id = ad_info.job_id
            existing_ad.updated_at = ad_info.updated_at or my_time_now()

            if ad_info.seller_id is not None:
                existing_ad.seller_id = ad_info.seller_id

            self.db.commit()
            self.db.refresh(existing_ad)
            return self.get_ad_by_link(existing_ad)

        else:
            ad_info.created_at = ad_info.created_at or my_time_now()
            ad_info.updated_at = ad_info.updated_at or my_time_now()

            self.db.add(ad_info)
            self.db.commit()
            self.db.refresh(ad_info)
            logger.info(f"Inserted new ad with batch id: {ad_info.job_id}")
            return self.get_ad_by_link(ad_info)

    def get_seller_by_name_and_location(self, seller) -> SellerInfo | None:
        stmt = (
            select(SellerInfo)
            .where(
                SellerInfo.name == seller.name,
                SellerInfo.location == seller.location
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def save_or_update_seller(self, seller: SellerInfo) -> SellerInfo:
        existing_seller = self.get_seller_by_name_and_location(seller)

        if existing_seller:
            existing_seller.phone = seller.phone
            existing_seller.contact_code = seller.contact_code
            existing_seller.stock_url = seller.stock_url
            existing_seller.job_id = seller.job_id
            existing_seller.updated_at = seller.updated_at or my_time_now()

            self.db.commit()
            self.db.refresh(existing_seller)
            return self.get_seller_by_name_and_location(existing_seller)

        else:
            seller.created_at = seller.created_at or my_time_now()
            seller.updated_at = seller.updated_at or my_time_now()

            self.db.add(seller)
            self.db.commit()
            self.db.refresh(seller)
            return self.get_seller_by_name_and_location(seller)
