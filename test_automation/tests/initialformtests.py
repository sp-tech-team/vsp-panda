from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json

json_file = Path(__file__).parent.parent / "tests" / "test_data.json"

with open(json_file, "r") as f:
    data = json.load(f)


def test_app_is_launched(page):
    page_header = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_text("🔹 Raise a Request")
    email_input = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder("Enter your email ID")
    forgot_email = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
    expect(page_header).to_be_visible()
    expect(email_input).to_be_visible()
    expect(forgot_email).to_be_visible()


def test_user_search_with_valid_email(page):
    email_scenario = data["test_user_search_with_valid_email"]
    email_input = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder("Enter your email ID")
    email_input.click()
    email_input.fill(email_scenario["EmailId"])
    email_input.press("Enter")
    spinner = page.locator("i")
    spinner.wait_for(state="hidden")
    vol_category = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_text(f"Volunteer Category: {email_scenario['VolunteerCategory']}")
    expect(vol_category).to_be_visible()


def test_user_search_with_valid_phn_number(page):
    phn_number_scenario = data["test_user_search_with_valid_phn_number"]
    forgot_email = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
    forgot_email.click()
    phn_number = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
        "Enter phone number without country code")
    phn_number.fill(phn_number_scenario['PhoneNumber'])
    phn_number.press("Enter")
    vol_category = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_text(f"Volunteer Category: {phn_number_scenario['VolunteerCategory']}")
    expect(vol_category).to_be_visible()


def test_enter_invalid_email_shows_error(page):
    email_scenario = data["test_enter_invalid_email_shows_error"]
    email_input = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder("Enter your email ID")
    email_input.click()
    email_input.fill(email_scenario["EmailId"])
    email_input.press("Enter")
    error_msg = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        "Email ID does not exist in the database.")
    expect(error_msg).to_be_visible()


def test_empty_email_validation(page):
    email_input = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder("Enter your email ID")
    email_input.click()
    email_input.fill("    ")
    email_input.press("Enter")
    error_msg = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        "Please enter your email ID.")
    expect(error_msg).to_be_visible()


def test_user_search_diff_country_code_phn(page):
    country_code_scenario = data["test_user_search_diff_country_code_phn"]
    forgot_email = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
    forgot_email.click()
    phn_number = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
        "Enter phone number without")
    combobox = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_role(
        "combobox", name="Choose an option")
    combobox.fill(country_code_scenario["CountryCode"])
    combobox.press("ArrowDown")
    combobox.press("Enter")
    combobox.press("Tab")
    phn_number.fill(country_code_scenario["PhoneNumber"])
    phn_number.press("Enter")
    vol_category = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_text(f"Volunteer Category: {country_code_scenario['VolunteerCategory']}")
    expect(vol_category).to_be_visible()


def test_empty_phone_number_validation(page):
    forgot_email = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
    forgot_email.click()
    phn_number = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
        "Enter phone number without")
    phn_number.fill("  ")
    phn_number.press("Enter")
    error_msg = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        "Phone number is required.")
    expect(error_msg).to_be_visible()


def test_invalid_phone_number_validation(page):
    forgot_email = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
    forgot_email.click()
    phn_number = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
        "Enter phone number without")
    phn_number.fill("123456")
    phn_number.press("Enter")
    error_msg = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        "Phone number does not exist in the database.")
    expect(error_msg).to_be_visible()


def test_invalid_email_phn_number_validation(page):
    invalid_email_phn_scenario = data["test_invalid_email_phn_number_validation"]
    email_input = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder("Enter your email ID")
    email_input.click()
    email_input.fill(invalid_email_phn_scenario["EmailId"])
    email_input.press("Enter")
    email_error_msg = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        "Email ID does not exist in the database.")
    forgot_email = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
    forgot_email.click()
    phn_number = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
        "Enter phone number without")
    phn_number.fill(invalid_email_phn_scenario["PhoneNumber"])
    phn_number.press("Enter")
    phn_error_msg = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        "Phone number does not exist in the database.")
    expect(email_error_msg).to_be_visible()
    expect(phn_error_msg).to_be_visible()
    counter_msg = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        "Please visit counter 23/24 at welcome point for further assistance with your request.")
    expect(counter_msg).to_be_visible()
