from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean, JSON, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass


class WebmotorsCarAd(Base):
    __tablename__ = "webmotors_car_ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ID único retornado pela API do Webmotors
    unique_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    # Preço
    price: Mapped[float] = mapped_column(Float, nullable=True)
    search_price: Mapped[float] = mapped_column(Float, nullable=True)

    # Especificações básicas
    make: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(120))
    version: Mapped[str] = mapped_column(String(255))

    year_fabrication: Mapped[int] = mapped_column(Integer)
    year_model: Mapped[int] = mapped_column(Integer)
    odometer: Mapped[int] = mapped_column(Integer)
    transmission: Mapped[str] = mapped_column(String(80))
    fuel: Mapped[str] = mapped_column(String(80))
    body_type: Mapped[str] = mapped_column(String(80))
    color: Mapped[str] = mapped_column(String(50))

    armored: Mapped[bool] = mapped_column(Boolean, default=False)
    final_plate: Mapped[str] = mapped_column(String(5))

    # Multivalores retornam como JSON
    optionals: Mapped[dict] = mapped_column(JSON, nullable=True)
    lifestyle: Mapped[dict] = mapped_column(JSON, nullable=True)
    vehicle_attributes: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Dados do vendedor
    seller_type: Mapped[str] = mapped_column(String(10))
    seller_name: Mapped[str] = mapped_column(String(120))
    seller_city: Mapped[str] = mapped_column(String(100))
    seller_state: Mapped[str] = mapped_column(String(100))
    seller_cnpj: Mapped[str] = mapped_column(String(20), nullable=True)
    seller_phones: Mapped[dict] = mapped_column(JSON, nullable=True)
    seller_localization: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Fotos
    photos: Mapped[dict] = mapped_column(JSON)

    # Datas (ISO format from API)
    created_date_api: Mapped[str] = mapped_column(String(40))
    published_date_api: Mapped[str] = mapped_column(String(40))

    # Controle interno do seu scraper
    inserted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
