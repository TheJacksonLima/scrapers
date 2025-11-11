from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from car_scraper.db.entity.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from car_scraper.db.entity import CarDownloadInfo
    from car_scraper.db.entity.car_ad_info import CarAdInfo


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    total_ads: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    downloaded_cars: Mapped[list["CarDownloadInfo"]] = relationship(
        "CarDownloadInfo",
        back_populates="brand",
        cascade="all, delete-orphan",
    )

    detailed_ads: Mapped[list["CarAdInfo"]] = relationship(
        "CarAdInfo",
        back_populates="brand",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("name", "source", name="uk_brand_name_source"),
    )

    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}', source='{self.source}', total_ads={self.total_ads})>"
