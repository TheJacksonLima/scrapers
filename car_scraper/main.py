from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from car_scraper.db.models import Base
from car_scraper.services.brand_service import save_brands
from car_scraper.scrapers.webmotors import WebmotorsScraper
from car_scraper.utils.config import settings
from car_scraper.utils.logging_config import setup_logging

def main():
    logger = setup_logging()
    logger.info("Starting scraper...")

    engine = create_engine(settings.DATABASE_URL, future=True)
    Base.metadata.create_all(engine)

    try:
        webMotors = WebmotorsScraper()
        brands = webMotors.get_brands()

        with Session(engine) as session:
            saved = save_brands(session, brands)
            logger.info(f"{len(saved)} brands updated/inserted.")
    except Exception as e:
        logger.exception(f"Error executing scrapper {e}")

if __name__ == "__main__":
    main()
