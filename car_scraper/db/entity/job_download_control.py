from datetime import datetime

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy import Integer, String, Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from car_scraper.db.entity.base import Base
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType


class JobDownloadControl(Base):
    __tablename__ = "job_download_control"

    job_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_type: Mapped[JobType] = mapped_column(PgEnum(JobType), nullable=False, default="")
    source_name: Mapped[JobSource] = mapped_column(PgEnum(JobSource), nullable=False, default="")
    status: Mapped[JobStatus] = mapped_column(PgEnum(JobStatus), nullable=False, default="")
    error_message: Mapped[str] = mapped_column(String(1000), nullable=True)
    message: Mapped[str] = mapped_column(String(1000), nullable=True)
    last_page: Mapped[int] = mapped_column(Integer, nullable=False)
    total_pages: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    cars: Mapped[list["CarDownloadInfo"]] = relationship(
        "CarDownloadInfo",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    brand_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
    )
