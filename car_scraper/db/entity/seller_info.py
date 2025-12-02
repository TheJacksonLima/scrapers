from datetime import datetime
from sqlalchemy import DateTime, func, Integer, String, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from car_scraper.db.entity.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from car_scraper.db.entity.job_download_control import JobDownloadControl


class SellerInfo(Base):
    __tablename__ = "seller_info"
    __table_args__ = (UniqueConstraint("name", "location", name="uq_seller_name_location"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)
    contact_code: Mapped[str] = mapped_column(String(20), nullable=True)
    stock_url: Mapped[str] = mapped_column(String(500), nullable=True)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False)

    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("job_download_control.job_id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    ads: Mapped[list["CarAdInfo"]] = relationship(
        "CarAdInfo", back_populates="seller", cascade="all, delete-orphan"
    )

    job: Mapped["JobDownloadControl"] = relationship("JobDownloadControl", back_populates="sellers")

    def __repr__(self):
        return (
            f"<SellerInfo(name='{self.name}', location='{self.location}', phone='{self.phone}', "
            f"contact_code='{self.contact_code}', stock_url='{self.stock_url}', job_id={self.job_id})>"
        )
