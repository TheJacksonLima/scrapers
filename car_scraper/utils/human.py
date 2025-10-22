import time
import random
from bs4 import BeautifulSoup

def human_delay(a=0.8, b=2.0):
    time.sleep(random.uniform(a, b))


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
        time.sleep(random.uniform(0.1, 0.3))  # pausa entre os scrolls
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
