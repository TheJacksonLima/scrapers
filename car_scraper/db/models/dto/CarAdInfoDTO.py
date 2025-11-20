from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from car_scraper.db.entity.car_ad_info import CarAdInfo


@dataclass
class CarAdInfoDTO:
    id: Optional[int] = None
    ad_link: str = ""
    name: Optional[str] = None
    desc: Optional[str] = None
    ad_images_links: List[str] = None
    qty_images: Optional[int] = None
    city: str = ""
    year: Optional[int] = None
    km: Optional[int] = None
    transmission: Optional[str] = None
    type: str = ""
    color: str = ""
    trade_in: bool = False
    status: bool = False
    ipva: bool = False
    license: bool = False
    items: List[str] = None
    seller_id: Optional[int] = None

    brand_id: int = 0
    job_id: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return f"{self.to_dict()}"

    @staticmethod
    def to_dto(entity: CarAdInfo) -> "CarAdInfoDTO":
        return CarAdInfoDTO(
            id=entity.id,
            ad_link=entity.ad_link,
            name=entity.name,
            desc=entity.desc,
            ad_images_links=entity.ad_images_links,
            qty_images=entity.qty_images,
            city=entity.city,
            year=entity.year,
            km=entity.km,
            transmission=entity.transmission,
            type=entity.type,
            color=entity.color,
            trade_in=entity.trade_in,
            status=entity.status,
            ipva=entity.ipva,
            license=entity.license,
            items=entity.items,
            brand_id=entity.brand_id,
            job_id=entity.job_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            seller_id=entity.seller_id
        )

    @staticmethod
    def from_entity_list(entities: List[CarAdInfo]) -> List["CarAdInfoDTO"]:
        return [CarAdInfoDTO.from_entity(e) for e in entities]

    @staticmethod
    def to_entity(dto: "CarAdInfoDTO") -> CarAdInfo:
        return CarAdInfo(
            id=dto.id,
            ad_link=dto.ad_link,
            name=dto.name,
            desc=dto.desc,
            ad_images_links=dto.ad_images_links or [],
            qty_images=dto.qty_images,
            city=dto.city,
            year=dto.year,
            km=dto.km,
            transmission=dto.transmission,
            type=dto.type,
            color=dto.color,
            trade_in=dto.trade_in,
            status=dto.status,
            ipva=dto.ipva,
            license=dto.license,
            items=dto.items or [],
            brand_id=dto.brand_id,
            job_id=dto.job_id,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            seller_id=dto.seller_id
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ad_link": self.ad_link,
            "name": self.name,
            "desc": self.desc,
            "ad_images_links": self.ad_images_links,
            "qty_images": self.qty_images,
            "city": self.city,
            "year": self.year,
            "km": self.km,
            "transmission": self.transmission,
            "type": self.type,
            "color": self.color,
            "trade_in": self.trade_in,
            "status": self.status,
            "ipva": self.ipva,
            "license": self.license,
            "items": self.items,
            "brand_id": self.brand_id,
            "job_id": self.job_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
