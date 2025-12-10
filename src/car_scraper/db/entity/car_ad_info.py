from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, func, ForeignKey, Boolean, Index
from sqlalchemy import Integer, String, Enum as PgEnum
from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from car_scraper.db.entity.base import Base
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus

if TYPE_CHECKING:
    pass


class CarAdInfo(Base):
    __tablename__ = "car_ad_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ad_link: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    desc: Mapped[str] = mapped_column(String(100), nullable=True)

    ad_images_links: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(String)), nullable=False, default=list
    )
    qty_images: Mapped[int] = mapped_column(Integer, nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=True)
    year: Mapped[str] = mapped_column(String, nullable=True)
    km: Mapped[int] = mapped_column(Integer, nullable=True)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=True)
    transmission: Mapped[str] = mapped_column(String(50), nullable=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(100), nullable=False)
    trade_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[JobStatus] = mapped_column(PgEnum(JobStatus), nullable=False, default="")
    source: Mapped[JobSource] = mapped_column(PgEnum(JobSource), nullable=False, default="")

    ipva: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    license: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    items: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(String)), nullable=False, default=list
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    brand_id: Mapped[int] = mapped_column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_download_control.job_id", ondelete="CASCADE"), nullable=False)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("seller_info.id", ondelete="SET NULL"), nullable=True)

    # relationships
    brand: Mapped["Brand"] = relationship("Brand", back_populates="detailed_ads")
    job: Mapped["JobDownloadControl"] = relationship("JobDownloadControl", back_populates="detailed_ads")
    seller: Mapped["SellerInfo"] = relationship("SellerInfo", back_populates="ads")

    def __repr__(self):
        return (
            f"<CarAdInfo(city='{self.city}', year={self.year}, km={self.km}, "
            f"transmission='{self.transmission}', type='{self.type}', color='{self.color}', "
            f"brand_id={self.brand_id}, job_id={self.job_id})>"
        )


Index("ix_car_ad_info_ad_link", CarAdInfo.ad_link, unique=True)
