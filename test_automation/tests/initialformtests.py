from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json
from pages.finduserpage import FindUserPage
from pages.userdetailspage import UserDetailsPage

json_file = Path(__file__).parent.parent / "tests" / "testdata.json"

with open(json_file, "r") as f:
    data = json.load(f)


def test_app_is_launched(page):
    find_user_page = FindUserPage(page)
    expect(find_user_page.page_header).to_be_visible()
    expect(find_user_page.email_input).to_be_visible()
    expect(find_user_page.forgot_email).to_be_visible()


def test_user_search_with_valid_email(page):
    email_scenario = data["test_user_search_with_valid_email"]
    find_user_page = FindUserPage(page)
    user_dtls_page = UserDetailsPage(page)
    email_id = email_scenario["EmailId"]
    find_user_page.find_user_by_email(email_id)
    find_user_page.wait_for_locator()
    vol_category = user_dtls_page.get_volunteer_category(
        email_scenario["VolunteerCategory"])
    expect(vol_category).to_be_visible()


def test_user_search_with_valid_phn_number(page):
    phn_number_scenario = data["test_user_search_with_valid_phn_number"]
    find_user_page = FindUserPage(page)
    user_dtls_page = UserDetailsPage(page)
    find_user_page.forgot_email.click()
    find_user_page.find_user_by_phn_num(
        phn_number_scenario['CountryCode'], phn_number_scenario['PhoneNumber'])

    find_user_page.wait_for_locator()
    vol_category = user_dtls_page.get_volunteer_category(
        phn_number_scenario["VolunteerCategory"])
    expect(vol_category).to_be_visible()


def test_enter_invalid_email_shows_error(page):
    email_scenario = data["test_enter_invalid_email_shows_error"]
    find_user_page = FindUserPage(page)
    email_id = email_scenario["EmailId"]
    find_user_page.find_user_by_email(email_id)
    find_user_page.wait_for_locator()
    expect(find_user_page.email_error).to_be_visible()


def test_user_search_diff_country_code_phn(page):
    country_code_scenario = data["test_user_search_diff_country_code_phn"]
    find_user_page = FindUserPage(page)
    user_dtls_page = UserDetailsPage(page)
    find_user_page.forgot_email.click()
    find_user_page.find_user_by_phn_num(
        country_code_scenario['CountryCode'], country_code_scenario['PhoneNumber'])
    find_user_page.wait_for_locator()
    vol_category = user_dtls_page.get_volunteer_category(
        country_code_scenario["VolunteerCategory"])
    expect(vol_category).to_be_visible()


def test_invalid_email_phn_number_validation(page):
    invalid_email_phn_scenario = data["test_invalid_email_phn_number_validation"]
    find_user_page = FindUserPage(page)

    email_id = invalid_email_phn_scenario["EmailId"]
    find_user_page.find_user_by_email(email_id)
    find_user_page.wait_for_locator()

    find_user_page.forgot_email.click()
    find_user_page.find_user_by_phn_num(
        invalid_email_phn_scenario['CountryCode'], invalid_email_phn_scenario['PhoneNumber'])
    find_user_page.wait_for_locator()

    expect(find_user_page.email_error).to_be_visible()
    expect(find_user_page.phn_error_msg).to_be_visible()
    expect(find_user_page.counter_msg).to_be_visible()


def test_empty_phone_number_validation(page):
    country_code_scenario = data["test_empty_phone_number_validation"]
    find_user_page = FindUserPage(page)
    find_user_page.forgot_email.click()
    find_user_page.find_user_by_phn_num(
        country_code_scenario['CountryCode'], country_code_scenario['PhoneNumber'])
    find_user_page.wait_for_locator()
    expect(find_user_page.phn_num_req).to_be_visible()


def test_empty_email_validation(page):
    invalid_email_scenario = data["test_empty_email_validation"]
    find_user_page = FindUserPage(page)
    email_id = invalid_email_scenario["EmailId"]
    find_user_page.find_user_by_email(email_id)
    find_user_page.wait_for_locator()
    expect(find_user_page.email_req).to_be_visible()


def test_invalid_phone_number_validation(page):
    country_code_scenario = data["test_invalid_phone_number_validation"]
    find_user_page = FindUserPage(page)
    find_user_page.forgot_email.click()
    find_user_page.find_user_by_phn_num(
        country_code_scenario['CountryCode'], country_code_scenario['PhoneNumber'])
    find_user_page.wait_for_locator()
    expect(find_user_page.phn_error_msg).to_be_visible()
