import argparse
import math

from car_scraper.db.entity.base import Base
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.dto.JobDownloadControlDTO import JobDownloadControlDTO
from car_scraper.db.models.enums.JobSource import JobSource
from car_scraper.db.models.enums.JobStatus import JobStatus
from car_scraper.db.models.enums.JobType import JobType
from car_scraper.db.mongo_repository import save_payload
from car_scraper.db.session import engine
from car_scraper.scrapers import BaseScraper
from car_scraper.scrapers.mobiauto import MobiAuto_Scrapper
from car_scraper.scrapers.webmotors import Webmotors_Scraper
from car_scraper.services.service import Service
from car_scraper.utils.exceptions import AdScrapingError
from car_scraper.utils.human import human_delay
from car_scraper.utils.logging_config import setup_logging
from car_scraper.utils.my_time_now import my_time_now

logger = setup_logging()
service = Service()
web_motors = Webmotors_Scraper()
mobi_auto = MobiAuto_Scrapper()
global scraper, source


def update_total_ads_all_brands(source: JobSource):
    for brand in service.get_all_brands(source):
        logger.info(f"Getting ads from:{brand}")
        update_total_ads_from_brand(brand)


def update_total_ads_from_brand(brand: BrandDTO):
    global scraper

    logger.info(f"Updating total ads from brand {brand}")
    batch_info = service.create_batch(brand, JobType.BRAND_TOTAL_ADS_UPDATE)

    batch_info.status = JobStatus.RUNNING
    batch_info.attempts = batch_info.attempts + 1
    service.update_batch(batch_info)

    try:
        brand = service.get_brand(brand.source, brand.name)
        brand.total_ads = scraper.get_total_ads(brand)
        brand.qty_pages = math.ceil(brand.total_ads / scraper.ADS_PER_PAGE)
        brand_updated = service.update_ads(brand)

        batch_info.status = JobStatus.COMPLETED
        batch_info.total_pages = brand_updated.qty_pages

    except Exception as e:
        batch_info.status = JobStatus.FAILED
        batch_info.error_message = f"{type(e).__name__}: {e}"[:500]
        logger.exception(f"Error while updating ads for brand {brand} on batch: {batch_info}")

    finally:
        service.update_batch(batch_info)


def get_ads_from_brand(brand: BrandDTO):
    global scraper
    ad_count = 0
    count_no_action = 0
    error_message = ""

    batch_info = init_batch(brand, JobType.CAR_DOWNLOAD_INFO)
    batch_info.status = JobStatus.RUNNING
    batch_info.started_at = my_time_now()
    batch_info.attempts = batch_info.attempts + 1
    batch_info = service.update_batch(batch_info)
    page_count = batch_info.last_page - 3  # because: if (page_count > brand.qty_pages) or (count_no_action == 3):
    logger.info(f"Getting ads from brand {brand} batch {batch_info}")

    try:
        while True:
            #Dentro do scraper, na wemotor tem que mudar isso ainda
            #brand.href = re.sub(r"page=\d+", f"page={page_count}", brand.href)

            list_car_download_info = scraper.get_cars_from_brand(brand, batch_info.job_id, page_count)
            count_downloaded = len(list_car_download_info)
            saved = service.update_list_car_download_info(list_car_download_info)
            count_saved = len(saved)

            logger.info(f"{brand}\t found: {count_downloaded}, saved {count_saved}")

            ad_count += count_saved
            batch_info.last_page = page_count
            service.update_batch(batch_info)

            page_count += 1

            if count_saved == 0:
                count_no_action += 1

            logger.info(f"Page: {page_count} of {brand.qty_pages}  - ads saved: {ad_count} of {brand.total_ads} - "
                        f"missing payloads {count_no_action}\n")

            if (page_count % 50) == 0:
                human_delay(30, 60)

            if (page_count > brand.qty_pages) or (count_no_action == 3):
                if count_no_action == 3:
                    page_count -= 3
                error_message = f" Found {page_count} of {brand.qty_pages} - total of missing payloads {count_no_action}"
                break

        batch_info.status = JobStatus.COMPLETED
        batch_info.total_pages = page_count
        batch_info.error_message = error_message
        batch_info.finished_at = my_time_now()
        logger.info(f"{batch_info}")

    except Exception as e:
        batch_info.status = JobStatus.FAILED
        batch_info.finished_at = my_time_now()
        batch_info.error_message = f"{type(e).__name__}: {e}"[:500]
        batch_info.last_page = page_count

        logger.exception("Error while fetching ads for %s on page %s", brand, page_count)
    finally:
        service.update_batch(batch_info)


def get_scraper(source: JobSource) -> BaseScraper | None:
    if source == JobSource.WEBMOTORS:
        scraper = web_motors
        logger.debug("web_motors scraper")
    elif source == JobSource.MOBIAUTO:
        scraper = mobi_auto
        logger.debug("mobi_auto scraper")
    else:
        logger.debug("Scraper not defined!!!")
        raise "Missing scraper parameter or scrapper was not defined!!!"

    return scraper


def get_brands(source: JobSource):
    logger.info(f"Getting ads from brands")
    batch_info = service.create_batch(source, JobType.BRAND_DOWNLOAD)

    try:
        scraper = get_scraper(source)
        brands = scraper.get_brands()
        brands_saved = service.save_brands(brands)
        batch_info.status = JobStatus.COMPLETED
        logger.info(f"{len(brands_saved)} brands updated/inserted.")

    except Exception as e:
        batch_info.status = JobStatus.FAILED
        batch_info.error_message = f"{type(e).__name__}: {e}"[:500]
        logger.exception(f"Error while fetching brands from{source}")

    finally:
        service.update_batch(batch_info)


def check_if_add_is_missing(car_ad) -> bool:
    try:
        if web_motors.is_ad_sold(car_ad.href):
            logger.info(f"{car_ad.car_desc} is not available")
            car_ad.status = JobStatus.MISSING_AD
            service.update_car_download_info(car_ad)
            return True
        return False
    except Exception as e:
        raise AdScrapingError("Error when checking ad!", car_ad) from e


def validate_ads():
    global source
    logger.info(f"Validating car ads")
    l_car_ads = service.get_ads_to_download(source=source)
    for car_ad in l_car_ads:
        try:
            if not check_if_add_is_missing(car_ad):
                car_ad.status = JobStatus.READY
                service.update_car_download_info(car_ad)

        except AdScrapingError as e:
            logger.error(f"An error occurred while processing the ad: {e}")
            car_ad.status = JobStatus.FAILED
            service.update_car_download_info(car_ad)


def get_car_ads(validate=False):
    global scraper, source

    l_ads_and_sellers = []
    ads_counter = 0

    logger.info(f"Getting car ads")
    l_car_ads = service.get_ads_to_scrape(status=JobStatus.PENDING, source=source)

    if not l_car_ads:
        logger.info(f"No car ads found!")
        return

    logger.info(f"Aqui 1 : source:{source} - type:{JobType.CAR_INFO}")
    batch_info = service.create_batch(source, JobType.CAR_INFO)
    batch_info.status = JobStatus.RUNNING
    service.update_batch(batch_info)
    logger.info(f"Aqui 2")

    try:
        for car_ad in l_car_ads:
            try:
                if validate and check_if_add_is_missing(car_ad):
                    continue

                car_ad.job_id = batch_info.job_id
                service.update_car_download_info(car_ad)

                ad_info = scraper.get_car_ad(car_ad)
                if ad_info is not None:
                    save_payload(ad_info)
                    ads_counter += 1
                    car_ad.status = JobStatus.COMPLETED
                    service.update_car_download_info(car_ad)
                else:
                    car_ad.status = JobStatus.FAILED
                    service.update_car_download_info(car_ad)

            except Exception as e:
                logger.exception(f"Error while processing ad {car_ad.href} — {car_ad.car_desc}")
                car_ad.status = JobStatus.FAILED
                service.update_car_download_info(car_ad)
                raise e

        service.save_or_update_ads_and_sellers(l_ads_and_sellers)
        batch_info.status = JobStatus.COMPLETED
        batch_info.finished_at = my_time_now()

    except Exception as e:
        logger.exception(f"Unexpected batch-level error while fetching car ads on batch {batch_info.job_id}")
        batch_info.status = JobStatus.FAILED
        batch_info.finished_at = my_time_now()
        batch_info.error_message = f"{type(e).__name__}: {e}"[:500]
        raise e

    finally:
        service.update_batch(batch_info)


def init_batch(brand: BrandDTO, job_type: JobType) -> JobDownloadControlDTO:
    batch_info = service.get_last_batch_from_brand(brand, job_type)
    last_page = batch_info.last_page if batch_info else 0

    if (batch_info is None) or (batch_info.status == JobStatus.COMPLETED):  #tem que ver isso aqui
        batch_info = service.create_batch(brand, job_type)
        batch_info.last_page = last_page

    logger.info(f"Processing batch {batch_info}")
    return batch_info


def execute_validate_ads():
    logger.info("Validating ads")

    for i in range(0, 11):
        try:
            logger.info(f"Validation attempt {i + 1}/11")
            validate_ads()
        except Exception as ex:
            logger.exception(f"Error during ad validation on attempt {i + 1}")
            continue

        if i != 10:
            human_delay(6, 30)

    logger.info("Done validating ads")


def execute_get_car_ads():
    counter_ex = 0
    #validate_ads()
    global source
    counter_ready_ads = service.get_count_from_source(JobStatus.PENDING, source)

    if counter_ready_ads == 0:
        counter_ready_ads = 1

    while counter_ready_ads > 0:  #and counter_ex < int(settings.MAX_EX_ALLOWED)*10:
        logger.info(f"Execute get car ads, total of READY ads: {counter_ready_ads}")
        try:
            get_car_ads()
            human_delay(10, 30)
        except Exception as ex:
            counter_ex = counter_ex + 1
            logger.info(f"One exception has occurred: {ex}")
            logger.info(f"Total exceptions: {counter_ex}")
            human_delay(60, 300)
        finally:
            #validate_ads()
            #human_delay(10, 30)
            counter_ready_ads = service.get_count_from_source(JobStatus.PENDING, source)


def producer(brand):
    get_ads_from_brand(brand)


def consumer():
    execute_get_car_ads()


def get_ads_from_all_brands(source_enum):
    pass


def main():
    logger.info("Starting scraper...")
    Base.metadata.create_all(bind=engine)

    parser = argparse.ArgumentParser(description="Car Scraper Worker")

    parser.add_argument(
        "--source",
        type=str,
        choices=["MOBIAUTO", "WEBMOTORS"],
        required=True,
        help="Source of ads to scrape"
    )

    parser.add_argument(
        "--brand",
        type=str,
        required=False,
        help="Brand to scrape (required only for producer)"
    )

    parser.add_argument(
        "--action",
        type=str,
        choices=["producer", "consumer"],
        required=True,
        help="Choose producer or consumer mode"
    )

    args = parser.parse_args()

    source_enum = JobSource[args.source]

    global scraper, source
    source = source_enum
    scraper = MobiAuto_Scrapper() if source_enum == JobSource.MOBIAUTO else Webmotors_Scraper()

    logger.info(f"Worker started | source={source_enum} | action={args.action}")

    if args.action == "producer":
        if not args.brand:
            logger.error("Producer mode requires --brand argument\n ie --brand Fiat or --brand all")
            return

        if args.brand == 'all':
            for brand in service.get_all_brands(source_enum):
                if brand is None: continue
                producer(brand)
        else:
            brand = service.get_brand(args.brand, source_enum)
            if brand is None: logger.info("Brand not found!!")
            producer(brand)

    elif args.action == "consumer":
        consumer()


if __name__ == "__main__":
    main()
