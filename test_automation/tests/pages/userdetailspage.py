import time
from datetime import datetime, timedelta
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import pytest


class UserDetailsPage:

    def __init__(self, page):
        self.page = page
        self.frame = page.locator(
            'iframe[title="streamlitApp"]'
        ).content_frame

        self.page_header = self.frame.get_by_text(
            "🔹 Raise a Request"
        )

        self.cat_dropdown = self.frame.get_by_placeholder("Select Category")

        self.subcat_dropdown = self.frame.get_by_placeholder(
            "Select Sub Category")

        self.choose_option = self.frame.get_by_placeholder("Choose an option")

        self.from_date = self.frame.get_by_test_id("stDateInputField").first
        self.to_date = self.frame.get_by_test_id("stDateInputField").nth(1)

        self.coord_email = self.frame.get_by_test_id(
            "stTextInputRootElement").get_by_role("textbox", name=".")

        self.req_reason = self.frame.get_by_test_id(
            "stTextAreaRootElement").get_by_role("textbox", name=".")

        self.submit_req = self.frame.get_by_test_id(
            "stBaseButton-secondary")

        self.success_msg = self.frame.locator("text=Your request ID is")

        self.pgmavailable = self.frame.get_by_text(
            "No dates available for the")

        self.pgmdate = self.frame.get_by_placeholder("Select Program Date")

        self.pgmdeptdate = self.frame.get_by_text("Active program dates are")

        # Add locator once alert is added
        self.silenceerrormsg = self.frame.get_by_text(
            "The duration between From")

        # self.healthrelated = self.frame.locator('input[type="radio"][value="0"]')

        # self.healthrelated = self.page.get_by_label("Yes")

    def get_volunteer_category(self, volunteer_category):
        return self.frame.get_by_text(
            f"Volunteer Category: {volunteer_category}"
        )

    def get_user_name(self, name):
        return self.frame.get_by_text(
            f"Name: {name}"
        )

    def get_dept_date(self, date):
        return self.frame.get_by_text(
            f"Departure Date: {date}"
        )

    def enter_request(self, testdata):
        self.select_category(testdata['Category'])

        if ((testdata['VolunteerCategory'] == "Ashram Volunteer") or (testdata['VolunteerCategory'] == "Short Term Department Support")) and (testdata['SubCategory'] == "3 Day Silence"):
            self.page.keyboard.press("Enter")

        elif (testdata['SubCategory'] is not None):
            self.select_subcategory(testdata['SubCategory'])
        else:
            pytest.skip(
                "Sub category is not available. Skipping this scenario.")

        if (testdata["ProgramDate"] is not None):
            if self.pgmavailable.is_visible():
                pytest.skip(
                    "Program is not available. Skipping this scenario.")

            if self.pgmdeptdate.is_visible():
                pytest.skip(
                    "Program after departure date. Skipping this scenario.")

            self.select_prgmdates()

        if (testdata["FromDate"] is not None):
            self.select_from_to_date(
                testdata['SubCategory'], testdata['DepartureDate'], testdata['FromDate'], testdata['ToDate'])

        if (testdata["CoordinatorEmail"] is not None):
            self.enter_coord_email(testdata["CoordinatorEmail"])

        if (testdata["Reason"] is not None):
            self.enter_req_reason(testdata["Reason"])

        self.click_submit()

    def get_date_with_delta(self, delta_days):
        return (
            datetime.now() + timedelta(days=int(delta_days))
        ).strftime("%d/%m/%Y")

    def get_delta_from_dept_date(self, dept_date, delta_days):
        date_obj = datetime.strptime(dept_date, "%b %d, %Y").date()
        return (
            date_obj + timedelta(days=int(delta_days))
        ).strftime("%d/%m/%Y")

    def select_category(self, category):
        self.cat_dropdown.wait_for(state="visible", timeout=30000)
        self.cat_dropdown.click()
        self.cat_dropdown.fill(category)
        self.page.keyboard.press("Enter")

    def select_subcategory(self, subcategory):
        if subcategory in ["Arogya", "Meet Sahaya Team", "Karma Sadhana Support", "1 Day city visit", "Stay Extension"]:
            self.choose_option.wait_for(state="visible", timeout=30000)
            self.choose_option.click()
            self.choose_option.fill(subcategory)
            self.page.keyboard.press("Enter")
        else:
            self.subcat_dropdown.wait_for(state="visible", timeout=30000)
            self.subcat_dropdown.click()
            self.subcat_dropdown.fill(subcategory)
            self.page.keyboard.press("Enter")
        # if (subcategory in ("Break", "Exit", "1 Day city visit")):
        # self.healthrelated.check()
        # self.page.get_by_label("Yes").click()

    def select_prgmdates(self):
        self.page.keyboard.press("Tab")
        self.pgmdate.click()
        self.pgmdate.press("ArrowDown")
        self.pgmdate.press("Enter")

    def select_from_to_date(self, subcategory, deptdate, fromdate, todate):
        if (subcategory == "Stay Extension"):
            self.date_value = self.get_delta_from_dept_date(deptdate, fromdate)
        else:
            self.date_value = self.get_date_with_delta(fromdate)

        self.from_date.wait_for(state="visible", timeout=30000)
        self.from_date.click()
        self.from_date.clear()
        self.from_date.fill(self.date_value)
        self.from_date.press("Tab")

        self.select_to_date(self.date_value, todate)

    def select_to_date(self, fromdate, todate):
        if todate is not None:
            self.final_date = datetime.strptime(
                fromdate, "%d/%m/%Y").date() + timedelta(days=todate)
            # self.to_value = self.get_date_with_delta(final_date)
            self.to_date.wait_for(state="visible", timeout=30000)
            self.to_date.click()
            self.to_date.clear()
            self.to_date.fill(self.final_date.strftime("%d/%m/%Y"))
            self.to_date.press("Tab")

    def enter_coord_email(self, coordinatoremail):
        self.coord_email.click()
        self.coord_email.fill(coordinatoremail)
        self.coord_email.press("Enter")

    def enter_req_reason(self, reason):
        self.req_reason.click()
        self.req_reason.fill(reason)
        self.req_reason.press("Enter")

    def click_submit(self):
        self.submit_req.click()

    def get_reqid(self, scenario_name):
        try:
            if scenario_name == "test_ltv_usrdtl_neg_silence_3day":
                if not self.silenceerrormsg.is_visible():
                    return None

                alert_text = self.silenceerrormsg.text_content().strip()
                print(f"Alert displayed: {alert_text}")
                return True

            self.success_msg.wait_for(state="visible", timeout=20000)
            return (
                self.success_msg.text_content()
                .replace("Your request ID is", "")
                .strip()
            )

        except PlaywrightTimeoutError:
            pytest.fail(
                "Success message did not appear within 10 seconds. Request was likely not submitted successfully.")

    #  ok button on pop-up
    #  self.page.locator("iframe[title=\"streamlitApp\"]").content_frame.get_by_test_id("stBaseButton-primary").click()
