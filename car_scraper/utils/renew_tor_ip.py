import logging

from stem import Signal
from stem.control import Controller

logger = logging.getLogger(__name__)


def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
        logger.info("New Tor Ip requested")
