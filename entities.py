# entities.py

from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Volunteer:
    """Represents a volunteer record from the Volunteer Google Sheet."""

    visit_id: str
    person_id: int
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
class TeamMaster:
    """Represents a team record from the Team Master Google Sheet."""

    team_id: str
    name: str
    is_active: bool
    contact_email: str

    def __str__(self) -> str:
        return f"{self.team_id} - {self.name}"

@dataclass
class CategoryMaster:
    """Represents a category record from the Category Master Google Sheet."""

    category_id: int
    category: str
    has_programs: bool
    is_active: bool

    def __str__(self) -> str:
        return self.category

@dataclass
class SubCategoryMaster:
    """Represents a sub-category record from the Sub-Category Master Google Sheet."""

    sub_category_id: int
    category_id: int
    name: str
    is_active: bool
    team_id: str
    volunteer_category: str
    help_text: str

    category: CategoryMaster | None = None

    def __str__(self) -> str:
        return f"{self.name} | {self.category.category}"

@dataclass
class ProgramMaster:
    """Represents a program record from the Program Master Google Sheet."""

    program_id: int
    program_name: str
    program_code: str
    applicable_gender: str
    is_active: bool
    load_program_dates: bool
    restriction_details: str
    help_text: str

    def __str__(self) -> str:
        return f'{self.program_name} ({self.program_code})'

@dataclass
class ProgramToTeamMapping:
    """Represents a mapping between a program and a team from the Program to Team Mapping Google Sheet."""

    program_id: int
    volunteer_category: str
    team_id: str

    program: ProgramMaster | None = None
    team: TeamMaster | None = None

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
    slots_count: int

    program: ProgramMaster | None = None

    def __str__(self) -> str:
        return f"{self.start_date.strftime("%b %d, %Y")} - {self.end_date.strftime("%b %d, %Y")}"

@dataclass
class Requests:
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
    request_status: str
    team_comments: str
    closed_by: str 
    assigned_department: str
    reassigned_by: str
    status: str
    status_sub_type: str
    last_edited: datetime
    system_id: str
    closed_on: date | None = None
    from_date_processed: date | None = None
    to_date_processed: date | None = None
    timestamp_processed: date | None = None

    def __str__(self) -> str:
        return f"{self.request_id} - {self.request_type} | {self.name} <{self.email_id}> <{self.phone_number}>"

@dataclass
class Log:
    """Represents a log record from the Logs Google Sheet."""

    log_id: int
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

    setting_id: int
    name: str
    description: str
    value: str

    def __str__(self) -> str:
        return f"{self.name} | {self.value}"