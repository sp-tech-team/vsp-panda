from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json
from pages.userdetailspage import UserDetailsPage
from pages.finduserpage import FindUserPage
import pytest

json_file = Path(__file__).parent.parent / "tests" / "stv_testdata.json"

with open(json_file, "r") as f:
    data = json.load(f)


@pytest.mark.parametrize(
    "scenario_name",
    data.keys(),
    ids=data.keys()
)
def test_stv_usrdtl(page, scenario_name):

    scenario = data[scenario_name]

    find_user_page = FindUserPage(page)
    user_dtls_page = UserDetailsPage(page)

    find_user_page.search_user(scenario)
    user_dtls_page.enter_request(scenario)

    result = user_dtls_page.get_reqid(scenario_name)
    print(f"Scenario: {scenario}")
    print(f"Result is: {result}")
    assert result is not None


# def test_stv_usrdtl_stayext(page, scenario_name):

#     scenario = data["test_stv_usrdtl_stayext"]
#     user_dtls_page = UserDetailsPage(page)
#     find_user_page = FindUserPage(page)

#     find_user_page.search_user(scenario)
#     user_dtls_page.enter_request(scenario)

#     result = user_dtls_page.get_reqid(scenario_name)
#     print(f"Scenario: {scenario}")
#     print(f"Result is: {result}")
#     assert result is not None
