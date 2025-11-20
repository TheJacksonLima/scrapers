from decouple import Config, RepositoryEnv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
env_path = PROJECT_ROOT / "application.properties"
config = Config(repository=RepositoryEnv(str(env_path)))


class Settings:
    """Central configuration object for environment variables."""

    # Web URLs
    WEBMOTORS_URL: str = config("WEBMOTORS_URL", default="https://www.webmotors.com.br")
    ICARROS_URL: str = config("ICARROS_URL", default="https://www.icarros.com.br")
    OLX_AUTO_URL: str = config("OLX_AUTO_URL", default="https://www.olx.com.br/autos")

    #Execution parameters
    MAX_ADS_TO_PROCESS: str = config("MAX_ADS_TO_PROCESS", default="50")

    # Database connection
    DATABASE_URL: str = config("DATABASE_URL", default="")

    HEADLESS: bool = config("HEADLESS", cast=bool, default=False)
    TIMEOUT: int = config("TIMEOUT", cast=int, default=20000)

    LOG_DIR = config("LOG_DIR", default=str(PROJECT_ROOT / "tmp/logs"))
    LOG_FILE = config("LOG_FILE", default=str(Path(LOG_DIR) / "car_scraper.log"))
    LOG_LEVEL = config("LOG_LEVEL", default="INFO").upper()



settings = Settings()
