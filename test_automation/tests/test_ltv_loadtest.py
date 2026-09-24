# python
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Barrier

import pytest
from playwright.sync_api import sync_playwright

from pages.finduserpage import FindUserPage
from pages.userdetailspage import UserDetailsPage


DATA_DIR = Path(__file__).parent
DEFAULT_DATA_FILES = (
    "ltv_testdata.json",
    "stv_testdata.json",
    "ashram_testdata.json",
)


def _load_scenarios() -> dict:
    configured_files = os.getenv("LTV_DATA_FILES")
    file_names = (
        [name.strip() for name in configured_files.split(",") if name.strip()]
        if configured_files
        else list(DEFAULT_DATA_FILES)
    )
    scenarios = {}

    for file_name in file_names:
        data_file = Path(file_name)
        if not data_file.is_absolute():
            data_file = DATA_DIR / data_file

        with data_file.open(encoding="utf-8") as data_file_handle:
            file_scenarios = json.load(data_file_handle)

        duplicate_names = scenarios.keys() & file_scenarios.keys()
        if duplicate_names:
            raise ValueError(
                f"Duplicate scenario names in {data_file.name}: "
                f"{sorted(duplicate_names)}"
            )
        scenarios.update(file_scenarios)

    return scenarios


SCENARIOS = _load_scenarios()


USERS = max(int(os.getenv("LTV_USERS", "50")), 50)
BASE_URL = os.getenv("LTV_BASE_URL")
SCENARIO_NAMES = [
    name.strip()
    for name in os.getenv(
        "LTV_SCENARIOS", os.getenv("LTV_SCENARIO", "")
    ).split(",")
    if name.strip()
]
if not SCENARIO_NAMES:
    ltv_data_file = DATA_DIR / "ltv_testdata.json"
    if ltv_data_file.exists():
        with ltv_data_file.open(encoding="utf-8") as ltv_data_file_handle:
            SCENARIO_NAMES = list(json.load(ltv_data_file_handle))
    else:
        SCENARIO_NAMES = list(SCENARIOS)
HEADLESS = os.getenv("LTV_HEADLESS", "true").lower() == "true"
BROWSER_START_DELAY = max(
    float(os.getenv("LTV_BROWSER_START_DELAY", "0")),
    0,
)


def _run_user(user_number: int, scenario_name: str, start_barrier: Barrier) -> str:
    """Run one independent LTV user session."""
    if not BASE_URL:
        raise RuntimeError("LTV_BASE_URL must be set.")

    start_barrier.wait()

    time.sleep((user_number - 1) * BROWSER_START_DELAY)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=HEADLESS)

        try:
            context = browser.new_context()
            page = context.new_page()
            page.goto(BASE_URL, wait_until="domcontentloaded")

            # Add login/setup steps here if they are not handled by BASE_URL.
            scenario = SCENARIOS[scenario_name]
            find_user_page = FindUserPage(page)
            user_details_page = UserDetailsPage(page)
            find_user_page.search_user(scenario)
            user_details_page.enter_request(scenario)
            result = user_details_page.get_reqid(scenario_name)
            assert result is not None

            return f"user-{user_number} ({scenario_name}): passed"
        finally:
            browser.close()


@pytest.mark.load
def test_ltv_usrdtl_50_concurrent_users():
    """Execute test_ltv_usrdtl with at least 50 concurrent users."""
    if os.getenv("RUN_LTV_LOAD") != "1":
        pytest.skip("Set RUN_LTV_LOAD=1 to run the concurrent load test.")

    unknown_scenarios = [
        name for name in SCENARIO_NAMES if name not in SCENARIOS]
    if unknown_scenarios:
        pytest.fail(
            f"Unknown scenarios: {unknown_scenarios}. "
            f"Available scenarios: {list(SCENARIOS)}"
        )

    start_barrier = Barrier(USERS)
    failures = []

    with ThreadPoolExecutor(max_workers=USERS) as executor:
        futures = [
            executor.submit(
                _run_user,
                user_number,
                SCENARIO_NAMES[(user_number - 1) % len(SCENARIO_NAMES)],
                start_barrier,
            )
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
