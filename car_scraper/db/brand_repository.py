from sqlalchemy import select
from sqlalchemy.orm import Session
from car_scraper.db.models import Brand


def find_by_name_and_source(session: Session, name: str, source: str) -> Brand | None:
    stmt = select(Brand).where(Brand.name == name, Brand.source == source)
    return session.execute(stmt).scalar_one_or_none()


def save(session: Session, dto) -> Brand:
    brand = find_by_name_and_source(session, dto.name, dto.source)
    if brand is None:
        brand = Brand(name=dto.name, source=dto.source, url=dto.href)
        session.add(brand)
    else:
        brand.url = dto.href
    return brand
