from decouple import Config, RepositoryEnv
from pathlib import Path

env_path = Path(__file__).parent.parent / "application.properties"
config = Config(repository=RepositoryEnv(str(env_path)))

class Settings:
    """Central configuration object for environment variables."""

    # Web URLs
    WEBMOTORS_URL: str = config("WEBMOTORS_URL", default="https://www.webmotors.com.br")
    ICARROS_URL: str = config("ICARROS_URL", default="https://www.icarros.com.br")
    OLX_AUTO_URL: str = config("OLX_AUTO_URL", default="https://www.olx.com.br/autos")

    # Database connection
    DB_URL: str = config("DB_URL")
    DB_USER: str = config("DB_USERNAME", default="")
    DB_PASSWORD: str = config("DB_PASSWORD", default="")

    HEADLESS: bool = config("HEADLESS", cast=bool, default=False)
    TIMEOUT: int = config("TIMEOUT", cast=int, default=20000)

settings = Settings()
