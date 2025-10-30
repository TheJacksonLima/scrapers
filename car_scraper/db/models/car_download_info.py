from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from car_scraper.db.models.base import Base

class CarDownloadInfo(Base):
    __tablename__ = "car_download_info"

    href: Mapped[str] = mapped_column(String(500), primary_key=True)
    car_desc: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    brand_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
    )

    brand: Mapped["Brand"] = relationship(
        "Brand",
        back_populates="cars",
    )

    def __repr__(self):
        return f"<CarDownloadInfo(href='{self.href}', car_desc='{self.car_desc}', image={self.image})>"
