from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json
from pages.userdetailspage import UserDetailsPage
from pages.finduserpage import FindUserPage
import pytest

json_file = Path(__file__).parent.parent / "tests" / "ashram_testdata.json"

with open(json_file, "r") as f:
    data = json.load(f)


# @pytest.mark.parametrize(
#     "scenario_name",
#     data.keys(),
#     ids=data.keys()
# )
# def test_stv_usrdtl(page, scenario_name):

#     scenario = data[scenario_name]

#     user_dtls_page = UserDetailsPage(page)
#     find_user_page = FindUserPage(page)

#     find_user_page.search_user(scenario)
#     user_dtls_page.enter_request(scenario)

#     request_id = user_dtls_page.get_reqid()
#     print(f"Scenario: {scenario}")
#     print(f"Request ID: {request_id}")
#     assert request_id is not None


def test_av_usrdtl_exitbrk_travel(page):

    email_scenario = data["test_av_usrdtl_exitbrk_travel"]
    user_dtls_page = UserDetailsPage(page)
    find_user_page = FindUserPage(page)

    find_user_page.search_user(email_scenario)
    user_dtls_page.enter_request(email_scenario)

    request_id = user_dtls_page.get_reqid
    print(f"Request ID: {request_id}")
    assert request_id is not None
