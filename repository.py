from __future__ import annotations

from datetime import date, datetime
from typing import Any

import gspread
import streamlit as st

from entities import *
from utils import (
    normalize_email,
    normalize_phone_number,
    parse_date,
    phone_numbers_match,
)




#region Google Sheets headers

VOLUNTEER_HEADERS = (
    "Visit ID",
    "Person ID",
    "Volunteer ID",
    "Name",
    "Gender",
    "Email ID",
    "Phone Number",
    "Country",
    "Volunteer Category",
    "Seva Name",
    "Departure Date",
)

TEAM_MASTER_HEADERS = (
    "Team ID",
    "Name",
    "Is Active",
    "Contact Email",
)

CATEGORY_MASTER_HEADERS = (
    "Category ID",
    "Category",
    "Has Programs",
    "Is Active",
)

SUB_CATEGORY_MASTER_HEADERS = (
    "Sub Category ID",
    "Category ID",
    "Name",
    "Is Active",
    "Team ID",
    "Volunteer Category",
    "Help Text",
)

PROGRAM_MASTER_HEADERS = (
    "Program ID",
    "Program Name",
    "Program Code",
    "Applicable Gender",
    "Is Active",
    "Load Program Dates",
    "Restriction Details",
    "Help Text",
)

PROGRAM_DATE_HEADERS = (
    "Program Date ID",
    "Program ID",
    "Start Date",
    "End Date",
    "Status",
    "Slots Count",)

#endregion Google Sheets headers







@st.cache_resource
def get_google_sheet() -> gspread.Worksheet:
    """
    Create and cache the Google Sheets worksheet connection.

    Required Streamlit secrets:

        [gcp_service_account]
        type = "service_account"
        project_id = "..."
        private_key_id = "..."
        private_key = "..."
        client_email = "..."
        client_id = "..."
        auth_uri = "https://accounts.google.com/o/oauth2/auth"
        token_uri = "https://oauth2.googleapis.com/token"
        auth_provider_x509_cert_url = "..."
        client_x509_cert_url = "..."
        universe_domain = "googleapis.com"
        spreadsheet_id = "..."
    """
    credentials = dict(st.secrets["gcp_service_account"])
    spreadsheet_details = dict(st.secrets["spreadsheet_details"])

    client = gspread.service_account_from_dict(credentials)
    spreadsheet = client.open_by_key(spreadsheet_details["spreadsheet_id"])

    return spreadsheet

def _validate_headers(headers: list[str], worksheet: str) -> None:
    """Ensure that the worksheet contains all required columns."""
    missing_headers: list[str] = []

    if worksheet == "Volunteer":
        missing_headers = [
            header for header in VOLUNTEER_HEADERS if header not in headers
        ]
    elif worksheet == "Team Master":
        missing_headers = [
            header for header in TEAM_MASTER_HEADERS if header not in headers
        ]
    elif worksheet == "Category Master":
        missing_headers = [
            header for header in CATEGORY_MASTER_HEADERS if header not in headers
        ]
    elif worksheet == "Sub Category Master":
        missing_headers = [
            header for header in SUB_CATEGORY_MASTER_HEADERS if header not in headers
        ]
    elif worksheet == "Program Master":
        missing_headers = [
            header for header in PROGRAM_MASTER_HEADERS if header not in headers
        ]
    elif worksheet == "Program Dates":
        missing_headers = [
            header for header in PROGRAM_DATE_HEADERS if header not in headers
        ]
    # ** Need to add more as worksheets are added

    if missing_headers:
        raise ValueError(
            f"{worksheet} sheet is missing required columns: "
            + ", ".join(missing_headers)
        )







# region Mapping Google Sheets rows to entities

def _row_to_volunteer(row: dict[str, Any]) -> Volunteer:
    """Convert a Google Sheets row into a Volunteer entity."""

    return Volunteer(
        visit_id = str(row.get("Visit ID", "")).strip(),
        person_id = str(row.get("Person ID", "")).strip(),
        volunteer_id = str(row.get("Volunteer ID", "")).strip(),
        name = str(row.get("Name", "")).strip(),
        gender = str(row.get("Gender", "")).strip(),
        email_id = str(row.get("Email ID", "")).strip(),
        phone_number = str(row.get("Phone Number", "")).strip(),
        country = str(row.get("Country", "")).strip(),
        volunteer_category = str(
            row.get("Volunteer Category", "")
        ).strip(),
        seva_name = str(row.get("Seva Name", "")).strip(),
        departure_date = parse_date(row.get("Departure Date")),
    )

def _row_to_team_master(row: dict[str, Any]) -> TeamMaster:
    """Convert a Google Sheets row into a TeamMaster entity."""

    return TeamMaster(
        team_id = str(row.get("Team ID", "")).strip(),
        name = str(row.get("Name", "")).strip(),
        is_active = str(row.get("Is Active", "")).strip().lower() == "true",
        contact_email = str(row.get("Contact Email", "")).strip(),
    )

def _row_to_category_master(row: dict[str, Any]) -> CategoryMaster:
    """Convert a Google Sheets row into a CategoryMaster entity."""

    return CategoryMaster(
        category_id = int(row.get("Category ID", 0)),
        category = str(row.get("Category", "")).strip(),
        has_programs = str(row.get("Has Programs", "")).strip().lower() == "true",
        is_active = str(row.get("Is Active", "")).strip().lower() == "true",
    )

def _row_to_subcategory_master(row: dict[str, Any]) -> SubCategoryMaster:
    """Convert a Google Sheets row into a SubCategoryMaster entity."""

    return SubCategoryMaster(
        sub_category_id = int(row.get("Sub Category ID", 0)),
        category_id = int(row.get("Category ID", 0)),
        name = str(row.get("Name", "")).strip(),
        is_active = str(row.get("Is Active", "")).strip().lower() == "true",
        team_id = str(row.get("Team ID", "")).strip(),
        volunteer_category = str(
            row.get("Volunteer Category", "")
        ).strip(),
        help_text = str(row.get("Help Text", "")).strip(),

        category = None,  # This will be populated later when linking to CategoryMaster
    )       

def _row_to_program_master(row: dict[str, Any]) -> ProgramMaster:
    """Convert a Google Sheets row into a ProgramMaster entity."""

    return ProgramMaster(
        program_id = int(row.get("Program ID", 0)),
        program_name = str(row.get("Program Name", "")).strip(),
        program_code = str(row.get("Program Code", "")).strip(),
        applicable_gender = str(row.get("Applicable Gender", "")).strip(),
        is_active = str(row.get("Is Active", "")).strip().lower() == "true",
        load_program_dates = str(row.get("Load Program Dates", "")).strip().lower() == "true",
        restriction_details = str(row.get("Restriction Details", "")).strip(),
        help_text = str(row.get("Help Text", "")).strip(),
    )

def _row_to_program_dates(row: dict[str, Any]) -> ProgramDates:
    """Convert a Google Sheets row into a ProgramDates entity."""

    return ProgramDates(
        program_date_id = int(row.get("Program Date ID", '0')),
        program_id = int(row.get("Program ID", '0')),
        start_date = parse_date(row.get("Start Date")),
        end_date = parse_date(row.get("End Date")),
        status = row.get("Status", "").strip(),
        slots_count = int(str(row.get("Slots Count", 0)).strip() or 0)
    )

# endregion Mapping Google Sheets rows to entities







# region Load data from Google Sheets into entities

@st.cache_data(ttl=10, show_spinner=False)
def load_volunteers() -> tuple[Volunteer, ...]:
    """
    Load Volunteer records from Google Sheets.

    The Sheet row order is preserved because it is required for the
    fallback rule when matching records have no departure date.
    """
    
    sheet = get_google_sheet()
    worksheet = sheet.worksheet("Volunteer Master") # ** Need to check if this is working
    values = worksheet.get_all_values()

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, "Volunteer") # ** Need to check if this is working

    volunteers: list[Volunteer] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        volunteers.append(_row_to_volunteer(row))

    return tuple(volunteers)

@st.cache_data(ttl=10, show_spinner=False)
def load_teams() -> tuple[TeamMaster, ...]:
    """
    Load Team Master records from Google Sheets.=
    """
    
    sheet = get_google_sheet()
    worksheet = sheet.worksheet("Team Master") # ** Need to check if this is working
    values = worksheet.get_all_values()

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, "Team Master") # ** Need to check if this is working

    teams: list[TeamMaster] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        teams.append(_row_to_team_master(row))

    return tuple(teams)

@st.cache_data(ttl=10, show_spinner=False)
def load_categories() -> tuple[CategoryMaster, ...]:
    """
    Load Category Master records from Google Sheets.
    """
    
    sheet = get_google_sheet()
    worksheet = sheet.worksheet("Category Master") # ** Need to check if this is working
    values = worksheet.get_all_values()

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, "Category Master") # ** Need to check if this is working

    categories: list[CategoryMaster] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        categories.append(_row_to_category_master(row))

    return tuple(categories)

@st.cache_data(ttl=10, show_spinner=False)
def load_subcategories() -> tuple[SubCategoryMaster, ...]:
    """
    Load SubCategory Master records from Google Sheets.
    """
    
    sheet = get_google_sheet()
    worksheet = sheet.worksheet("Sub Category Master") # ** Need to check if this is working
    values = worksheet.get_all_values()

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, "Sub Category Master") # ** Need to check if this is working

    subcategories: list[SubCategoryMaster] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        subcategories.append(_row_to_subcategory_master(row))

    return tuple(subcategories)

@st.cache_data(ttl=10, show_spinner=False)
def load_programs() -> tuple[ProgramMaster, ...]:
    """
    Load Program Master records from Google Sheets.
    """
    
    sheet = get_google_sheet()
    worksheet = sheet.worksheet("Program Master") # ** Need to check if this is working
    values = worksheet.get_all_values()

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, "Program Master") # ** Need to check if this is working

    programs: list[ProgramMaster] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        programs.append(_row_to_program_master(row))

    return tuple(programs)

@st.cache_data(ttl=10, show_spinner=False)
def load_program_dates() -> tuple[ProgramDates, ...]:
    """
    Load Program Dates records from Google Sheets.
    """
    
    sheet = get_google_sheet()
    worksheet = sheet.worksheet("Program Dates") # ** Need to check if this is working
    values = worksheet.get_all_values()

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, "Program Dates") # ** Need to check if this is working

    programs: list[ProgramDates] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        programs.append(_row_to_program_dates(row))

    return tuple(programs)


# endregion Load data from Google Sheets into entities







def _select_latest_volunteer_record(
    matches: list[Volunteer],
) -> Volunteer | None:
    """
    Select the required record from matching Volunteer records.

    If at least one matching record has a departure date, return the
    record with the latest departure date. Otherwise return the first
    matching record.
    """
    if not matches:
        return None

    dated_matches = [
        volunteer
        for volunteer in matches
        if volunteer.departure_date is not None
    ]

    if not dated_matches:
        return matches[0]

    return max(
        dated_matches,
        key=lambda volunteer: volunteer.departure_date,
    )






#region Repository classes

class VolunteerRepository:
    """Read-only repository for Volunteer records."""

    def __init__(self, volunteers: tuple[Volunteer, ...] | None = None) -> None:
        self._volunteers = (
            load_volunteers()
            if volunteers is None
            else volunteers 
        )

    def get_latest_by_email(self, email: str) -> Volunteer | None:
        """Return the latest Volunteer record matching an email address."""
        normalized_email = normalize_email(email)

        if normalized_email is None:
            return None

        matches = [
            volunteer
            for volunteer in self._volunteers
            if normalize_email(volunteer.email_id) == normalized_email
        ]

        return _select_latest_volunteer_record(matches)

    def get_latest_by_phone(self, phone_number: str) -> Volunteer | None:
        """Return the latest Volunteer record matching a phone number."""
        normalized_input = normalize_phone_number(phone_number)

        if normalized_input is None:
            return None

        matches = [
            volunteer
            for volunteer in self._volunteers
            if phone_numbers_match(
                volunteer.phone_number,
                normalized_input,
            )
        ]

        return _select_latest_volunteer_record(matches)

class TeamRepository:
    """Read-only repository for Team Master records."""

    def __init__(self, teams: tuple[TeamMaster, ...] | None = None) -> None:
        self._teams = (
            load_teams()
            if teams is None
            else teams 
        )

    def get_by_id(self, team_id: str) -> TeamMaster | None:
        """Return the TeamMaster record matching a team ID."""
        normalized_team_id = str(team_id).strip()

        if not normalized_team_id:
            return None

        for team in self._teams:
            if str(team.team_id).strip() == normalized_team_id:
                return team

        return None

    def get_active_teams(self) -> tuple[TeamMaster, ...]:
        """Return all active TeamMaster records."""
        return tuple(
            team
            for team in self._teams
            if team.is_active
        )

class CategoryRepository:
    """Read-only repository for Category Master records."""

    def __init__(self, categories: tuple[CategoryMaster, ...] | None = None) -> None:
        self._categories = (
            load_categories()
            if categories is None
            else categories 
        )

    def get_by_id(self, category_id: int) -> CategoryMaster | None:
        """Return the CategoryMaster record matching a category ID."""
        for category in self._categories:
            if category.category_id == category_id:
                return category

        return None

    def get_active_categories(self) -> tuple[CategoryMaster, ...]:
        """Return all active CategoryMaster records."""
        return tuple(
            category
            for category in self._categories
            if category.is_active
        )

class SubCategoryRepository:
    """Read-only repository for SubCategory Master records."""

    def __init__(self, subcategories: tuple[SubCategoryMaster, ...] | None = None) -> None:
        self._subcategories = (
            load_subcategories()
            if subcategories is None
            else subcategories 
        )

    def get_by_id(self, sub_category_id: int) -> SubCategoryMaster | None:
        """Return the SubCategoryMaster record matching a sub-category ID."""

        for subcategory in self._subcategories:
            if subcategory.sub_category_id == sub_category_id:
                return subcategory

        return None

    def get_by_category_id_for_vol_cat(self, category_id: int, volunteer_category: str) -> tuple[SubCategoryMaster, ...]:
        """Return all SubCategoryMaster records matching a category ID."""

        active_subcategories = self.get_active_subcategories()

        matches = [
            subcategory
            for subcategory in active_subcategories
            if subcategory.category_id == category_id and 
                subcategory.volunteer_category == volunteer_category
        ]

        return tuple(matches)

    def get_active_subcategories(self) -> tuple[SubCategoryMaster, ...]:
        """Return all active SubCategoryMaster records."""
        return tuple(
            subcategory
            for subcategory in self._subcategories
            if subcategory.is_active
        )

class ProgramRepository:
    """Read-only repository for Program Master records."""

    def __init__(self, programs: tuple[ProgramMaster, ...] | None = None, 
                    program_dates: tuple[ProgramDates, ...] | None = None) -> None:
        self._programs = (
            load_programs()
            if programs is None
            else programs 
        )

        self._program_dates = (
            load_program_dates()
            if program_dates is None
            else program_dates 
        )

    def get_by_id(self, program_id: int) -> ProgramMaster | None:
        """Return the ProgramMaster record matching a program ID."""

        for program in self._programs:
            if program.program_id == program_id:
                return program

        return None

    def get_active_programs_for_gender(self, gender: str) -> tuple[ProgramMaster, ...]:
        """Return all active ProgramMaster records for a specific gender."""
        return tuple(
            program
            for program in self._programs
            if program.is_active and (program.applicable_gender == "Both" or program.applicable_gender == gender)
        )

    def get_active_program_dates(self, program_id: int) -> tuple[ProgramDates, ...]:
        """Return all program dates for a specific program ID."""

        return tuple(
            program_date
            for program_date in self._program_dates 
            if program_date.status == "Active" and program_date.program_id == program_id
        )
        

    def get_program_dates_in_range(self, program_id: int, departure_date: datetime.date) -> tuple[datetime.date, ...]:
        """
        Return all program dates for a specific program ID that are on or after the departure date.
        """
        # Assuming you have a method to get all program dates for a specific program ID
        active_program_dates = self.get_active_program_dates(program_id)

        filtered_dates = [
            program_date
            for program_date in active_program_dates
            if program_date.start_date < departure_date and program_date.end_date < departure_date
        ]

        return tuple(filtered_dates)

#endregion Repository classes