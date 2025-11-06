from typing import List,Optional
from dataclasses import dataclass
from car_scraper.db.entity import CarDownloadInfo
from car_scraper.db.models.enums.JobStatus import JobStatus


@dataclass
class CarDownloadInfoDTO:
    job_id: int = 0
    href: str = ""
    page: int = 0
    car_desc: str = ""
    status: JobStatus = JobStatus.PENDING
    image: Optional[str] = None
    brand_id: Optional[int] = None


    def __str__(self):
        return f"Car({self.car_desc}) - href: {self.href}, image: {self.image or 'N/A'}"

    @staticmethod
    def to_dto(entity: CarDownloadInfo) -> "CarDownloadInfoDTO":
        return CarDownloadInfoDTO(
            job_id=entity.job_id,
            href=entity.href,
            page=entity.page,
            car_desc=entity.car_desc,
            image=entity.image,
            brand_id=entity.brand_id,
            status=entity.status
        )

    @staticmethod
    def to_entity(dto: "CarDownloadInfoDTO") -> CarDownloadInfo:
        return CarDownloadInfo(
            job_id=dto.job_id,
            href=dto.href,
            page=dto.page,
            car_desc=dto.car_desc,
            image=dto.image,
            brand_id=dto.brand_id,
            status=dto.status

        )
    @staticmethod
    def from_entity(entity: "CarDownloadInfo") -> "CarDownloadInfoDTO":
        return CarDownloadInfoDTO(
            job_id=entity.job_id,
            href=entity.href,
            page=entity.page,
            car_desc=entity.car_desc,
            image=entity.image,
            brand_id=entity.brand_id,
            status = entity.status
        )

    @staticmethod
    def from_entity_list(entities: List["CarDownloadInfo"]) -> List["CarDownloadInfoDTO"]:
        return [CarDownloadInfoDTO.from_entity(e) for e in entities]

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "href": self.href,
            "page": self.page,
            "car_desc": self.car_desc,
            "image": self.image,
            "brand_id": self.brand_id,
            "status": self.status,
        }
