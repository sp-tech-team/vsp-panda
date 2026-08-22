import time

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",  # optional
            headless=False,
            slow_mo=500
        )

        yield browser

        browser.close()


@pytest.fixture(scope="session")
def context(browser):
    context = browser.new_context()

    yield context

    context.close()


@pytest.fixture(scope="function")
def page(context):
    page = context.new_page()
    page.goto("https://vsp-panda.streamlit.app/")
    # , wait_until="networkidle")
    time.sleep(3)
    spinner = page.locator("i")
    spinner.wait_for(state="hidden")

    yield page

    page.close()
