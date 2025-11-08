import math
import re

from sqlalchemy import func

from car_scraper.db.entity.base import Base
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.dto.JobDownloadControlDTO import JobDownloadControlDTO
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType
from car_scraper.db.session import engine
from car_scraper.scrapers.webmotors import Webmotors_Scraper
from car_scraper.services.service import Service
from car_scraper.utils.logging_config import setup_logging
from car_scraper.utils.my_time_now import my_time_now

logger = setup_logging()
service = Service()
web_motors = Webmotors_Scraper()


def update_total_ads_all_brands():
    for brand in service.get_all_brands("webmotors"):
        logger.info(f"Getting ads from:{brand}")
        update_total_ads_from_brand(brand)


def update_total_ads_from_brand(brand: BrandDTO):
    logger.info(f"Updating total ads from brand {brand}")
    batch_info = service.create_batch(brand, JobType.BRAND_TOTAL_ADS_UPDATE)

    batch_info.status = JobStatus.RUNNING
    batch_info.attempts = batch_info.attempts + 1
    service.update_batch(batch_info)

    try:
        brand = service.get_brand(brand.source, brand.name)
        total_ads = web_motors.get_total_ads(brand)
        brand_updated = service.update_ads(brand, total_ads)

        batch_info.status = JobStatus.COMPLETED
        batch_info.total_pages = math.ceil(brand_updated.total_ads / 47),

    except Exception as e:
        batch_info.status = JobStatus.FAILED
        batch_info.error_message = f"{type(e).__name__}: {e}"[:500]
        logger.exception(f"Error while updating ads for brand {brand} on batch: {batch_info}")

    finally:
        service.update_batch(batch_info)


def get_ads_from_brand(brand: BrandDTO, batch_info: JobDownloadControlDTO):
    logger.info(f"Getting ads from brand {brand} batch {batch_info}")

    batch_info.status = JobStatus.RUNNING
    batch_info.attempts = batch_info.attempts + 1
    batch_info = service.update_batch(batch_info)

    page_count = batch_info.last_page
    ad_count = 0
    count_no_action = 0

    try:
        while True:
            brand.href = re.sub(r"page=\d+", f"page={page_count}", brand.href)

            list_car_download_info = web_motors.get_cars_from_brand(brand, batch_info.job_id, page_count)
            count_downloaded = len(list_car_download_info)

            saved = service.save_car_download_info(list_car_download_info)
            count_saved = len(saved)

            logger.info(f"{brand}\t found: {count_downloaded}, saved {count_saved}")

            ad_count += count_saved
            batch_info.last_page = page_count
            service.update_batch(batch_info)

            logger.info(f"Page: {page_count} ads saved: {ad_count}\n")

            page_count += 1

            if count_saved == 0:
                count_no_action += 1

            if (page_count > batch_info.total_pages) or (count_no_action == 3):
                break

        batch_info.status = JobStatus.COMPLETED
        batch_info.error_message = ""
        batch_info.finished_at = my_time_now()

    except Exception as e:
        batch_info.status = JobStatus.FAILED
        batch_info.finished_at = my_time_now()
        batch_info.error_message = f"{type(e).__name__}: {e}"[:500]
        batch_info.last_page = page_count

        logger.exception("Error while fetching ads for %s on page %s", brand, page_count)
    finally:
        service.update_batch(batch_info)


def get_brands(source: JobSource):
    logger.info(f"Getting ads from brands")
    batch_info = service.create_batch(source, JobType.BRAND_DOWNLOAD)

    try:
        brands = web_motors.get_brands()
        saved = service.save_brands(brands)
        batch_info.status = JobStatus.COMPLETED
        logger.info(f"{len(saved)} brands updated/inserted.")

    except Exception as e:
        batch_info.status = JobStatus.FAILED
        batch_info.error_message = f"{type(e).__name__}: {e}"[:500]
        logger.exception(f"Error while fetching brands from{source}")

    finally:
        service.update_batch(batch_info)


def get_car_ads():
    logger.info(f"Getting car ads")
    l_car_ads = service.get_ads_to_download()

    if (l_car_ads is None) or (len(l_car_ads) == 0):
        logger.info(f"No car ads found!")
        return

    l_car_ad_saved = []
    car_ad_saved = []

    batch_info = service.create_batch(JobSource.WEBMOTORS, JobType.CAR_INFO)
    try:
        for car_ad in l_car_ads:
            car_ad_ret = web_motors.get_car_ad(car_ad)
            if car_ad_ret is not None:
                car_ad_saved = car_ad_saved + 1
                l_car_ad_saved.append(car_ad_saved)

        batch_info.status = JobStatus.COMPLETED
        batch_info.message = ' '.join(l_car_ad_saved)
        batch_info.finished_at = my_time_now()

    except Exception as e:
        batch_info.status = JobStatus.FAILED
        batch_info.finished_at = my_time_now()
        batch_info.error_message = f"{type(e).__name__}: {e}"[:500]
        batch_info.message = ' '.join(l_car_ad_saved)
        logger.exception(f"Error while fetching car ads on batch {batch_info.job_id}")

    finally:
        service.update_batch(batch_info)


def init_batch(brand: BrandDTO, job_type: JobType) -> JobDownloadControlDTO:
    batch_info = service.get_last_batch_from_brand(brand, job_type)
    if (batch_info is None) or (batch_info.status == JobStatus.COMPLETED):
        batch_info = service.create_batch(brand, job_type)

    logger.info(f"Processing batch {batch_info}")
    return batch_info


def main():
    logger.info("Starting scraper...")
    Base.metadata.create_all(bind=engine)
    try:
        #get_brands()
        #update_total_ads_all_brands()

        #brand = service.get_brand('webmotors', 'Honda')
        #batch = init_batch(brand, JobType.CAR_DOWNLOAD_INFO)
        #get_ads_from_brand(brand, batch)
        get_car_ads()
    except Exception as e:
        logger.exception(f"Error executing scrapper {e}")


if __name__ == "__main__":
    main()
