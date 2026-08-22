from playwright.sync_api import sync_playwright, expect
from pathlib import Path
import json
import time


json_file = Path(__file__).parent.parent / "tests" / "test_data.json"

with open(json_file, "r") as f:
    data = json.load(f)


def test_ltv_usrdtl_valid_email(page):
    email_scenario = data["test_ltv_usrdtl_valid_email"]
    email_input = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder("Enter your email ID")
    email_input.click()
    email_input.fill(email_scenario["EmailId"])
    email_input.press("Enter")
    spinner = page.locator("i")
    spinner.wait_for(state="hidden")

    expected_name = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        f"Name: {email_scenario['Name']}")
    expect(expected_name).to_be_visible()
    print(
        f"✅ Verified Name: '{email_scenario['Name']}' is displayed correctly.  ")

    expected_volcat = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        f"Volunteer Category: {email_scenario['VolunteerCategory']}")
    expect(expected_volcat).to_be_visible()
    print(
        f"✅ Verified Volunteer Category: '{email_scenario['VolunteerCategory']}' is displayed correctly.  ")

    expected_deptdate = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        f"Departure Date: {email_scenario['DepartureDate']}")
    expect(expected_deptdate).to_be_visible()
    print(
        f"✅ Verified Departure Date: '{email_scenario['DepartureDate']}' is displayed correctly.  ")


def test_ltv_usrdtl_valid_phnnum(page):
    phn_number_scenario = data["test_ltv_usrdtl_valid_phnnum"]
    forgot_email = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
    forgot_email.click()
    phn_number = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
        "Enter phone number without country code")
    phn_number.fill(phn_number_scenario['PhoneNumber'])
    phn_number.press("Enter")

    expected_name = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        f"Name: {phn_number_scenario['Name']}")
    expect(expected_name).to_be_visible()
    print(
        f"✅ Verified Name: '{phn_number_scenario['Name']}' is displayed correctly.  ")

    expected_volcat = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        f"Volunteer Category: {phn_number_scenario['VolunteerCategory']}")
    expect(expected_volcat).to_be_visible()
    print(
        f"✅ Verified Volunteer Category: '{phn_number_scenario['VolunteerCategory']}' is displayed correctly.  ")

    expected_deptdate = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_text(
        f"Departure Date: {phn_number_scenario['DepartureDate']}")
    expect(expected_deptdate).to_be_visible()
    print(
        f"✅ Verified Departure Date: '{phn_number_scenario['DepartureDate']}' is displayed correctly.  ")


def test_ltv_usrdtl_accom_sahaya(page):
    phn_number_scenario = data["test_ltv_usrdtl_accom_sahaya"]
    forgot_email = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-secondary")
    forgot_email.click()
    phn_number = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
        "Enter phone number without country code")
    phn_number.fill(phn_number_scenario['PhoneNumber'])
    phn_number.press("Enter")

    cat_dropdown = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_role("combobox", name="Choose an option")
    cat_dropdown.wait_for(state="visible", timeout=30000)
    cat_dropdown.click()
    cat_dropdown.fill(phn_number_scenario['Category'])
    page.keyboard.press("Enter")
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")
    page.keyboard.press("Down arrow")

    subcat_dropdown = page.locator(
        "iframe[title=\"streamlitApp\"]").content_frame.get_by_role("combobox", name="Choose an option")
    subcat_dropdown.wait_for(state="visible", timeout=30000)
    subcat_dropdown.click()
    subcat_dropdown.fill(phn_number_scenario['Category'])
    page.keyboard.press("Enter")

    # category = page.locator(
    #     "iframe[title=\"streamlitApp\"]").content_frame.get_by_text(phn_number_scenario['Category'])
    # category.wait_for(state="visible", timeout=30000)
    # print("Visible:", category.is_visible())
    # print("Enabled:", category.is_enabled())
    # category.click()

    # subcat = page.locator(
    #     "iframe[title=\"streamlitApp\"]").content_frame.get_by_text(phn_number_scenario['SubCategory'])
    # subcat.wait_for(state="visible", timeout=30000)
    # print("Visible:", subcat.is_visible())
    # print("Enabled:", subcat.is_enabled())
    # subcat.click()

    # coordinator_email = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
    #     "Enter your Seva Coordinator").click()
    # coordinator_email.fill(phn_number_scenario['CoordinatorEmail'])
    # coordinator_email.press("Tab")

    # enter_reason = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_placeholder(
    #     "Please fill in with as much").click()
    # enter_reason.fill(
    #     "Test automation creating request for Accommodation, meet with Sahaya with coorindator email")
    # submit_req = page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id(
    #     "stBaseButton-secondary").click()

    # expect(cat_dropdown).to_be_visible()
    # expect(select_cat).to_be_visible()
    # expect(select_subcat).to_be_visible()
    # expect(enter_reason).to_be_visible()
    # expect(submit_req).to_be_visible()
