from typing import List, Optional
from car_scraper.db.session import SessionLocal
from car_scraper.db.models import Brand
from car_scraper.db.brand_repository import BrandRepository
from car_scraper.scrapers import BrandDTO


class BrandService:
    @staticmethod
    def to_dto(entity: Brand) -> BrandDTO:
        return BrandDTO(
            name=entity.name,
            href=entity.url,
            source=entity.source
        )

    @staticmethod
    def to_entity(dto: BrandDTO) -> Brand:
        return Brand(
            name=dto.name,
            source=dto.source,
            url=dto.href
        )

    def get_all_brands(self, source: str) -> List[BrandDTO]:
        with SessionLocal() as db:
            repo = BrandRepository(db)
            return [self.to_dto(b) for b in repo.get_all_brands(source)]

    def get_brand_url(self, name: str, source: str) -> BrandDTO | None:
        with SessionLocal() as db:
            repo = BrandRepository(db)
            return self.to_dto(repo.get_by_name_and_source(name, source))

    def save_brands(self, brand_dtos: List[BrandDTO]) -> List[Brand]:
        with SessionLocal() as db:
            repo = BrandRepository(db)
            saved: List[Brand] = []
            for dto in brand_dtos:
                brand = repo.save(dto)  # upsert no repository
                saved.append(brand)
            db.commit()
            return saved
