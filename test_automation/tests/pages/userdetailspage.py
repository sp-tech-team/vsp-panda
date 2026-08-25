class UserDetailsPage:

    def __init__(self, page):
        self.page = page
        self.frame = page.locator(
            'iframe[title="streamlitApp"]'
        ).content_frame

        self.page_header = self.frame.get_by_text(
            "🔹 Raise a Request"
        )

    def get_volunteer_category(self, volunteer_category):
        return self.frame.get_by_text(
            f"Volunteer Category: {volunteer_category}"
        )
