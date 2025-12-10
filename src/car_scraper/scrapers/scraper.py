from abc import ABC, abstractmethod
from typing import List, Optional
from car_scraper.db.models.dto.BradDTO import BrandDTO
from car_scraper.db.models.dto.CarDownloadInfoDTO import CarDownloadInfoDTO


class BaseScraper(ABC):
    @abstractmethod
    def get_brands(self) -> List[BrandDTO]:
        pass

    @abstractmethod
    def get_cars_from_brand(self, brand: BrandDTO) -> list[CarDownloadInfoDTO] | Optional[dict]:
        pass

