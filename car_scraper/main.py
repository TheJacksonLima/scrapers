from car_scraper.services.brand_service import BrandService
from car_scraper.scrapers.webmotors import Webmotors_Scraper
from car_scraper.services.brand_service import BrandService
from car_scraper.utils.logging_config import setup_logging

logger = setup_logging()
service = BrandService()
web_motors = Webmotors_Scraper()


def get_cars_from_brand(source: str, brand: str):
     brand_dto = service.get_brand_url(source,brand)
     print(f"{brand_dto.name}\n{brand_dto.href}")
     web_motors.get_cars_from_brand(brand_dto)



def get_brands():

    brands = web_motors.get_brands()
    saved = service.save_brands(brands)
    logger.info(f"{len(saved)} brands updated/inserted.")


def main():
    logger.info("Starting scraper...")

    #   engine = create_engine(settings.DATABASE_URL, future=True)
    #   Base.metadata.create_all(engine)

    try:
        #get_brands()
        get_cars_from_brand("webmotors","Volkswagen")
    except Exception as e:
        logger.exception(f"Error executing scrapper {e}")


if __name__ == "__main__":
    main()
