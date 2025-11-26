import logging
import random
import time

from bs4 import BeautifulSoup
from sqlalchemy.dialects import postgresql

from car_scraper.utils.config import PROJECT_ROOT

logger = logging.getLogger(__name__)


def human_delay(min_seconds=0.8, max_seconds=2.0):
    duration = random.uniform(min_seconds, max_seconds)
    logger.info(f"Sleeping for {duration:.2f} seconds...")
    time.sleep(duration)


def human_scroll(page, distance=600):
    step = 60
    scrolled = 0
    while scrolled < distance:
        page.evaluate("window.scrollBy(0, %s)" % step)
        scrolled += step
        time.sleep(random.uniform(0.05, 0.18))


def human_scroll_to_bottom(page, step=400):
    last_height = page.evaluate("document.body.scrollHeight")

    while True:
        page.evaluate(f"window.scrollBy(0, {step})")
        time.sleep(random.uniform(0.1, 0.3))
        time.sleep(random.uniform(0.5, 1.0))
        new_height = page.evaluate("document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height


def show_html(container, size=2000):
    html_content = container.inner_html()
    soup = BeautifulSoup(html_content, "html.parser")
    pretty_html = soup.prettify()

    print("===== CONTAINER HTML =====")
    print(pretty_html[:size])
    print("===== END OF HTML =====")


def show_sql(stmt):
    print("===== SQL =====")
    print(stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))
    print("==========")


def save_page_to_file(content: str):
    tmp_dir = PROJECT_ROOT / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    file_path = tmp_dir / "page.html"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
