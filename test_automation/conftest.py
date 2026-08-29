import time
import pytest
from playwright.sync_api import sync_playwright
from pathlib import Path


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",  # optional
            headless=False,
            slow_mo=1000
        )

        yield browser

        browser.close()


@pytest.fixture(scope="session")
def context(browser):
    context = browser.new_context()

    yield context

    context.close()


@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()
    page.goto("https://vsp-panda.streamlit.app/")
    # , wait_until="networkidle")
    time.sleep(3)
    spinner = page.locator("i")
    spinner.wait_for(state="hidden")

    yield page

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)

        page.screenshot(
            path=screenshots_dir / f"{request.node.name}.png",
            full_page=True
        )

    page.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
