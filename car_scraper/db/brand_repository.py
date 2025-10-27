from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from car_scraper.db.models.brand import Brand
from car_scraper.scrapers.scraper import BrandDTO


class BrandRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_brands(self,  source: str) -> List[Brand]:
        stmt = select(Brand).where(Brand.source == source)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_name_and_source(self, source: str, name: str) -> Brand | None:
        stmt = select(Brand).where(Brand.name == name, Brand.source == source)
        return self.db.execute(stmt).scalar_one_or_none()

    def save(self, dto: BrandDTO) -> Brand:
        brand = self.get_by_name_and_source(dto.name, dto.source)
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

    def update_total_ads(self, name: str, source: str, total_ads: int) -> Optional[Brand]:
        brand = self.get_by_name_and_source(source, name)
        if brand:
            brand.total_ads = total_ads
            self.db.add(brand)
            self.db.commit()
            self.db.refresh(brand)
            return brand
        return None