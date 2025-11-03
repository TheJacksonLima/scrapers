import re
from car_scraper.db.entity.base import Base  # ou declarative_base se você usa direto
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType
from car_scraper.db.session import engine
from car_scraper.scrapers.webmotors import Webmotors_Scraper
from car_scraper.services.service import Service
from car_scraper.utils.logging_config import setup_logging

logger = setup_logging()
service = Service()
web_motors = Webmotors_Scraper()


def update_total_ads_all_brands():
    for brand in service.get_all_brands("webmotors"):
        logger.info(f"Getting ads from:{brand}")
        update_total_ads_from_brand(brand)


def update_total_ads_from_brand(brand: BrandDTO):
    brand = service.get_brand_url(brand.source, brand.name)
    total_ads = web_motors.get_total_ads(brand)
    logger.info(f"Updated: {service.update_ads(brand, total_ads)}")

import re
from datetime import datetime

def get_ads_from_brand(brand: BrandDTO):
    logger.info(f"Getting ads from brand {brand}")

    batch_info = service.create_batch(brand, JobType.CAR_DOWNLOAD_INFO)

    page_count = 1
    ad_count = 0

    try:
        while True:
            brand.href = re.sub(r"page=\d+", f"page={page_count}", brand.href)

            list_car_download_info = web_motors.get_cars_from_brand(brand)

            logger.info(f"{brand}\t found : {len(list_car_download_info)} ads")
            service.save_car_download_info(list_car_download_info)

            ad_count += len(list_car_download_info)
            batch_info.last_page = page_count
            service.update_batch(batch_info)

            logger.info(f"Page: {page_count} ads saved: {ad_count}\n")

            page_count += 1

            if page_count > batch_info.total_pages:
                break

        batch_info.status = JobStatus.COMPLETED
        batch_info.error_message = ""
        batch_info.finished_at = datetime.utcnow()

    except Exception as e:
        batch_info.status = JobStatus.FAILED
        batch_info.error_message = f"{type(e).__name__}: {e}"
        batch_info.last_page = page_count

        logger.exception("Error while fetching ads for %s on page %s", brand, page_count)
    finally:
        service.update_batch(batch_info)


def get_brands():
    brands = web_motors.get_brands()
    saved = service.save_brands(brands)
    logger.info(f"{len(saved)} brands updated/inserted.")


def main():
    logger.info("Starting scraper...")
    Base.metadata.create_all(bind=engine)
    try:
        #get_brands()
        #update_total_ads_all_brands()
        brand = service.get_brand_url('webmotors', 'Audi')
        get_ads_from_brand(brand)
    except Exception as e:
        logger.exception(f"Error executing scrapper {e}")


if __name__ == "__main__":
    main()
