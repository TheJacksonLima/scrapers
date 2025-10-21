import time, random


def human_delay(a=0.8, b=2.0):
    time.sleep(random.uniform(a, b))


def human_scroll(page, distance=600):
    step = 60
    scrolled = 0
    while scrolled < distance:
        page.evaluate("window.scrollBy(0, %s)" % step)
        scrolled += step
        time.sleep(random.uniform(0.05, 0.18))
