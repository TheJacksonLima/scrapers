import math
from typing import List

from car_scraper.db.entity import JobDownloadControl
from car_scraper.db.models.dto.JobDownloadControlDTO import JobDownloadControlDTO
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType
from car_scraper.db.repository import Repository
from car_scraper.db.entity.brand import Brand
from car_scraper.db.models.dto.CarDownloadInfoDTO import CarDownloadInfoDTO
from car_scraper.db.session import SessionLocal
from car_scraper.db.models.dto.BradDTO import BrandDTO


class Service:
    @staticmethod
    def get_all_brands(source: str) -> List[BrandDTO]:
        with SessionLocal() as db:
            repo = Repository(db)
            return [BrandDTO.to_dto(b) for b in repo.get_all_brands(source)]

    @staticmethod
    def get_brand_url(name: str, source: str) -> BrandDTO | None:
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
    def update_ads(brand: BrandDTO, total_ads: int):
        with SessionLocal() as db:
            repo = Repository(db)
            repo.update_total_ads(brand, total_ads)
            db.commit()
        return repo.get_by_source_and_name(brand.source, brand.name)

    @staticmethod
    def save_car_download_info(list_car_ads_dto: List[CarDownloadInfoDTO]):
        with SessionLocal() as db:
            repo = Repository(db)
            for dto in list_car_ads_dto:
                entity = CarDownloadInfoDTO.to_entity(dto)
                repo.save_car_download_info(entity)
            db.commit()

    @staticmethod
    def create_batch(brand: BrandDTO, job_type: JobType) -> JobDownloadControlDTO:
        batch = JobDownloadControl(
            job_type=job_type.value,
            source_name=brand.source,
            status=JobStatus.PENDING,
            error_message="",
            last_page=0,
            total_pages=math.ceil(brand.total_ads / 47),
            attempts=0
        )

        with SessionLocal() as db:
            repo = Repository(db)
            ret = repo.create_batch(batch)
            db.commit()
            return JobDownloadControlDTO.from_entity(ret)

    @staticmethod
    def update_batch(batch: JobDownloadControlDTO) -> JobDownloadControlDTO:
        with SessionLocal() as db:
            repo = Repository(db)
            ret = repo.update_batch(batch.to_entity())
            db.commit()
            return JobDownloadControlDTO.from_entity(ret)
