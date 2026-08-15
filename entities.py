# entities.py

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Volunteer:
    """Represents a volunteer record from the Volunteer Google Sheet."""

    visit_id: str
    person_id: str # !! Need to ask SH about datafield
    volunteer_id: str
    name: str
    gender: str
    email_id: str
    phone_number: str
    country: str
    volunteer_category: str
    seva_name: str
    departure_date: date | None = None

    def __str__(self) -> str:
        return f"{self.name} | <{self.email_id}> | <{self.phone_number}>"
    
@dataclass
class Team:
    """Represents a team record from the Team Master Google Sheet."""

    team_id: str
    name: str
    is_active: bool
    contact_email: str

    def __str__(self) -> str:
        return f"{self.team_id} - {self.name}"

@dataclass
class Category:
    """Represents a category record from the Category Master Google Sheet."""

    category_id: str
    category: str
    has_programs: bool
    is_active: bool
    display_order: int

    def __str__(self) -> str:
        return self.category

@dataclass
class SubCategory:
    """Represents a sub-category record from the Sub-Category Master Google Sheet."""

    sub_category_id: str
    category_id: str
    name: str
    is_active: bool
    team_id: str
    volunteer_category: str
    help_text: str
    show_from_date_input: bool
    show_to_date_input: bool
    show_coordinator_email_input: bool
    display_order: int

    def __str__(self) -> str:
        return self.name

@dataclass
class Program:
    """Represents a program record from the Program Master Google Sheet."""

    program_id: str
    program_name: str
    applicable_gender: str
    category_id: int
    is_active: bool
    show_from_date_input: bool
    show_to_date_input: bool
    show_coordinator_email_input: bool
    restriction_details: str
    help_text: str
    duration_in_days: int

    def __str__(self) -> str:
        return self.program_name

@dataclass
class ProgramToTeamMapping:
    """Represents a mapping between a program and a team from the Program to Team Mapping Google Sheet."""

    program_id: int
    volunteer_category: str
    team_id: str

    program: Program | None = None
    team: Team | None = None

    def __str__(self) -> str:
        return f"{self.program.program_name} - {self.team.name}"

@dataclass
class ProgramDates:
    """Represents the dates for a program from the Program Dates Google Sheet."""

    program_date_id: int
    program_id: int
    start_date: date
    end_date: date
    status: str
    slots_count: int | 0

    def __str__(self) -> str:
        return f"{self.start_date.strftime("%b %d, %Y")} - {self.end_date.strftime("%b %d, %Y")}"

@dataclass
class Request:
    """Represents a request record from the Requests Google Sheet."""

    request_id: str
    person_id: int
    visit_id: str
    name: str
    gender: str
    email_id: str
    phone_number: str
    volunteer_category: str
    request_type: str # represents the category of the request
    sub_category: str
    from_date: date
    to_date: date
    description: str
    timestamp: datetime
    request_status: str # ?? what to set
    team_comments: str # not from streamlit
    closed_by: str # not from streamlit
    assigned_department: str 
    reassigned_by: str # not from streamlit
    status: str 
    status_sub_type: str 
    last_edited: datetime 
    system_id: str # ?? what to set
    closed_on: date | None = None # not from streamlit
    from_date_processed: date | None = None # not from streamlit
    to_date_processed: date | None = None # not from streamlit
    timestamp_processed: date | None = None # not from streamlit

    def __str__(self) -> str:
        return f"{self.request_id} - {self.request_type} | {self.name} <{self.email_id}> <{self.phone_number}>"

@dataclass
class Log:
    """Represents a log record from the Logs Google Sheet."""

    log_id: str
    ip_address: str
    email_id: str
    phone_number: str
    message: str
    exception: str
    timestamp: datetime

    def __str__(self) -> str:
        return f"{self.log_id} - {self.email_id} | {self.message} | {self.timestamp}"

@dataclass
class Setting:
    """Represents a setting record from the Settings Google Sheet."""

    setting_id: str
    name: str
    description: str
    value: str

    def __str__(self) -> str:
        return f"{self.name} | {self.value}"
