from typing import List,Optional
from dataclasses import dataclass
from car_scraper.db.models import CarDownloadInfo


@dataclass
class CarDownloadInfoDTO:
    id: Optional[int] = None
    href: str = ""
    car_desc: str = ""
    image: Optional[str] = None
    brand_id: Optional[int] = None

    def __str__(self):
        return f"Car({self.car_desc}) - href: {self.href}, image: {self.image or 'N/A'}"

    @staticmethod
    def to_dto(entity: CarDownloadInfo) -> "CarDownloadInfoDTO":
        return CarDownloadInfoDTO(
            id=entity.id,
            href=entity.href,
            car_desc=entity.car_desc,
            image=entity.image,
            brand_id=entity.brand_id
        )

    @staticmethod
    def to_entity(dto: "CarDownloadInfoDTO") -> CarDownloadInfo:
        return CarDownloadInfo(
            href=dto.href,
            car_desc=dto.car_desc,
            image=dto.image,
            brand_id=dto.brand_id
        )
    @staticmethod
    def from_entity(entity: "CarDownloadInfo") -> "CarDownloadInfoDTO":
        return CarDownloadInfoDTO(
            id=entity.id,
            href=entity.href,
            car_desc=entity.car_desc,
            image=entity.image,
            brand_id=entity.brand_id
        )

    @staticmethod
    def from_entity_list(entities: List["CarDownloadInfo"]) -> List["CarDownloadInfoDTO"]:
        return [CarDownloadInfoDTO.from_entity(e) for e in entities]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "href": self.href,
            "car_desc": self.car_desc,
            "image": self.image,
            "brand_id": self.brand_id,
        }
