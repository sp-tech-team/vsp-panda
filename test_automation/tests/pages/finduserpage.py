class FindUserPage:

    def __init__(self, page):
        self.page = page
        self.frame = page.locator(
            'iframe[title="streamlitApp"]'
        ).content_frame

        self.page_header = self.frame.get_by_text(
            "🔹 Raise a Request"
        )

        self.email_input = self.frame.get_by_placeholder(
            "Enter your email ID"
        )

        self.forgot_email = self.frame.get_by_test_id("stBaseButton-secondary")
        self.country_code = self.frame.get_by_role("combobox", name=".")

        self.phn_number = self.frame.get_by_placeholder(
            "Enter phone number without")

        self.email_req = self.frame.get_by_text("Please enter your email ID.")

        self.email_error = self.frame.get_by_text("Email ID does not exist in")
        self.phn_error_msg = self.frame.get_by_text(
            "Phone number does not exist in the database.")

        self.phn_num_req = self.frame.get_by_text(
            "Phone number is required.")

        self.counter_msg = self.frame.get_by_text(
            "Please visit counter 23/24 at welcome point for further assistance with your request.")

    def search_user(self, email_scenario):
        if email_scenario.get('EmailId') is not None:
            print("Searching by email")
            self.find_user_by_email(email_scenario['EmailId'])

        if email_scenario.get('PhoneNumber') is not None:
            print("Searching by phone number")
            self.find_user_by_phn_num(
                email_scenario['CountryCode'],
                email_scenario['PhoneNumber']
            )

    def find_user_by_email(self, email_id):
        self.email_input.fill(email_id)
        self.email_input.press("Enter")
        self.wait_for_locator()

    def wait_for_locator(self):
        spinner = self.page.locator("i")
        spinner.wait_for(state="hidden")

    def find_user_by_phn_num(self, country_code, phone_number):

        if phone_number is None:
            raise ValueError("Phone number cannot be None")

        if country_code is not None:
            self.forgot_email.click()
            self.country_code.fill(country_code)
            self.country_code.press("ArrowDown")
            self.country_code.press("Enter")
            self.country_code.press("Tab")

            self.phn_number.fill(phone_number)
            self.phn_number.press("Enter")

            self.wait_for_locator()
