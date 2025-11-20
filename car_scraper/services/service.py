import math
from functools import singledispatchmethod
from typing import List, Tuple
from datetime import datetime
from car_scraper.db.entity import JobDownloadControl
from car_scraper.db.entity.brand import Brand
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.dto.CarAdInfoDTO import CarAdInfoDTO
from car_scraper.db.models.dto.CarDownloadInfoDTO import CarDownloadInfoDTO
from car_scraper.db.models.dto.JobDownloadControlDTO import JobDownloadControlDTO
from car_scraper.db.models.dto.SellerInfoDTO import SellerInfoDTO
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType
from car_scraper.db.repository import Repository
from car_scraper.db.session import SessionLocal
from car_scraper.utils.my_time_now import my_time_now
from car_scraper.utils.config import settings


class Service:
    @staticmethod
    def get_all_brands(source: str) -> List[BrandDTO]:
        with SessionLocal() as db:
            repo = Repository(db)
            return [BrandDTO.to_dto(b) for b in repo.get_all_brands(source)]

    @staticmethod
    def get_brand(name: str, source: str) -> BrandDTO | None:
        with SessionLocal() as db:
            repo = Repository(db)
            return BrandDTO.to_dto(repo.get_by_source_and_name(name, source))

    @staticmethod
    def get_ads_from_brand(brand_dto: BrandDTO):
        with SessionLocal() as db:
            repo = Repository(db)
            return BrandDTO.to_dto(repo.get_ads_from_brand(brand_dto.get_entity()))

    @staticmethod
    def get_ads_to_download() -> List[CarDownloadInfoDTO]:
        with SessionLocal() as db:
            repo = Repository(db)
            ret = repo.get_car_ads(settings.MAX_ADS_TO_PROCESS)
            return CarDownloadInfoDTO.from_entity_list(ret)

    @staticmethod
    def save_brands(brand_dtos: List[BrandDTO]) -> List[Brand]:
        with SessionLocal() as db:
            repo = Repository(db)
            saved: List[Brand] = []
            for dto in brand_dtos:
                brand = repo.save(dto)
                saved.append(brand)
            db.commit()
            return saved

    @staticmethod
    def update_ads(brand: BrandDTO, total_ads: int) -> BrandDTO:
        with SessionLocal() as db:
            repo = Repository(db)
            repo.update_total_ads(brand, total_ads)
            db.commit()
            ret = repo.get_by_source_and_name(brand.source, brand.name)
            return BrandDTO.to_dto(ret)

    @staticmethod
    def update_car_download_info(dto: CarDownloadInfoDTO) -> CarDownloadInfoDTO:
        with SessionLocal() as db:
            repo = Repository(db)
            entity = CarDownloadInfoDTO.to_entity(dto)
            ret = repo.update_car_download_info(entity)
            db.commit()
            return ret

    @staticmethod
    def update_list_car_download_info(list_car_ads_dto: List[CarDownloadInfoDTO]) -> List[CarDownloadInfoDTO]:
        with SessionLocal() as db:
            repo = Repository(db)
            list_car_ads_dto_out = []
            for dto in list_car_ads_dto:
                entity = CarDownloadInfoDTO.to_entity(dto)
                repo.update_car_download_info(entity)
                list_car_ads_dto_out.append(CarDownloadInfoDTO.to_dto(entity))

            db.commit()
            return list_car_ads_dto_out

    @staticmethod
    def get_last_batch_from_brand(brand: BrandDTO, job_type: JobType) -> JobDownloadControlDTO | None:
        with SessionLocal() as db:
            repo = Repository(db)
            ret = repo.get_last_batch(BrandDTO.to_entity(brand), job_type)
            db.commit()
            return None if ret is None else JobDownloadControlDTO.to_dto(ret)

    @staticmethod
    def update_batch(batch: JobDownloadControlDTO) -> JobDownloadControlDTO:
        update = JobDownloadControlDTO.to_entity(batch)
        with SessionLocal() as db:
            repo = Repository(db)
            ret = repo.update_batch(update)
            db.commit()
            return JobDownloadControlDTO.to_dto(ret)

    @singledispatchmethod
    def create_batch(self, arg, job_type: JobType) -> JobDownloadControlDTO:
        raise NotImplementedError("Type not supported")

    @create_batch.register
    def _(self, brand: BrandDTO, job_type: JobType) -> JobDownloadControlDTO:
        batch = JobDownloadControl(
            job_type=job_type.value,
            source_name=JobSource.WEBMOTORS,
            status=JobStatus.PENDING,
            error_message="",
            updated_at=my_time_now(),
            last_page=1,
            total_pages=math.ceil(brand.total_ads / 47),
            attempts=0,
            brand_id=brand.id
        )

        with SessionLocal() as db:
            repo = Repository(db)
            ret = repo.create_batch(batch)
            db.commit()
            return JobDownloadControlDTO.to_dto(ret)

    @create_batch.register
    def _(self, source: JobSource, job_type: JobType) -> JobDownloadControlDTO:
        batch = JobDownloadControl(
            job_type=job_type.value,
            source_name=source,
            status=JobStatus.PENDING,
            error_message="",
            updated_at=my_time_now(),
            last_page=1,
            total_pages=0,
            attempts=0
        )

        with SessionLocal() as db:
            repo = Repository(db)
            ret = repo.create_batch(batch)
            db.commit()
            return JobDownloadControlDTO.to_dto(ret)

    @staticmethod
    def save_or_update_ads_and_sellers(l_ads_and_sellers: List[Tuple[CarAdInfoDTO, SellerInfoDTO]]) -> List[Tuple[CarAdInfoDTO, SellerInfoDTO]]:
        with SessionLocal() as db:
            repo = Repository(db)
            l_ads_and_sellers_out = []
            for ad_info_dto, seller_dto in l_ads_and_sellers:
                seller_entity = SellerInfoDTO.to_entity(seller_dto)
                seller_saved = repo.save_or_update_seller(seller_entity)

                ad_info_entity = CarAdInfoDTO.to_entity(ad_info_dto)
                ad_info_entity.seller_id = seller_saved.id
                ad_saved = repo.save_or_update_car_ad_info(ad_info_entity)

                l_ads_and_sellers_out.append((CarAdInfoDTO.to_dto(ad_saved), SellerInfoDTO.to_dto(seller_saved)))

            db.commit()
            return l_ads_and_sellers_out
