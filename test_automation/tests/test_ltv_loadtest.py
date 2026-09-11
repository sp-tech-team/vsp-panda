# python
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Barrier

import pytest
from playwright.sync_api import sync_playwright

from test_automation.tests.longtermvoltests import (
    data as ltv_data,
    test_ltv_usrdtl as run_ltv_usrdtl,
)


USERS = max(int(os.getenv("LTV_USERS", "50")), 50)
BASE_URL = os.getenv("LTV_BASE_URL")
SCENARIO_NAME = os.getenv("LTV_SCENARIO", next(iter(ltv_data)))
HEADLESS = os.getenv("LTV_HEADLESS", "true").lower() == "true"


def _run_user(user_number: int, start_barrier: Barrier) -> str:
    """Run one independent LTV user session."""
    if not BASE_URL:
        raise RuntimeError("LTV_BASE_URL must be set.")

    start_barrier.wait()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=HEADLESS)

        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(BASE_URL, wait_until="domcontentloaded")

            # Add login/setup steps here if they are not handled by BASE_URL.
            run_ltv_usrdtl(page, SCENARIO_NAME)

            return f"user-{user_number}: passed"
        finally:
            browser.close()


@pytest.mark.load
def test_ltv_usrdtl_50_concurrent_users():
    """Execute test_ltv_usrdtl with at least 50 concurrent users."""
    if os.getenv("RUN_LTV_LOAD") != "1":
        pytest.skip("Set RUN_LTV_LOAD=1 to run the concurrent load test.")

    if SCENARIO_NAME not in ltv_data:
        pytest.fail(
            f"Unknown scenario {SCENARIO_NAME!r}. "
            f"Available scenarios: {list(ltv_data)}"
        )

    start_barrier = Barrier(USERS)
    failures = []

    with ThreadPoolExecutor(max_workers=USERS) as executor:
        futures = [
            executor.submit(_run_user, user_number, start_barrier)
            for user_number in range(1, USERS + 1)
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as error:
                failures.append(repr(error))

    if failures:
        pytest.fail(
            f"{len(failures)} of {USERS} concurrent users failed:\n"
            + "\n".join(failures)
        )
