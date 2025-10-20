from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class BrandDTO:
    name: str
    href: Optional[str] = None
    source: str = "unknown"  # "webmotors" | "icarros" | "olx_auto"

class BaseScraper(ABC):
    @abstractmethod
    def get_brands(self) -> List[BrandDTO]:
        """Fetch and return a list of brand data from a source."""
        pass
