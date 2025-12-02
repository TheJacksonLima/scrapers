from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from car_scraper.db.entity.seller_info import SellerInfo


@dataclass
class SellerInfoDTO:
    id: Optional[int] = None
    name: str = ""
    location: Optional[str] = None
    phone: Optional[str] = None
    contact_code: Optional[str] = None
    stock_url: Optional[str] = None
    job_id: int = 0
    is_private: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __str__(self):
        return f"SellerInfoDTO: {self.to_dict()}"

    @staticmethod
    def to_dto(entity: SellerInfo) -> "SellerInfoDTO":
        return SellerInfoDTO(
            id=entity.id,
            name=entity.name,
            location=entity.location,
            phone=entity.phone,
            contact_code=entity.contact_code,
            stock_url=entity.stock_url,
            job_id=entity.job_id,
            is_private=entity.is_private,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def from_entity_list(entities: list[SellerInfo]) -> list["SellerInfoDTO"]:
        return [SellerInfoDTO.to_dto(e) for e in entities]

    @staticmethod
    def to_entity(dto: "SellerInfoDTO") -> SellerInfo:
        return SellerInfo(
            id=dto.id,
            name=dto.name,
            location=dto.location,
            phone=dto.phone,
            contact_code=dto.contact_code,
            stock_url=dto.stock_url,
            job_id=dto.job_id,
            is_private=dto.is_private,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "phone": self.phone,
            "contact_code": self.contact_code,
            "stock_url": self.stock_url,
            "job_id": self.job_id,
            "is_private": self.is_private,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
