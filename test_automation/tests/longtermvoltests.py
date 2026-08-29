from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json
from pages.userdetailspage import UserDetailsPage
from pages.finduserpage import FindUserPage
import pytest

json_file = Path(__file__).parent.parent / "tests" / "ltv_testdata.json"

with open(json_file, "r") as f:
    data = json.load(f)


# def test_ltv_usrdtl_valid_email(page):
#     email_scenario = data["test_ltv_usrdtl_valid_email"]
#     user_dtls_page = UserDetailsPage(page)
#     find_user_page = FindUserPage(page)

#     find_user_page.search_user(email_scenario)

#     user_name = user_dtls_page.get_user_name(
#         email_scenario["Name"])

#     vol_category = user_dtls_page.get_volunteer_category(
#         email_scenario["VolunteerCategory"])

#     dept_date = user_dtls_page.get_dept_date(
#         email_scenario["DepartureDate"]
#     )
#     expect(user_name).to_be_visible()
#     expect(vol_category).to_be_visible()
#     expect(dept_date).to_be_visible()


# def test_ltv_usrdtl_valid_phnnum(page):
#     phn_number_scenario = data["test_ltv_usrdtl_valid_phnnum"]
#     user_dtls_page = UserDetailsPage(page)
#     find_user_page = FindUserPage(page)

#     find_user_page.search_user(phn_number_scenario)

#     user_name = user_dtls_page.get_user_name(
#         phn_number_scenario["Name"])

#     vol_category = user_dtls_page.get_volunteer_category(
#         phn_number_scenario["VolunteerCategory"])

#     dept_date = user_dtls_page.get_dept_date(
#         phn_number_scenario["DepartureDate"]
#     )
#     expect(user_name).to_be_visible()
#     expect(vol_category).to_be_visible()
#     expect(dept_date).to_be_visible()


# @pytest.mark.parametrize(
#     "scenario_name",
#     data.keys(),
#     ids=data.keys()
# )
# def test_ltv_usrdtl(page, scenario_name):

#     scenario = data[scenario_name]

#     user_dtls_page = UserDetailsPage(page)
#     find_user_page = FindUserPage(page)

#     find_user_page.search_user(scenario)
#     user_dtls_page.enter_request(scenario)

#     request_id = user_dtls_page.get_reqid()
#     print(f"Scenario: {scenario}")
#     print(f"Request ID: {request_id}")
#     assert request_id is not None


def test_ltv_usrdtl_stayext(page):

    email_scenario = data["test_ltv_usrdtl_stayext"]
    user_dtls_page = UserDetailsPage(page)
    find_user_page = FindUserPage(page)

    find_user_page.search_user(email_scenario)
    user_dtls_page.enter_request(email_scenario)

    request_id = user_dtls_page.get_reqid()
    print(f"Request ID: {request_id}")
    assert request_id is not None
