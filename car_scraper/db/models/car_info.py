from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from car_scraper.db.models.base import Base

class CarInfo(Base):
    __tablename__ = "car_info"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    href: Mapped[str] = mapped_column(String(500), nullable=False)
    car_desc: Mapped[str] = mapped_column(String(255), nullable=False)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # FK CORRETA (tabela 'brands', coluna 'id')
    brand_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("brands.id", ondelete="CASCADE"),
        nullable=False,
    )

    # RELACIONAMENTO ↔ Brand
    brand: Mapped["Brand"] = relationship(
        "Brand",
        back_populates="cars",
    )
