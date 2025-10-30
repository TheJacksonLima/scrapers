from typing import List

from car_scraper.db.repository import Repository
from car_scraper.db.models.brand import Brand
from car_scraper.db.models.dto.CarDownloadInfoDTO import CarDownloadInfoDTO
from car_scraper.db.session import SessionLocal
from car_scraper.db.models.dto.BradDTO import BrandDTO


class Service:
    def get_all_brands(self, source: str) -> List[BrandDTO]:
        with SessionLocal() as db:
            repo = Repository(db)
            return [BrandDTO.to_dto(b) for b in repo.get_all_brands(source)]

    def get_brand_url(self, name: str, source: str) -> BrandDTO | None:
        with SessionLocal() as db:
            repo = Repository(db)
            return BrandDTO.to_dto(repo.get_by_source_and_name(name, source))

    def get_ads_from_brand(self, brand_dto: BrandDTO):
        with SessionLocal() as db:
            repo = Repository(db)
            return BrandDTO.to_dto(repo.get_ads_from_brand(brand_dto.get_entity()))

    def save_brands(self, brand_dtos: List[BrandDTO]) -> List[Brand]:
        with SessionLocal() as db:
            repo = Repository(db)
            saved: List[Brand] = []
            for dto in brand_dtos:
                brand = repo.save(dto)
                saved.append(brand)
            db.commit()
            return saved

    def update_ads(self, brand: BrandDTO, total_ads: int):
        with SessionLocal() as db:
            repo = Repository(db)
            repo.update_total_ads(brand,total_ads)
            db.commit()
        return repo.get_by_source_and_name(brand.source, brand.name)

    def save_car_download_info(self,list_car_ads_dto: List[CarDownloadInfoDTO]):
        with SessionLocal() as db:
            repo = Repository(db)
            for dto in list_car_ads_dto:
                entity = CarDownloadInfoDTO.to_entity(dto)
                repo.save_car_download_info(entity)
            db.commit()


