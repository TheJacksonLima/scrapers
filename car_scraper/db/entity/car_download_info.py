from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from car_scraper.db.models import Brand
from car_scraper.db.entity.base import Base
from car_scraper.db.entity.job_download_control import JobDownloadControl


class CarDownloadInfo(Base):
    __tablename__ = "car_download_info"

    href: Mapped[str] = mapped_column(String(500), primary_key=True)
    car_desc: Mapped[str] = mapped_column(String(255), nullable=False)
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    brand_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
    )

    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("job_download_control.job_id", ondelete="CASCADE"),
        nullable=False
    )

    brand: Mapped["Brand"] = relationship(
        "Brand",
        back_populates="cars",
    )

    job: Mapped["JobDownloadControl"] = relationship(
        "JobDownloadControl",
        back_populates="cars"
    )

    def __repr__(self):
        return f"<CarDownloadInfo(href='{self.href}', car_desc='{self.car_desc}', image={self.image})>"
