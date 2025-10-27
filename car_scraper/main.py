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
     total = web_motors.get_total_ads()
     print(f"Total ads:{total}\n")

def get_brands():
    brands = web_motors.get_brands()
    saved = service.save_brands(brands)
    logger.info(f"{len(saved)} brands updated/inserted.")

def main():
    logger.info("Starting scraper...")
    try:
        #get_brands()
        get_cars_from_brand("webmotors","Volkswagen")
    except Exception as e:
        logger.exception(f"Error executing scrapper {e}")


if __name__ == "__main__":
    main()
