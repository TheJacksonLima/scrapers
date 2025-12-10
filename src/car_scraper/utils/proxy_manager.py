import logging
import os
import random
from typing import Optional

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROXY_FILE_PATH = os.path.join(BASE_DIR, "proxy.txt")


class ProxyManager:
    """
    ProxyManager que lê proxies do arquivo proxy.txt.
    Cada linha deve estar em um dos formatos:
        ip:porta:user:pass
        http://ip:porta:user:pass
        socks5://ip:porta:user:pass
        http://user:pass@ip:porta
    """

    def __init__(self):
        self.proxies_raw = self._load_proxies()
        if not self.proxies_raw:
            logger.warning("No proxies loaded — running WITHOUT proxy.")
            self.enabled = False
        else:
            self.enabled = True

    def _load_proxies(self) -> list[str]:
        """Lê lista de proxies brutos do arquivo."""
        try:
            with open(PROXY_FILE_PATH, "r") as f:
                proxies = [line.strip() for line in f.readlines() if line.strip()]
            logger.info(f"Loaded {len(proxies)} proxies from file.")
            return proxies
        except Exception as e:
            logger.error(f"Error loading proxy file: {e}")
            return []

    def _parse_proxy(self, raw: str) -> Optional[dict]:
        """
        Converte a linha do arquivo no formato Playwright.
        """

        # Caso 1: http://user:pass@ip:porta
        if raw.startswith("http://") or raw.startswith("https://") or raw.startswith("socks5://"):
            if "@" in raw:
                # http://user:pass@ip:porta
                scheme, rest = raw.split("://", 1)
                creds, host = rest.split("@", 1)
                user, password = creds.split(":", 1)

                return {
                    "server": "http://p.webshare.io:80",
                    "username": user,
                    "password": password
                }

            # Caso: apenas http://ip:porta (sem auth)
            return {"server": raw}

        # Caso 2: ip:porta:user:pass
        parts = raw.split(":")
        if len(parts) == 4:
            ip, port, user, password = parts
            return {
                "server": "http://p.webshare.io:80",
                "username": user,
                "password": password
            }

        # Formato inválido
        logger.error(f"Invalid proxy format: {raw}")
        return None

    def get_proxy(self) -> Optional[dict]:
        """Escolhe e retorna um proxy convertido para o formato Playwright."""
        if not self.enabled:
            return None

        raw = random.choice(self.proxies_raw)
        proxy = self._parse_proxy(raw)

        if not proxy:
            logger.error(f"Could not parse proxy: {raw}")
            return None

        logger.info(f"Using proxy: {proxy['server']} ({raw})")
        return proxy


proxy_manager = ProxyManager()
