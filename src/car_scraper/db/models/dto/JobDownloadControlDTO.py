from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
from car_scraper.db.entity import JobDownloadControl
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType
from car_scraper.db.models.enums.JobSource import JobSource


@dataclass
class JobDownloadControlDTO:
    job_id: Optional[int] = None
    job_type: Optional[JobType] = None
    source_name: Optional[JobSource] = None
    status: Optional[JobStatus] = None
    brand_id: int = 0
    error_message: str = ""
    last_page: int = 1
    total_pages: int = 0
    attempts: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    def __str__(self):
        return f"JobDownloadControlDTO: {self.to_dict()}"

    @staticmethod
    def to_dto(entity: JobDownloadControl) -> "JobDownloadControlDTO":
        return JobDownloadControlDTO(
            job_id=entity.job_id,
            job_type=entity.job_type,
            source_name=entity.source_name,
            brand_id=entity.brand_id,
            status=entity.status,
            error_message=entity.error_message,
            last_page=entity.last_page,
            total_pages=entity.total_pages,
            attempts=entity.attempts,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            started_at=entity.started_at,
            finished_at=entity.finished_at
        )

    @staticmethod
    def from_entity_list(entities: List[JobDownloadControl]) -> List["JobDownloadControlDTO"]:
        return [JobDownloadControlDTO.to_dto(e) for e in entities]

    @staticmethod
    def to_entity(dto : "JobDownloadControlDTO") -> JobDownloadControl:
        return JobDownloadControl(
            job_id=dto.job_id,
            job_type=dto.job_type,
            source_name=dto.source_name,
            brand_id=dto.brand_id,
            status=dto.status,
            error_message=dto.error_message,
            last_page=dto.last_page,
            total_pages=dto.total_pages,
            attempts=dto.attempts,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            started_at=dto.started_at,
            finished_at=dto.finished_at
        )

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "job_type": self.job_type.name if self.job_type else None,
            "source_name": self.source_name.name if self.source_name else None,
            "status": self.status.name if self.status else None,
            "brand_id": self.brand_id,
            "error_message": self.error_message,
            "last_page": self.last_page,
            "total_pages": self.total_pages,
            "attempts": self.attempts,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
