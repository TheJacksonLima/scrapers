import math
from functools import singledispatchmethod
from typing import List
from datetime import datetime
from car_scraper.db.entity import JobDownloadControl
from car_scraper.db.entity.brand import Brand
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.dto.CarDownloadInfoDTO import CarDownloadInfoDTO
from car_scraper.db.models.dto.JobDownloadControlDTO import JobDownloadControlDTO
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType
from car_scraper.db.repository import Repository
from car_scraper.db.session import SessionLocal


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
    def save_car_download_info(list_car_ads_dto: List[CarDownloadInfoDTO]) -> List[CarDownloadInfoDTO]:
        with SessionLocal() as db:
            repo = Repository(db)
            list_car_ads_dto_out = []
            for dto in list_car_ads_dto:
                entity = CarDownloadInfoDTO.to_entity(dto)
                repo.save_car_download_info(entity)
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
            source_name=JobSource.WEBMOTORS,#brand.source,
            status=JobStatus.PENDING,
            error_message="",
            updated_at=datetime.now(),
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
    def _(self, source: str, job_type: JobType) -> JobDownloadControlDTO:
        batch = JobDownloadControl(
            job_type=job_type.value,
            source_name=source,
            status=JobStatus.PENDING,
            error_message="",
            last_page=1,
            total_pages=0,
            attempts=0
        )

        with SessionLocal() as db:
            repo = Repository(db)
            ret = repo.create_batch(batch)
            db.commit()
            return JobDownloadControlDTO.to_dto(ret)
