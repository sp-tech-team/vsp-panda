from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json
import time
from datetime import datetime, timedelta


json_file = Path(__file__).parent.parent / "tests" / "ltv_testdata.json"

with open(json_file, "r") as f:
    data = json.load(f)


# def test_ltv_usrdtl_valid_email(page):
#     email_scenario = data["test_ltv_usrdtl_valid_email"]

#     expected_name = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
#         f"Name: {email_scenario['Name']}")
#     expect(expected_name).to_be_visible()
#     print(
#         f"✅ Verified Name: '{email_scenario['Name']}' is displayed correctly.  ")

#     expected_volcat = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
#         f"Volunteer Category: {email_scenario['VolunteerCategory']}")
#     expect(expected_volcat).to_be_visible()
#     print(
#         f"✅ Verified Volunteer Category: '{email_scenario['VolunteerCategory']}' is displayed correctly.  ")

#     expected_deptdate = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
#         f"Departure Date: {email_scenario['DepartureDate']}")
#     expect(expected_deptdate).to_be_visible()
#     print(
#         f"✅ Verified Departure Date: '{email_scenario['DepartureDate']}' is displayed correctly.  ")


# def test_ltv_usrdtl_valid_phnnum(page):
#     phn_number_scenario = data["test_ltv_usrdtl_valid_phnnum"]
#     forgot_email = page.locator(
#         "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
#     forgot_email.click()
#     phn_number = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
#         "Enter phone number without country code")
#     phn_number.fill(phn_number_scenario['PhoneNumber'])
#     phn_number.press("Enter")

#     expected_name = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
#         f"Name: {phn_number_scenario['Name']}")
#     expect(expected_name).to_be_visible()
#     print(
#         f"✅ Verified Name: '{phn_number_scenario['Name']}' is displayed correctly.  ")

#     expected_volcat = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
#         f"Volunteer Category: {phn_number_scenario['VolunteerCategory']}")
#     expect(expected_volcat).to_be_visible()
#     print(
#         f"✅ Verified Volunteer Category: '{phn_number_scenario['VolunteerCategory']}' is displayed correctly.  ")

#     expected_deptdate = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
#         f"Departure Date: {phn_number_scenario['DepartureDate']}")
#     expect(expected_deptdate).to_be_visible()
#     print(
#         f"✅ Verified Departure Date: '{phn_number_scenario['DepartureDate']}' is displayed correctly.  ")


# def get_date_with_delta(delta_days):
#     return (
#         datetime.now() + timedelta(days=int(delta_days))
#     ).strftime("%d/%m/%Y")


# def test_ltv_usrdtl_silence_3day(page):

#     phn_number_scenario = data["test_ltv_usrdtl_silence_3day"]

#     forgot_email = (
#         page.locator("iframe[title='streamlitApp']")
#         .content_frame
#         .get_by_test_id("stBaseButton-secondary")
#     )
#     forgot_email.click()

#     phn_number = (
#         page.locator("iframe[title='streamlitApp']")
#         .content_frame
#         .get_by_placeholder("Enter phone number without country code")
#     )
#     phn_number.fill(phn_number_scenario["PhoneNumber"])
#     phn_number.press("Enter")

#     cat_dropdown = (
#         page.locator("iframe[title='streamlitApp']")
#         .content_frame
#         .get_by_role("combobox", name="Select Category")
#     )
#     cat_dropdown.wait_for(state="visible", timeout=30000)
#     cat_dropdown.click()
#     cat_dropdown.fill(phn_number_scenario["Category"])
#     page.keyboard.press("Enter")

#     subcat_dropdown = (
#         page.locator("iframe[title='streamlitApp']")
#         .content_frame
#         .get_by_role("combobox", name="Select Sub Category")
#     )
#     subcat_dropdown.wait_for(state="visible", timeout=30000)
#     subcat_dropdown.click()
#     subcat_dropdown.fill(phn_number_scenario["SubCategory"])
#     page.keyboard.press("Enter")

#     # Date handling
#     if phn_number_scenario.get("FromDate") is not None:

#         date_value = get_date_with_delta(
#             phn_number_scenario["FromDate"]
#         )

#         from_date = (
#             page.locator("iframe[title='streamlitApp']")
#             .content_frame
#             .get_by_test_id("stDateInputField")
#             .first
#         )

#         from_date.wait_for(state="visible", timeout=30000)
#         from_date.click()
#         from_date.clear()
#         from_date.fill(date_value)
#         from_date.press("Tab")

#     if phn_number_scenario.get("ToDate") is not None:

#         final_date = (
#             int(phn_number_scenario["FromDate"]) + int(phn_number_scenario["ToDate"]))

#         date_value = get_date_with_delta(final_date)

#     to_date = (
#         page.locator("iframe[title='streamlitApp']")
#         .content_frame
#         .get_by_test_id("stDateInputField")
#         .nth(1)
#     )

#     to_date.wait_for(state="visible", timeout=30000)
#     to_date.click()
#     to_date.clear()
#     to_date.fill(date_value)
#     to_date.press("Tab")

#     sevacord_email = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
#         "Enter your Seva Coordinator")
#     sevacord_email.click()
#     sevacord_email.fill(phn_number_scenario["CoordinatorEmail"])
#     sevacord_email.press("Enter")

#     req_reason = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
#         "Please fill in with as much")
#     req_reason.click()
#     req_reason.fill(phn_number_scenario["Reason"])
#     req_reason.press("Enter")

#     submit_req = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id(
#         "stBaseButton-secondary").click()
