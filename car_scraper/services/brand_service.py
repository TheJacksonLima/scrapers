from sqlalchemy.orm import Session
from car_scraper.db.brand_repository import save
from car_scraper.db.models import Brand
from typing import List


def save_brands(session: Session, brand_dtos: List) -> List[Brand]:
    saved = []
    for dto in brand_dtos:
        brand = save(session, dto)
        saved.append(brand)
    session.commit()
    return saved
