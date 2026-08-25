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

        self.forgot_email = self.frame.get_by_test_id(
            "stBaseButton-secondary"
        )

        self.forgot_email = self.frame.get_by_test_id("stBaseButton-secondary")

        self.country_code = self.frame.get_by_role(
            "combobox", name="Select country code")

        self.phn_number = self.frame.get_by_placeholder(
            "Enter phone number without country code"
        )
        self.email_req = self.frame.get_by_text("Please enter your email ID.")
        self.email_error = self.frame.get_by_text("Email ID does not exist in")

        self.phn_error_msg = self.frame.get_by_text(
            "Phone number does not exist in the database.")

        self.phn_num_req = self.frame.get_by_text(
            "Phone number is required.")

        self.counter_msg = self.frame.get_by_text(
            "Please visit counter 23/24 at welcome point for further assistance with your request.")

    def find_user_by_email(self, email_id):
        self.email_input.fill(email_id)
        self.email_input.press("Enter")

    def wait_for_locator(self):
        spinner = self.page.locator("i")
        spinner.wait_for(state="hidden")

    def find_user_by_phn_num(self, country_code, phone_number):

        if phone_number is None:
            raise ValueError("Phone number cannot be None")

        if country_code is not None:
            self.country_code.fill(country_code)
            self.country_code.press("ArrowDown")
            self.country_code.press("Enter")
            self.country_code.press("Tab")

            self.phn_number.fill(phone_number)
            self.phn_number.press("Enter")
