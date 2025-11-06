from typing import Optional
from dataclasses import dataclass
from car_scraper.db.entity.brand import Brand


@dataclass
class BrandDTO:
    id: int
    name: str
    href: Optional[str] = None
    source: str = "unknown"
    total_ads: int = 0

    def __str__(self):
        return f"Brand:  {self.id} {self.name} (source:{self.source}) - (total_ads:{self.total_ads})"

    @staticmethod
    def to_dto(entity: Brand) -> "BrandDTO":
        return BrandDTO(
            id=entity.id,
            name=entity.name,
            href=entity.url,
            source=entity.source,
            total_ads=entity.total_ads
        )

    @staticmethod
    def to_entity(dto: "BrandDTO") -> Brand:
        return Brand(
            id=dto.id,
            name=dto.name,
            source=dto.source,
            url=dto.href,
            total_ads=dto.total_ads
        )

    @staticmethod
    def get_entity(self) -> Brand:
        return Brand(
            id=self.id,
            name=self.name,
            source=self.source,
            url=self.href,
            total_ads=self.total_ads
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "url": self.href,
            "total_ads": self.total_ads
        }
