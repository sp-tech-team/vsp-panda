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
import utils
from labels import *




#region Google Sheets headers

CATEGORIES_HEADER = (
    CATEGORY_CATEGORY_ID,
    CATEGORY_CATEGORY,
    CATEGORY_HAS_PROGRAMS,
    CATEGORY_IS_ACTIVE,
    CATEGORY_DISPLAY_ORDER,
)

LOGS_HEADER = (
    LOG_LOG_ID,
    LOG_IP_ADDRESS,
    LOG_EMAIL_ID,
    LOG_PHONE_NUMBER,
    LOG_MESSAGE,
    LOG_EXCEPTION,
    LOG_TIMESTAMP
)

PARAMETERS_HEADER = (
    PARAMETER_PARAMETER_ID,
    PARAMETER_PARAMETER_NAME,
    PARAMETER_PARAMETER_VALUE
)

# PROGRAMS_HEADER = (
#     PROGRAM_PROGRAM_ID,
#     PROGRAM_PROGRAM_NAME,
#     PROGRAM_APPLICABLE_GENDER,
#     PROGRAM_CATEGORY_ID,
#     PROGRAM_IS_ACTIVE,
#     PROGRAM_USER_INPUT_FROM_DATE,
#     PROGRAM_USER_INPUT_TO_DATE,
#     PROGRAM_SHOW_COORDINATOR_EMAIL,
#     PROGRAM_RESTRICTION_DETAILS,
#     PROGRAM_HELP_TEXT,
#     PROGRAM_DURATION_IN_DAYS
# )

PROGRAM_DATES_HEADER = (
    PROGRAM_DATES_PROGRAM_DATE_ID,
    PROGRAM_DATES_PROGRAM_ID,
    PROGRAM_DATES_START_DATE,
    PROGRAM_DATES_END_DATE,
    PROGRAM_DATES_IS_ACTIVE,
    PROGRAM_DATES_TOTAL_SLOTS,
)

# PROGRAM_TEAM_MAPPING_HEADER = (
#     PROGRAM_TEAM_MAPPING_PROGRAM_TEAM_MAP_ID,
#     PROGRAM_TEAM_MAPPING_PROGRAM_ID,
#     PROGRAM_TEAM_MAPPING_VOLUNTEER_CATEGORY,
#     PROGRAM_TEAM_MAPPING_TEAM_ID
# )

REQUESTS_HEADER = (
    REQUESTS_REQUEST_ID,
    REQUESTS_PERSON_ID,
    REQUESTS_VISIT_ID,
    REQUESTS_NAME,
    REQUESTS_GENDER,
    REQUESTS_EMAIL_ID,
    REQUESTS_PHONE_NUMBER,
    REQUESTS_VOLUNTEER_CATEGORY,
    REQUESTS_CATEGORY_ID,
    REQUESTS_SUB_CATEGORY_ID,
    # REQUESTS_PROGRAM_ID,
    REQUESTS_FROM_DATE,
    REQUESTS_TO_DATE,
    REQUESTS_DESCRIPTION,
    REQUESTS_TIMESTAMP,
    REQUESTS_ASSIGNED_DEPARTMENT,
    REQUESTS_PROGRAM_DATE_ID,
    REQUESTS_COORDINATOR_EMAIL_ID,
    REQUESTS_STATUS,
    REQUESTS_STATUS_SUBTYPE,
    REQUESTS_LAST_EDITED,
    REQUESTS_CLOSED_BY,
    REQUESTS_CLOSED_ON,
    REQUESTS_REASSIGNED_BY
)

SETTINGS_HEADER = (
    SETTINGS_SETTING_ID,
    SETTINGS_NAME,
    SETTINGS_DESCRIPTION,
    SETTINGS_VALUE
)

SUB_CATEGORIES_MASTER_HEADER = (
    SUB_CATEGORY_SUB_CATEGORY_ID,
    SUB_CATEGORY_CATEGORY_ID,
    SUB_CATEGORY_NAME,
    SUB_CATEGORY_APPLICABLE_GENDER,
    SUB_CATEGORY_IS_ACTIVE,
    SUB_CATEGORY_TEAM_ID,
    SUB_CATEGORY_VOLUNTEER_CATEGORY,
    SUB_CATEGORY_HELP_TEXT,
    SUB_CATEGORY_USER_INPUT_FROM_DATE,
    SUB_CATEGORY_USER_INPUT_TO_DATE,
    SUB_CATEGORY_SHOW_HEALTH_RELATED_BOOL,
    SUB_CATEGORY_SHOW_COORDINATOR_EMAIL,
    # SUB_CATEGORY_DISPLAY_ORDER,
    SUB_CATEGORY_DURATION_IN_DAYS,
    SUB_CATEGORY_DYNAMIC_DROPDOWN_FIELDS,
    SUB_CATEGORY_DYNAMIC_TEXTBOX_FIELDS,
    SUB_CATEGORY_SECONDARY_EMAIL_ID
)

TEAMS_HEADER = (
    TEAM_TEAM_ID,
    TEAM_NAME,
    TEAM_IS_ACTIVE,
    TEAM_CONTACT_EMAIL,
)

VALIDATION_CATEGORIES_HEADER = (
    VOLUNTER_CATEGORY_VOLUNTEER_CATEGORY_ID,
    VOLUNTEER_CATEGORY_NAME,
    VOLUNTEER_CATEGORY_REQUEST_LABEL
)

VOLUNTEERS_HEADER = (
    VOLUNTEER_VISIT_ID,
    VOLUNTEER_PERSON_ID,
    VOLUNTEER_VOLUNTEER_ID,
    VOLUNTEER_NAME,
    VOLUNTEER_GENDER,
    VOLUNTEER_EMAIL_ID,
    VOLUNTEER_PHONE_NUMBER,
    VOLUNTEER_COUNTRY,
    VOLUNTEER_VOLUNTEER_CATEGORY,
    VOLUNTEER_SEVA_NAME,
    VOLUNTEER_DEPARTURE_DATE,
)

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

    if worksheet == CATEGORIES_WORKSHEET:
        missing_headers = [
            header for header in CATEGORIES_HEADER if header not in headers
        ]
    elif worksheet == LOGS_WORKSHEET:
        missing_headers = [
            header for header in LOGS_HEADER if header not in headers
        ]
    elif worksheet == PARAMETERS_WORKSHEET:
        missing_headers = [
            header for header in PARAMETERS_HEADER if header not in headers
        ]
    # elif worksheet == PROGRAMS_WORKSHEET:
    #     missing_headers = [
    #         header for header in PROGRAMS_HEADER if header not in headers
    #     ]
    elif worksheet == PROGRAM_DATES_WORKSHEET:
        missing_headers = [
            header for header in PROGRAM_DATES_HEADER if header not in headers
        ]
    # elif worksheet == PROGRAM_TEAM_MAPPING_WORKSHEET:
    #     missing_headers = [
    #         header for header in PROGRAM_TEAM_MAPPING_HEADER if header not in headers
    #     ]
    elif worksheet == REQUESTS_WORKSHEET:
        missing_headers = [
            header for header in REQUESTS_HEADER if header not in headers
        ]
    elif worksheet == SETTINGS_WORKSHEET:
        missing_headers = [
            header for header in SETTINGS_HEADER if header not in headers
        ]
    elif worksheet == SUB_CATEGORIES_WORKSHEET:
        missing_headers = [
            header for header in SUB_CATEGORIES_MASTER_HEADER if header not in headers
        ]
    elif worksheet == TEAMS_WORKSHEET:
        missing_headers = [
            header for header in TEAMS_HEADER if header not in headers
        ]
    elif worksheet == VOLUNTEER_CATEGORIES_WORKSHEET:
        missing_headers = [
            header for header in VALIDATION_CATEGORIES_HEADER if header not in headers
        ]
    elif worksheet == VOLUNTEERS_WORKSHEET:
        missing_headers = [
            header for header in VOLUNTEERS_HEADER if header not in headers
        ]
    # ** Need to add more as worksheets are added

    if missing_headers:
        raise ValueError(
            f"{worksheet} sheet is missing required columns: "
            + ", ".join(missing_headers)
        )







# region Mapping Google Sheets rows to entities

def _row_to_category_entity(row: dict[str, Any]) -> Category:
    """Convert a Google Sheets row into a Category entity."""

    return Category(
        category_id = str(row.get(CATEGORY_CATEGORY_ID, 0)),
        category = str(row.get(CATEGORY_CATEGORY, "")).strip(),
        has_programs = str(row.get(CATEGORY_HAS_PROGRAMS, "")).strip().lower() == "true",
        is_active = str(row.get(CATEGORY_IS_ACTIVE, "")).strip().lower() == "true",
        display_order = int(str(row.get(CATEGORY_DISPLAY_ORDER, 0)).strip() or 0)
    )

def _row_to_parameter_entity(row: dict[str, Any]) -> Parameter:
    return Parameter(
        parameter_id = str(row.get(PARAMETER_PARAMETER_ID, "")).strip(),
        parameter_name = str(row.get(PARAMETER_PARAMETER_NAME, "")).strip(),
        parameter_value = str(row.get(PARAMETER_PARAMETER_VALUE, "")).strip(),
    )
  
# def _row_to_program_entity(row: dict[str, Any]) -> Program:
#     """Convert a Google Sheets row into a Program entity."""

#     return Program(
#         program_id = str(row.get(PROGRAM_PROGRAM_ID, 0)).strip(),
#         program_name = str(row.get(PROGRAM_PROGRAM_NAME, "")).strip(),
#         applicable_gender = str(row.get(PROGRAM_APPLICABLE_GENDER, "")).strip(),
#         category_id = str(row.get(PROGRAM_CATEGORY_ID, 0)),
#         is_active = str(row.get(PROGRAM_IS_ACTIVE, "")).strip().lower() == "true",
#         show_from_date_input = str(row.get(PROGRAM_USER_INPUT_FROM_DATE, "")).strip().lower() == "true",
#         show_to_date_input = str(row.get(PROGRAM_USER_INPUT_TO_DATE, "")).strip().lower() == "true",
#         show_coordinator_email_input = str(row.get(PROGRAM_SHOW_COORDINATOR_EMAIL, "")).strip().lower() == "true",
#         restriction_details = str(row.get(PROGRAM_RESTRICTION_DETAILS, "")).strip(),
#         help_text = str(row.get(PROGRAM_HELP_TEXT, "")).strip(),
#         duration_in_days = int(str(row.get(PROGRAM_DURATION_IN_DAYS, 0)).strip() or 0)
#     )

def _row_to_program_dates_entity(row: dict[str, Any]) -> ProgramDates:
    """Convert a Google Sheets row into a ProgramDates entity."""

    return ProgramDates(
        program_date_id = str(row.get(PROGRAM_DATES_PROGRAM_DATE_ID, '0')).strip(),
        program_id = str(row.get(PROGRAM_DATES_PROGRAM_ID, '0')).strip(),
        start_date = parse_date(row.get(PROGRAM_DATES_START_DATE)),
        end_date = parse_date(row.get(PROGRAM_DATES_END_DATE)),
        is_active = str(row.get(PROGRAM_DATES_IS_ACTIVE, "")).strip().lower() == "true",
        slots_count = int(str(row.get(PROGRAM_DATES_TOTAL_SLOTS, 0)).strip() or 0)
    )

# def _row_to_program_team_mapping_entity(row: dict[str, Any]) -> ProgramToTeamMapping:
#     """Convert a Google Sheets row into a ProgramToTeamMapping entity."""
    
#     return ProgramToTeamMapping(
#         program_team_map_id = str(row.get(PROGRAM_TEAM_MAPPING_PROGRAM_TEAM_MAP_ID, "")).strip(),
#         program_id = str(row.get(PROGRAM_TEAM_MAPPING_PROGRAM_ID, "")).strip(),
#         volunteer_category = str(row.get(PROGRAM_TEAM_MAPPING_VOLUNTEER_CATEGORY, "")).strip(),
#         team_id = str(row.get(PROGRAM_TEAM_MAPPING_TEAM_ID, "")).strip()
#     )

def _row_to_settings_entity(row: dict[str, Any]) -> Setting:
    return Setting(
        setting_id = str(row.get(SETTINGS_SETTING_ID, "")).strip(),
        name = str(row.get(SETTINGS_NAME, "")).strip(),
        description = str(row.get(SETTINGS_DESCRIPTION, "")).strip(),
        value = str(row.get(SETTINGS_VALUE, "")).strip(),
    )

def _row_to_subcategory_entity(row: dict[str, Any]) -> SubCategory:
    """Convert a Google Sheets row into a Sub Category entity."""

    dynamic_dropdown_fields = [ item.strip() for item in str(row.get(SUB_CATEGORY_DYNAMIC_DROPDOWN_FIELDS, "")).split(",") if item.strip() ]
    dynamic_textbox_fields = [ item.strip() for item in str(row.get(SUB_CATEGORY_DYNAMIC_TEXTBOX_FIELDS, "")).split(",") if item.strip() ]

    return SubCategory(
        subcategory_id = str(row.get(SUB_CATEGORY_SUB_CATEGORY_ID, 0)).strip(),
        category_id = str(row.get(SUB_CATEGORY_CATEGORY_ID, 0)).strip(),
        name = str(row.get(SUB_CATEGORY_NAME, "")).strip(),
        applicable_gender = str(row.get(SUB_CATEGORY_APPLICABLE_GENDER, "")).strip(),
        is_active = str(row.get(SUB_CATEGORY_IS_ACTIVE, "")).strip().lower() == "true",
        team_id = str(row.get(SUB_CATEGORY_TEAM_ID, "")).strip(),
        volunteer_category = str(row.get(SUB_CATEGORY_VOLUNTEER_CATEGORY, "")).strip(),
        help_text = str(row.get(SUB_CATEGORY_HELP_TEXT, "")).strip(),
        show_from_date_input = str(row.get(SUB_CATEGORY_USER_INPUT_FROM_DATE, "")).strip().lower() == "true",
        show_to_date_input = str(row.get(SUB_CATEGORY_USER_INPUT_TO_DATE, "")).strip().lower() == "true",
        show_health_related_bool_input = str(row.get(SUB_CATEGORY_SHOW_HEALTH_RELATED_BOOL, "")).strip().lower() == "true",
        show_coordinator_email_input = str(row.get(SUB_CATEGORY_SHOW_COORDINATOR_EMAIL, "")).strip().lower() == "true",
        # display_order = int(str(row.get(SUB_CATEGORY_DISPLAY_ORDER, 0)).strip() or 0),
        duration_in_days = int(str(row.get(SUB_CATEGORY_DURATION_IN_DAYS, 0)).strip() or 0),
        dynamic_dropdown_fields = dynamic_dropdown_fields,
        dynamic_textbox_fields = dynamic_textbox_fields,
        secondary_email = str(row.get(SUB_CATEGORY_SECONDARY_EMAIL_ID, "").strip())
    )   

def _row_to_team_entity(row: dict[str, Any]) -> Team:
    """Convert a Google Sheets row into a Team entity."""

    return Team(
        team_id = str(row.get(TEAM_TEAM_ID, "")).strip(),
        name = str(row.get(TEAM_NAME, "")).strip(),
        is_active = str(row.get(TEAM_IS_ACTIVE, "")).strip().lower() == "true",
        contact_email = str(row.get(TEAM_CONTACT_EMAIL, "")).strip(),
    )

def _row_to_volunteer_category_entity(row: dict[str, Any]) -> VolunteerCategory:
    """Convert a Google Sheets row into a VolunteerCategory entity."""

    return VolunteerCategory(
        volunteer_category_id = str(row.get(VOLUNTER_CATEGORY_VOLUNTEER_CATEGORY_ID, "")).strip(),
        name = str(row.get(VOLUNTEER_CATEGORY_NAME, "")).strip(),
        request_label = str(row.get(VOLUNTEER_CATEGORY_REQUEST_LABEL, "")).strip()
    )

def _row_to_volunteer_entity(row: dict[str, Any]) -> Volunteer:
    """Convert a Google Sheets row into a Volunteer entity."""

    return Volunteer(
        visit_id = str(row.get(VOLUNTEER_VISIT_ID, "")).strip(),
        person_id = str(row.get(VOLUNTEER_PERSON_ID, "")).strip(),
        volunteer_id = str(row.get(VOLUNTEER_VOLUNTEER_ID, "")).strip(),
        name = str(row.get(VOLUNTEER_NAME, "")).strip(),
        gender = str(row.get(VOLUNTEER_GENDER, "")).strip(),
        email_id = str(row.get(VOLUNTEER_EMAIL_ID, "")).strip(),
        phone_number = str(row.get(VOLUNTEER_PHONE_NUMBER, "")).strip(),
        country = str(row.get(VOLUNTEER_COUNTRY, "")).strip(),
        volunteer_category = str(row.get(VOLUNTEER_VOLUNTEER_CATEGORY, "")).strip(),
        seva_name = str(row.get(VOLUNTEER_SEVA_NAME, "")).strip(),
        departure_date = parse_date(row.get(VOLUNTEER_DEPARTURE_DATE)),
    )

# endregion Mapping Google Sheets rows to entities




allCacheRetention = utils.get_setting("allCacheRetention")
if not allCacheRetention or str(allCacheRetention).isdigit():
    allCacheRetention = 1800 # default value if nothing is found

# required_tbl_list = [
#     "categories", 
#     "parameters", 
#     "programs", 
#     "program_dates", 
#     "program_team_mapping", 
#     "settings", 
#     "subcategories",
#     "teams", 
#     "volunteer_categories"
#     "volunteers", 
# ]

# for tbl in required_tbl_list:
#     if tbl not in cacheRetention.keys():
#         cacheRetention[tbl] = 60 * 5 # if no config is given, make 5 min the default


# region Load data from Google Sheets into entities

@st.cache_data(ttl=allCacheRetention, show_spinner=False)
def fetch_all_sheet_data() -> dict[str, list[list[str]]]:
    """
    Fetches raw data for ALL worksheets in 1 single API call.
    """
    sheet = get_google_sheet()
    
    # List all tab names you want to load
    target_tabs = [
        CATEGORIES_WORKSHEET, 
        PARAMETERS_WORKSHEET, 
        PROGRAM_DATES_WORKSHEET,
        SETTINGS_WORKSHEET,
        SUB_CATEGORIES_WORKSHEET,
        TEAMS_WORKSHEET,
        VOLUNTEER_CATEGORIES_WORKSHEET,
        VOLUNTEERS_WORKSHEET
    ]
    
    # Batch call - 1 API Hit for all tabs combined!
    res = sheet.values_batch_get(target_tabs)
    
    data_by_tab = {}
    for value_range in res.get("valueRanges", []):
        # Extract tab name from range format "Categories!A1:Z100"
        tab_name = value_range.get("range", "").split("!")[0].strip("'")
        data_by_tab[tab_name] = value_range.get("values", [])
        
    return data_by_tab

def load_categories() -> list[Category]:
    """
    Load Category records from Google Sheets.
    """

    all_data = fetch_all_sheet_data()
    values = all_data.get(CATEGORIES_WORKSHEET, [])

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, CATEGORIES_WORKSHEET) # ** Need to check if this is working

    categories: list[Category] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        categories.append(_row_to_category_entity(row))

    categories = sorted(categories, key = lambda cat : cat.display_order)

    return categories

def load_parameters() -> tuple[Parameter, ...]:
    """
    Load Parameter records from Google Sheets.
    """

    all_data = fetch_all_sheet_data()
    values = all_data.get(PARAMETERS_WORKSHEET, [])

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, PARAMETERS_WORKSHEET) # ** Need to check if this is working

    parameters: list[Parameter] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        parameters.append(_row_to_parameter_entity(row))

    return tuple(parameters)

#
# def load_programs() -> tuple[Program, ...]:
#     """
#     Load Program records from Google Sheets.
#     """
    
#     all_data = fetch_all_sheet_data()
#     values = all_data.get(PROGRAMS_WORKSHEET, [])

#     if not values:
#         return ()

#     headers = [str(header).strip() for header in values[0]]
#     _validate_headers(headers, PROGRAMS_WORKSHEET) # ** Need to check if this is working

#     programs: list[Program] = []

#     for raw_row in values[1:]: # !! Don't know what this padded_row is doing
#         padded_row = raw_row + [""] * max( 
#             0,
#             len(headers) - len(raw_row),
#         )

#         row = dict(zip(headers, padded_row))
#         programs.append(_row_to_program_entity(row))

#     return tuple(programs)

def load_program_dates() -> tuple[ProgramDates, ...]:
    """
    Load Program Dates records from Google Sheets.
    """

    all_data = fetch_all_sheet_data()
    values = all_data.get(PROGRAM_DATES_WORKSHEET, [])

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, PROGRAM_DATES_WORKSHEET) # ** Need to check if this is working

    programs: list[ProgramDates] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        programs.append(_row_to_program_dates_entity(row))

    return tuple(programs)

#
# def load_program_team_mapping() -> tuple[ProgramToTeamMapping, ...]:
#     """
#     Load Program Team Mapping records from Google Sheets.
#     """
    
#     if sheet == None:
#         sheet = get_google_sheet()

#     worksheet = sheet.worksheet(PROGRAM_TEAM_MAPPING_WORKSHEET) # ** Need to check if this is working
#     values = worksheet.get_all_values()

#     if not values:
#         return ()

#     headers = [str(header).strip() for header in values[0]]
#     _validate_headers(headers, PROGRAM_TEAM_MAPPING_WORKSHEET) # ** Need to check if this is working

#     mapping: list[ProgramToTeamMapping] = []

#     for raw_row in values[1:]: # !! Don't know what this padded_row is doing
#         padded_row = raw_row + [""] * max( 
#             0,
#             len(headers) - len(raw_row),
#         )

#         row = dict(zip(headers, padded_row))
#         mapping.append(_row_to_program_team_mapping_entity(row))

#     return tuple(mapping)

def load_request_ids() -> tuple[str, ...]:
    """
    Load Request IDs from Request records from Google Sheets.
    """

    sheet = get_google_sheet()
    worksheet = sheet.worksheet(REQUESTS_WORKSHEET) # ** Need to check if this is working
    values = worksheet.get_all_values()

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, REQUESTS_WORKSHEET) # ** Need to check if this is working

    request_ids: list[str] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        request_ids.append(str(row.get("Request ID", "")))

    return tuple(request_ids)

def load_settings() -> tuple[Setting, ...]:
    """
    Load Settings records from Google Sheets.
    """

    all_data = fetch_all_sheet_data()
    values = all_data.get(SETTINGS_WORKSHEET, [])

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, SETTINGS_WORKSHEET) # ** Need to check if this is working

    settings: list[Parameter] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        settings.append(_row_to_settings_entity(row))

    return tuple(settings)

def load_subcategories() -> list[SubCategory]:
    """
    Load Sub Category records from Google Sheets.
    """

    all_data = fetch_all_sheet_data()
    values = all_data.get(SUB_CATEGORIES_WORKSHEET, [])

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, SUB_CATEGORIES_WORKSHEET) # ** Need to check if this is working

    subcategories: list[SubCategory] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        subcategories.append(_row_to_subcategory_entity(row))

    # subcategories = sorted(subcategories, key = lambda sub_cat : sub_cat.display_order)

    return subcategories

def load_teams() -> tuple[Team, ...]:
    """
    Load Team Master records from Google Sheets.
    """

    all_data = fetch_all_sheet_data()
    values = all_data.get(TEAMS_WORKSHEET, [])

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, TEAMS_WORKSHEET) # ** Need to check if this is working

    teams: list[Team] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        teams.append(_row_to_team_entity(row))

    return tuple(teams)

def load_volunteer_categories() -> tuple[VolunteerCategory, ...]:
    """
    Load Volunteer Category records from Google Sheets.
    """

    all_data = fetch_all_sheet_data()
    values = all_data.get(VOLUNTEER_CATEGORIES_WORKSHEET, [])

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, VOLUNTEER_CATEGORIES_WORKSHEET) # ** Need to check if this is working

    volunteer_categories: list[VolunteerCategory] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        volunteer_categories.append(_row_to_volunteer_category_entity(row))

    return tuple(volunteer_categories)

def load_volunteers() -> tuple[Volunteer, ...]:
    """
    Load Volunteer records from Google Sheets.

    The Sheet row order is preserved because it is required for the
    fallback rule when matching records have no departure date.
    """

    all_data = fetch_all_sheet_data()
    values = all_data.get(VOLUNTEERS_WORKSHEET, [])

    if not values:
        return ()

    headers = [str(header).strip() for header in values[0]]
    _validate_headers(headers, VOLUNTEERS_WORKSHEET) # ** Need to check if this is working

    volunteers: list[Volunteer] = []

    for raw_row in values[1:]: # !! Don't know what this padded_row is doing
        padded_row = raw_row + [""] * max( 
            0,
            len(headers) - len(raw_row),
        )

        row = dict(zip(headers, padded_row))
        volunteers.append(_row_to_volunteer_entity(row))

    return tuple(volunteers)

# endregion Load data from Google Sheets into entities












#region Repository classes

class CategoryRepository:
    """Read-only repository for Category records."""

    def __init__(self, categories: tuple[Category, ...] | None = None) -> None:
        self._categories = (
            load_categories()
            if categories is None
            else categories 
        )

    def get_by_id(self, category_id: str) -> Category | None:
        """Return the Category record matching a category ID."""
        for category in self._categories:
            if category.category_id == category_id:
                return category

        return None

    def get_active_categories(self) -> tuple[Category, ...]:
        """Return all active Category records."""
        return tuple(
            category
            for category in self._categories
            if category.is_active
        )

class LogRepository:
    """Repository for Log records."""

    def __init__(self) -> None:
        sheet = get_google_sheet()
        self._worksheet = sheet.worksheet("Logs")

    @staticmethod
    def _format_value(value: Any) -> Any:
        """Convert Python values into values suitable for Google Sheets."""

        if value is None:
            return ""

        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S") # need to put into gsheet settings

        if isinstance(value, date):
            return value.strftime("%Y-%m-%d") # need to put into gsheet settings

        return value

    def _request_to_row(self, log: Log) -> list[Any]:
        """Convert a Log object into the sheet's column order."""

        return [
            self._format_value(log.log_id),
            self._format_value(log.ip_address),
            self._format_value(log.email_id),
            self._format_value(log.phone_number),
            self._format_value(log.message),
            self._format_value(log.exception),
            self._format_value(log.timestamp),
        ]

    def write_to_sheet(self, log: Log) -> None:
        """Append a Log as a new row to the Google Sheet."""
        
        row = self._request_to_row(log)

        self._worksheet.append_row(
            row,
            value_input_option="USER_ENTERED",
            insert_data_option="INSERT_ROWS",
        )

class ParameterRepository:
    """Read-only repository for Parameter records."""

    def __init__(self, parameters: tuple[Parameter, ...] | None = None):
        self._parameters = (
            load_parameters()
            if parameters is None
            else parameters
        )

    def get_by_key(self, key: str) -> list[str]:
        filtered_parameters = [param.parameter_value 
                                for param in self._parameters 
                                if param.parameter_name == key ]

        return filtered_parameters

# class ProgramRepository:
#     """Read-only repository for Program records."""

#     def __init__(self, programs: tuple[Program, ...] | None = None, 
#                     program_dates: tuple[ProgramDates, ...] | None = None,
#                     program_team_map: tuple[ProgramToTeamMapping, ...] | None = None) -> None:
#         self._programs = (
#             load_programs()
#             if programs is None
#             else programs 
#         )

#         self._program_dates = (
#             load_program_dates()
#             if program_dates is None
#             else program_dates 
#         )

#         self._program_team_map = (
#             load_program_team_mapping()
#             if program_team_map is None
#             else program_team_map
#         )

#     def get_by_id(self, program_id: int) -> Program | None:
#         """Return the Program record matching a program ID."""

#         for program in self._programs:
#             if program.program_id == program_id:
#                 return program

#         return None

#     

#     
        
#     

#     def get_assigned_team(self, program_id: str, vol_cat: str) -> ProgramToTeamMapping:
#         """
#         Return the mapped team to program and volunteer category.
#         """

#         filtered_map = [
#             team_map
#             for team_map in self._program_team_map
#             if team_map.program_id == program_id
#         ]

#         for team_map in filtered_map:
#             if team_map.volunteer_category == vol_cat:
#                 return team_map

#         return None

class RequestRepository:
    """Repository for Program records."""

    def __init__(self) -> None:
        sheet = get_google_sheet()
        self._worksheet = sheet.worksheet("Requests")

    def get_existing_ids(self) -> list[str]:
        return load_request_ids()
    
    @staticmethod
    def _format_value(value: Any) -> Any:
        """Convert Python values into values suitable for Google Sheets."""

        if value is None:
            return ""

        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S") # need to put into gsheet settings

        if isinstance(value, date):
            return value.strftime("%Y-%m-%d") # need to put into gsheet settings

        return value

    def _request_to_row(self, request: Request) -> list[Any]:
        """Convert a Request object into the sheet's column order."""

        return [
            self._format_value(request.request_id),
            self._format_value(request.person_id),
            self._format_value(request.visit_id),
            self._format_value(request.name),
            self._format_value(request.gender),
            self._format_value(request.email_id),
            self._format_value(request.phone_number),
            self._format_value(request.volunteer_category),
            self._format_value(request.category_id),
            self._format_value(request.subcategory_id),
            self._format_value(request.from_date),
            self._format_value(request.to_date),
            self._format_value(request.description),
            self._format_value(request.timestamp),
            self._format_value(request.assigned_department),
            self._format_value(request.program_date_id),
            self._format_value(request.coordinator_email_id),
            self._format_value(request.status),
            self._format_value(request.status_sub_type),
            self._format_value(request.last_edited),
        ]

    def write_to_sheet(self, request: Request) -> None:
        """Append a Request as a new row to the Google Sheet."""

        row = self._request_to_row(request)

        self._worksheet.append_row(
            row,
            value_input_option="USER_ENTERED",
            insert_data_option="INSERT_ROWS",
        )

class SettingRepository:
    """Read-only repository for Setting records."""

    def __init__(self, settings: tuple[Setting, ...] | None = None):
        self._settings = (
            load_settings()
            if settings is None
            else settings
        )

    def get_by_key(self, key: str) -> Setting:
        for setting in self._settings:
            if setting.name == key:
                return setting
        
        return None

class SubCategoryRepository:
    """Read-only repository for Sub Category records."""

    def __init__(self, subcategories: tuple[SubCategory, ...] | None = None,
                        program_dates: tuple[ProgramDates, ...] | None = None) -> None:
        self._subcategories = (
            load_subcategories()
            if subcategories is None
            else subcategories 
        )

        self._program_dates = (
            load_program_dates()
            if program_dates is None
            else program_dates 
        )

    def get_by_category_and_gender(self, category_id: int, gender: str, volunteer_category: str) -> tuple[SubCategory, ...]:
        """Return all active Program records for a specific gender and category id."""
        return tuple(
            subcategory
            for subcategory in self._subcategories
            if subcategory.is_active and subcategory.category_id == category_id and
                (subcategory.applicable_gender == "Both" or subcategory.applicable_gender == gender) and
                subcategory.volunteer_category == volunteer_category
        )

    def get_active_program_dates(self, subcategory_id: int) -> tuple[ProgramDates, ...]:
        """Return all program dates for a specific sub-category ID."""

        return tuple(
            program_date
            for program_date in self._program_dates 
            if program_date.is_active and program_date.program_id == subcategory_id
        )

    def get_program_dates_in_range(self, subcategory_id: int, departure_date: datetime.date) -> tuple[datetime.date, ...]:
        """
        Return all program dates for a specific subcategory ID that are on or after the departure date.
        """
        
        active_program_dates = self.get_active_program_dates(subcategory_id)

        filtered_dates = [
            program_date
            for program_date in active_program_dates
            if program_date.start_date < departure_date and program_date.end_date < departure_date
        ]

        return tuple(filtered_dates)

    def get_by_id(self, subcategory_id: int) -> SubCategory | None:
        """Return the Sub Category record matching a sub-category ID."""

        for subcategory in self._subcategories:
            if subcategory.subcategory_id == subcategory_id:
                return subcategory

        return None

    def get_by_category_id_for_vol_cat(self, category_id: int, volunteer_category: str) -> tuple[SubCategory, ...]:
        """Return all Sub Category records matching a category ID."""

        active_subcategories = self.get_active_subcategories()

        matches = [
            subcategory
            for subcategory in active_subcategories
            if subcategory.category_id == category_id and 
                subcategory.volunteer_category == volunteer_category
        ]

        return tuple(matches)

    def get_active_subcategories(self) -> tuple[SubCategory, ...]:
        """Return all active Sub Category records."""
        return tuple(
            subcategory
            for subcategory in self._subcategories
            if subcategory.is_active
        )

class TeamRepository:
    """Read-only repository for Team records."""

    def __init__(self, teams: tuple[Team, ...] | None = None) -> None:
        self._teams = (
            load_teams()
            if teams is None
            else teams 
        )

    def get_by_id(self, team_id: str) -> Team | None:
        """Return the Team record matching a team ID."""
        normalized_team_id = str(team_id).strip()

        if not normalized_team_id:
            return None

        for team in self._teams:
            if str(team.team_id).strip() == normalized_team_id:
                return team

        return None

    def get_active_teams(self) -> tuple[Team, ...]:
        """Return all active Team records."""
        return tuple(
            team
            for team in self._teams
            if team.is_active
        )

class VolunteerCategoryRepository:
    """Read-only repository for VolunteerCategory records."""
    
    def __init__(self, categories: tuple[VolunteerCategory, ...] | None = None) -> None:
        self._volunteer_categories = (
            load_volunteer_categories()
            if categories is None
            else categories 
        )

    def get_by_id(self, category_id: str) -> VolunteerCategory | None:
        """Return the VolunteerCategory record matching a volunteer category ID."""
        for vol_cat in self._volunteer_categories:
            if vol_cat.volunteer_category_id == category_id:
                return vol_cat

        return None

    def get_by_name(self, category_name: str) -> VolunteerCategory | None:
        """Return the VolunteerCategory record matching a volunteer category."""
        for vol_cat in self._volunteer_categories:
            if vol_cat.name == category_name:
                return vol_cat

        return None

class VolunteerRepository:
    """Read-only repository for Volunteer records."""

    def __init__(self, volunteers: tuple[Volunteer, ...] | None = None) -> None:
        self._volunteers = (
            load_volunteers()
            if volunteers is None
            else volunteers 
        )

    @staticmethod
    def _select_latest_volunteer_record(matches: list[Volunteer]) -> Volunteer | None:
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
    
    def get_latest_by_email(self, email: str) -> Volunteer | None:
        """Return the latest Volunteer record matching an email address."""
        normalized_email = normalize_email(email)

        if normalized_email is None:
            return None, ""

        matches = [
            volunteer
            for volunteer in self._volunteers
            if normalize_email(volunteer.email_id) == normalized_email
        ]

        volunteer = self._select_latest_volunteer_record(matches)

        return_msg = ""
        if not volunteer:
            return_msg = "Volunteer not found."
        elif not volunteer.departure_date:
            return_msg = "Departure date not found."
        elif volunteer.departure_date < datetime.today().date():
            return_msg = f"Departure date ({volunteer.departure_date.strftime("%Y-%m-%d")}) is past."

        return volunteer, return_msg
            
    def get_latest_by_phone(self, phone_number: str, region: str = "IN") -> Volunteer | None:
        """Return the latest Volunteer record matching a phone number."""
        normalized_input = normalize_phone_number(phone_number, region)

        if normalized_input is None:
            return None, ""

        matches = [
            volunteer
            for volunteer in self._volunteers
            if phone_numbers_match(
                volunteer.phone_number,
                normalized_input,
            )
        ]

        volunteer = self._select_latest_volunteer_record(matches)
        
        return_msg = ""
        if not volunteer:
            return_msg = "Volunteer not found."
        elif not volunteer.departure_date:
            return_msg = "Departure date not found."
        elif volunteer.departure_date < datetime.today().date():
            return_msg = f"Departure date ({volunteer.departure_date.strftime("%Y-%m-%d")}) is past."

        return volunteer, return_msg

#endregion Repository classes