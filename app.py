from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import streamlit as st
import threading
import utils
import re

from entities import Program, Request, SubCategory
from repository import CategoryRepository, ParameterRepository, ProgramRepository, RequestRepository, SettingRepository, SubCategoryRepository, TeamRepository, VolunteerCategoryRepository, VolunteerRepository
from service import EmailService

category_repo = CategoryRepository()
parameter_repo = ParameterRepository()
program_repo = ProgramRepository()
request_repo = RequestRepository()
setting_repo = SettingRepository()
subcategory_repo = SubCategoryRepository()
team_repo = TeamRepository()
vol_cat_repo = VolunteerCategoryRepository()
volunteer_repo = VolunteerRepository()

email_service = EmailService()

if "state" not in st.session_state:
    st.session_state["state"] = "Identification"
elif "volunteer_identified" in st.session_state and st.session_state["volunteer_identified"]:
    st.session_state["state"] = "Form"

    # These fields are requried for validating the form
    # Initializing the states, actual values would be put while the fields are rendered
    st.session_state["is_sub_cat_req"] = False
    st.session_state["is_program_selection"] = False
    st.session_state["is_program_date_req"] = False
    st.session_state["is_coordinator_email_req"] = False

def load_css() -> None:
    """Load application CSS."""

    css_path = Path(__file__).parent / "styles" / "style.css"
    css = css_path.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )

def show_volunteer_email_identification() -> None:
    """Render the Volunteer identification flow."""
    # st.header("👤 Volunteer Identification")

    required_label("📧 Email ID")
    email = st.text_input(
        "",
        placeholder="Enter your email ID",
        label_visibility="collapsed",
        key="email_id"
    )

    if email:
        if not email.strip():
            st.error("Please enter your email ID.")
            return

        volunteer = volunteer_repo.get_latest_by_email(email)

        if volunteer is not None:
            st.session_state["volunteer"] = volunteer
            st.session_state["volunteer_identified"] = True

            if st.session_state.get("volunteer_identified"):
                volunteer = st.session_state["volunteer"]
                st.rerun()

        st.error("❌ Email ID does not exist in the database.")
        
def show_forgot_email_button() -> None:
    """Render the 'Forgot Email' button."""

    if st.button("🔍 Forgot my Email ID"):
        st.session_state["forgot_email_clicked"] = True

def show_volunteer_phone_identification() -> None:
    """Render the phone identification flow."""
    country_codes = utils.get_country_code_map()
    default_country_code_index = next(
                                        (
                                            index
                                            for index, cc in enumerate(country_codes)
                                            if cc.region == "IN"
                                        ),
                                        None,
                                    )

    required_label("🌍 Select Country Code")
    input_country = st.selectbox("", country_codes, 
                                    index=default_country_code_index, 
                                    label_visibility="collapsed",
                                    key="country_code")
    input_country_code = input_country.country_code

    required_label("📞 Phone Number")
    phone_number = st.text_input(
        "",
        placeholder="Enter phone number without country code",
        label_visibility="collapsed",
        key="phone_number"
    )

    if input_country_code and phone_number:
        if not phone_number.strip():
            st.error("Phone number is required.")
            return

        full_phone_number = f"+{input_country_code}{phone_number.strip()}"

        volunteer = volunteer_repo.get_latest_by_phone(full_phone_number, input_country.region)

        if volunteer is None:
            st.error("❌ Phone number does not exist in the database.")

            warning = setting_repo.get_by_key("VOLUNTEER_IDENTIFICATION_MSG")
            st.warning(f"⚠️ {warning.value}")

            if st.button("🔄 Retry"):
                st.session_state["forgot_email_clicked"] = False
                st.session_state["volunteer_identified"] = False
                st.session_state["volunteer"] = None
                st.rerun()

            return

        st.session_state["volunteer"] = volunteer
        st.session_state["volunteer_identified"] = True
        st.rerun()

    if st.session_state.get("volunteer_identified"):
        volunteer = st.session_state["volunteer"]

def show_volunteer_details() -> None:
    """Render the volunteer details."""
    volunteer = st.session_state.get("volunteer")
    if not volunteer:
        st.error("Volunteer not identified.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {volunteer.name}")
        st.write(f"**Departure Date:** {volunteer.departure_date.strftime("%b %d, %Y")}")

    with col2:
        st.write(f"**Volunteer Category:** {volunteer.volunteer_category}") 

def show_category_selection() -> None:
    """Render the category selection flow."""
    volunteer = st.session_state.get("volunteer")
    if not volunteer:
        st.error("Volunteer not identified.")
        return

    categories = category_repo.get_active_categories()
    category_options = {category.category: category for category in categories}

    required_label("📌 I want to reach out to:")
    input_category_name = st.selectbox(
        "", # ** No longer relevant
        list(category_options.keys()),
        index=None,
        key="input_category_name",
        label_visibility="collapsed",
    )

    if (input_category_name is not None) and (input_category_name in category_options):
        input_category = category_options[input_category_name]
        st.session_state["input_category"] = input_category
        return

    st.session_state.pop("input_category", None)

def show_subcategory_selection() -> None:
    """Render the subcategory selection flow."""
    volunteer = st.session_state.get("volunteer")
    if not volunteer:
        st.error("Volunteer not identified.")
        return

    # This field is used for form validation. 
    # I am assuming that if this function will be called only when sub category is required.
    st.session_state["is_sub_cat_req"] = True
    
    input_category = st.session_state.get("input_category")
    if not input_category:
        # st.error("Category not selected.")
        return

    filtered_subcategories = subcategory_repo.get_by_category_id_for_vol_cat(
                                input_category.category_id, 
                                volunteer.volunteer_category)

    subcategory_options = {subcategory.name: subcategory for subcategory in filtered_subcategories}

    required_label("📌 Sub Category")
    input_subcategory_name = st.selectbox(
        "", # ** No longer relevant
        list(subcategory_options.keys()),
        index = 0 if len(list(subcategory_options.keys())) == 1 else None, # Preselect if only 1 option is there
        key="input_subcategory_name",
        label_visibility="collapsed",
    )

    if (input_subcategory_name is not None) and (input_subcategory_name in subcategory_options):
        input_subcategory = subcategory_options[input_subcategory_name]
        st.session_state["input_subcategory"] = input_subcategory

        show_help_text(input_subcategory.help_text)

        return

    st.session_state.pop("input_subcategory", None)

def render_dynamic_dropdowns(sub_cat: SubCategory) -> None:
    dynamic_dropdowns = []
    for index, field_name in enumerate(sub_cat.dynamic_dropdown_fields):
        dynamic_dropdowns.append({
            "name": field_name,
            "is_req": True,
            "key_name": f"ddl_{index}"
        })

    st.session_state["dynamic_dropdowns"] = dynamic_dropdowns

    col1, col2 = st.columns(2)

    cur_col = col1
    for field in dynamic_dropdowns:
        with cur_col:
            option_values = parameter_repo.get_by_key(field["name"])
            if field["is_req"]:
                required_label(field["name"])
            
            st.selectbox(field["name"] if not field["is_req"] else "", 
                         option_values, index = None, 
                         key = field["key_name"],
                         label_visibility="collapsed",)

            cur_col = col1 if cur_col != col1 else col2

def render_dynamic_textbox(sub_cat: SubCategory) -> None:
    dynamic_textbox = []
    for index, field_name in enumerate(sub_cat.dynamic_textbox_fields):
        dynamic_textbox.append({
            "name": field_name,
            "is_req": True,
            "key_name": f"tb_{index}"
        })

    st.session_state["dynamic_textbox"] = dynamic_textbox

    col1, col2 = st.columns(2)

    cur_col = col1
    for field in dynamic_textbox:
        with cur_col:
            if field["is_req"]:
                required_label(field["name"])

            st.text_input(field["name"] if not field["is_req"] else "", 
                            placeholder=field["name"], key = field["key_name"],
                            label_visibility="collapsed",)

            cur_col = col1 if cur_col != col1 else col2

def show_program_selection() -> None:
    """Render the program selection flow."""
    volunteer = st.session_state.get("volunteer")
    if not volunteer:
        st.error("Volunteer not identified.")
        return

    # This field is used for form validation. 
    # I am assuming that if this function will be called only when program is required.
    st.session_state["is_program_req"] = True
    
    input_category = st.session_state.get("input_category")
    if not input_category:
        # st.error("Category not selected.")
        return

    programs = program_repo.get_by_category_and_gender(
                    input_category.category_id, 
                    volunteer.gender)

    program_options = {program.program_name: program for program in programs}

    required_label("📌 Program")
    input_program_name = st.selectbox(
        "", # ** No longer relevant
        list(program_options.keys()),
        index=None,
        key="input_program_name",
        label_visibility="collapsed",
    )

    if (input_program_name is not None) and (input_program_name in program_options):
        input_program = program_options[input_program_name]
        st.session_state["input_program"] = input_program

        show_help_text(input_program.help_text)

        return

    st.session_state.pop("input_program", None)

def show_program_dates_selection() -> None:
    """Render the program dates selection flow."""
    input_program = st.session_state.get("input_program")
    if not input_program:
        # st.error("Program not selected.")
        return

    # This field is used for form validation. 
    # I am assuming that if this function will be called only when program date is required.
    st.session_state["is_program_date_req"] = True

    # Assuming you have a method to get program dates based on the selected program
    program_dates = program_repo.get_program_dates_in_range(
                        input_program.program_id, 
                        volunteer.departure_date)

    if not program_dates:
        st.warning("No dates available for the selected program.")
        return

    required_label("📅 Select Program Date")
    input_date = st.selectbox(
        "",
        program_dates,
        index=None,
        key="input_date",
        label_visibility="collapsed",
    )

    info = setting_repo.get_by_key("PROGRAM_DATES_INFO_MSG")
    if info and not info.value.isspace():
        st.info(f"ℹ️ {info.value}")

    if input_date is not None:
        st.session_state["input_program_date"] = input_date
        return

    st.session_state.pop("input_program_date", None)

def show_custom_date_fields(program: Program) -> None:
    """Render the from date fields, conditionally."""
    if not program.show_from_date_input and not program.show_to_date_input:
        return

    from_date, to_date = None, None
    col1, col2 = st.columns(2)
    to_date_value = None
    max_date_value = date.today() + timedelta(days=90)

    with col1:
        if program.show_from_date_input:
            st.session_state["is_from_date_req"] = True

            required_label("📅 From Date")
            from_date = st.date_input("", format="DD/MM/YYYY", key="from_date",
                                      label_visibility="collapsed",
                                      max_value=max_date_value)

            to_date_value = from_date + timedelta(days = program.duration_in_days if program.duration_in_days > 0 else 1)

    with (col1 if not program.show_from_date_input else col2): # both columns should be used only when both date fields need to be shown
        if program.show_to_date_input:
            st.session_state["is_to_date_req"] = True

            required_label("📅 To Date")
            to_date = st.date_input("", value = to_date_value, format="DD/MM/YYYY", key="to_date",
                                    label_visibility="collapsed",
                                    max_value=max_date_value)

    if from_date:
        st.session_state["input_from_date"] = from_date
    else:
        st.session_state.pop("input_from_date", None)

    if to_date:
        st.session_state["input_to_date"] = to_date
    else:
        st.session_state.pop("input_to_date", None)

def show_coordinator_email_input() -> None:
    """Render the coordinator email input, validate and store in session state."""

    # This field is used for form validation. 
    # I am assuming that if this function will be called only when coordinator email is required.
    st.session_state["is_coordinator_email_req"] = True

    required_label("📧 Seva Coordinator Mail ID")
    coordinator_email = st.text_input(
        "",
        placeholder="Enter your Seva Coordinator Mail ID",
        value=st.session_state.get("coordinator_email", ""),
        key="coordinator_email",
        label_visibility="collapsed",
    )

    if coordinator_email is not None and coordinator_email != "":
        normalized = utils.normalize_email(coordinator_email)

        # Simple email validation: non-empty local part, an @, and a domain with a dot
        email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        if normalized is None or not email_regex.match(normalized):
            st.error("Please enter a valid coordinator email address.")
        else:
            st.session_state["input_coordinator_email"] = normalized    
            return

    st.session_state.pop("input_coordinator_email", None)
    
def show_description_box() -> None:
    """Render the description box."""
    required_label("📝 Reason for your request")
    description = st.text_area(
        "",
        placeholder="Please fill in with as much detail as possible",
        height=150,
        key="description",
        label_visibility="collapsed",
    )

    if description:
        st.session_state["input_description"] = description
        return

    st.session_state.pop("input_description", None)

def show_submit_button():
    """Render the submit button"""
    submit = st.button("Submit Request", key="submit")
    if not submit:
        return

    validation_results = []
    
    validation_results.append(
        validate_required(
            st.session_state.get("input_category", ""), 
            "⚠️ Please select a Request Type.")
    )

    is_sub_cat_req = st.session_state.get("is_sub_cat_req", False)
    if is_sub_cat_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_subcategory", ""), 
                "⚠️ Please select a Sub Category.")
        )

    dynamic_dropdowns = st.session_state.get("dynamic_dropdowns", None)
    if dynamic_dropdowns:
        for field in dynamic_dropdowns:
            if field["is_req"]:
                validation_results.append(
                    validate_required(
                        st.session_state.get(field["key_name"], ""),
                        f"⚠️ '{field["name"]}' is required."
                    )
                )


    dynamic_textbox = st.session_state.get("dynamic_textbox", None)
    if dynamic_textbox:
        for field in dynamic_textbox:
            if field["is_req"]:
                validation_results.append(
                    validate_required(
                        st.session_state.get(field["key_name"], ""),
                        f"⚠️ '{field["name"]}' is required."
                    )
                )

    is_program_req = st.session_state.get("is_program_req", False)
    if is_program_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_program", None), 
                "⚠️ Please select a Program.")
        )

    is_program_date_req = st.session_state.get("is_program_date_req", False)
    if is_program_date_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_program_date", None), 
                "⚠️ Please select a Program Date.")
        )

    is_from_date_req = st.session_state.get("is_from_date_req", False)
    if is_from_date_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_from_date", None), 
                "⚠️ Please select the From Date.")
        )

    is_to_date_req = st.session_state.get("is_to_date_req", False)
    if is_to_date_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_to_date", None), 
                "⚠️ Please select the To Date.")
        )

    from_date = st.session_state.get("input_from_date", None)
    to_date = st.session_state.get("input_to_date", None)

    if from_date and to_date:
        if from_date >= to_date:
            st.error("❌ From Date cannot be later than To Date.")
            validation_results.append(False)

        if (from_date >= volunteer.departure_date or 
            to_date >= volunteer.departure_date):
            st.error("❌ Input date cannot be later than your departure date. Please request extension if needed.")
            validation_results.append(False)
        

    is_coordinator_email_req = st.session_state.get("is_coordinator_email_req", False)
    if is_coordinator_email_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_coordinator_email", None), 
                "⚠️ Please enter the Coordinator Mail.")
        )

    validation_results.append(
        validate_required(
                st.session_state.get("input_description", ""), 
                "⚠️ Please fill in the reason.")
        )

    if not all(validation_results):
        return

    req: Request = None
    document_lock = threading.Lock()
    with document_lock:
        req = save_record()

    return req

def show_help_text(help_text: str) -> None:
    """Render the help text."""
    help_text = help_text.replace("\n", "<br />")

    if help_text:
        st.markdown(f"""
            <div style='color: #555555; background-color: #f8f9fa; padding: 12px; border-radius: 8px; font-size: 14px;'>
                {help_text}
            </div>""", 
            unsafe_allow_html=True)

def validate_required(value: Any, error_message: str) -> bool:
    """Validate a required Streamlit input."""

    if value is None:
        st.error(error_message)
        return False

    if isinstance(value, str) and not value.strip():
        st.error(error_message)
        return False

    return True

def save_record():
    volunteer = st.session_state["volunteer"]
    vol_cat = vol_cat_repo.get_by_id(volunteer.volunteer_category)
                                           
    category = st.session_state["input_category"]
    subcategory = st.session_state.get("input_subcategory", None)
    program = st.session_state.get("input_program", None)

    from_date = None
    to_date = None
    program_date = None
    coordinator_email = None
    team_id = None

    # from-to date assignment && coordinator assignment
    is_program_date_req = st.session_state.get("is_program_date_req", False)
    if is_program_date_req:
        program_date = st.session_state["input_program_date"]
        from_date, to_date = program_date.start_date, program_date.end_date

    if subcategory is not None:
        if subcategory.show_from_date_input:
            from_date = st.session_state["input_from_date"]
        if subcategory.show_to_date_input:
            to_date = st.session_state["input_to_date"]
        if subcategory.show_coordinator_email_input:
            coordinator_email = st.session_state["input_coordinator_email"]

        team_id = subcategory.team_id

    if program is not None:
        if program.show_from_date_input:
            from_date = st.session_state["input_from_date"]
        if program.show_to_date_input:
            to_date = st.session_state["input_to_date"]
        if program.show_coordinator_email_input:
            coordinator_email = st.session_state["input_coordinator_email"]

        team_map = program_repo.get_assigned_team(program.program_id, volunteer.volunteer_category)
        team_id = team_map.team_id

    # Prepare description

    description = st.session_state["input_description"]

    dynamic_dropdowns = st.session_state.get("dynamic_dropdowns", None)
    if dynamic_dropdowns:
        for field in dynamic_dropdowns:
            value = st.session_state[field["key_name"]]
            description += f"\n{field["name"]}: {value}"
    

    dynamic_textbox = st.session_state.get("dynamic_textbox", None)
    if dynamic_textbox:
        for field in dynamic_textbox:
            value = st.session_state[field["key_name"]]
            description += f"\n{field["name"]}: {value}"

    if coordinator_email and not coordinator_email.isspace():
        description += f"\nSeva Coordinator Mail ID: {coordinator_email}"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing_request_ids = request_repo.get_existing_ids()
    req = Request(
        request_id = utils.generate_request_id(vol_cat.request_label, existing_request_ids),
        person_id = volunteer.person_id,
        visit_id = volunteer.visit_id,
        name = volunteer.name,
        gender = volunteer.gender,
        email_id = volunteer.email_id,
        phone_number = volunteer.phone_number,
        volunteer_category = volunteer.volunteer_category, # !! Need to ask if the code or full label should go here
        request_type = category.category,
        sub_category = subcategory.name if subcategory != None else program.program_name,
        sub_category_id = subcategory.sub_category_id if subcategory != None else "",
        from_date = from_date,
        to_date = to_date,
        description = description,
        timestamp = timestamp,
        assigned_department = team_id,
        status = utils.get_setting("defaultRequestStatus"),
        status_sub_type = utils.get_setting("defaultRequestStatusSubType"), # to be left empty initially
        last_edited = timestamp,

        program_date_id = program_date.program_date_id if program_date is not None else None,
        coordinator_email_id = coordinator_email
    )

    request_repo.write_to_sheet(req)

    return req

def reset_req_flags():
    """
    Resets required flag, which are being used by validate method to be determine what is required.
    """

    st.session_state.pop("is_sub_cat_req", None)
    st.session_state.pop("is_program_req", None)
    st.session_state.pop("is_program_date_req", None)
    st.session_state.pop("is_from_date_req", None)
    st.session_state.pop("is_to_date_req", None)
    st.session_state.pop("is_coordinator_email_req", None)

def required_label(label: str) -> None:
    st.markdown(
        f"""
        <label class="required-label">
            {label}&nbsp;<span class="required-star">*</span>
        </label>
        """,
        unsafe_allow_html=True,
    )

def send_mail_requester(request: Request) -> None:
    """Send the request notification to the requester."""

    email_service._send_template_email(
        request=request,
        # recipient=request.email_id,
        recipient="yogesh.jaykar-ext@gmail.com",
        template_name=email_service.TEMPLATE_REQUESTER,
    )

def send_mail_team(request: Request) -> None:
    """Send the request notification to the assigned team."""

    team = team_repo.get_by_id(request.assigned_department)

    email_service._send_template_email(
        request=request,
        # recipient=team.contact_email,
        recipient="yogesh.jaykar-ext@gmail.com",
        template_name=email_service.TEMPLATE_TEAM,
    )

def send_mail_secondary_email(request: Request, secondary_email: str) -> None:
    """Send the request notification to a secondary email address."""

    email_service._send_template_email(
        request=request,
        # recipient=secondary_email,
        recipient="yogesh.jaykar-ext@gmail.com",
        template_name=email_service.TEMPLATE_SECONDARY_EMAIL,
    )

def send_mail_coordinator(request: Request) -> None:
    """Send the request notification to the coordinator."""

    coordinator_email = request.coordinator_email_id

    email_service._send_template_email(
        request=request,
        # recipient=coordinator_email,
        recipient="yogesh.jaykar-ext@gmail.com",
        template_name=email_service.TEMPLATE_COORDINATOR,
    )

if __name__ == "__main__":
    st.title("🔹 Raise a Request")

    reset_req_flags()

    load_css()
    if st.session_state.get("state") == "Identification":
        show_volunteer_email_identification()
        show_forgot_email_button()
    
        if st.session_state.get("forgot_email_clicked"):
            show_volunteer_phone_identification()

    elif st.session_state.get("state") == "Form":
        volunteer = st.session_state.get("volunteer")
        if volunteer:
            show_volunteer_details()

            show_category_selection()
            input_category = st.session_state.get("input_category")
            if input_category != None:
                if input_category.has_programs:
                    show_program_selection()
                else:
                    show_subcategory_selection()

            input_subcategory = st.session_state.get("input_subcategory")
            if input_subcategory != None:
                render_dynamic_dropdowns(input_subcategory)
                render_dynamic_textbox(input_subcategory)
                show_custom_date_fields(input_subcategory)

                if input_subcategory.show_coordinator_email_input:
                    show_coordinator_email_input()

            input_program = st.session_state.get("input_program")
            if input_program != None:
                if (not input_program.show_from_date_input and 
                    not input_program.show_to_date_input):
                    show_program_dates_selection()
                else:
                    show_custom_date_fields(input_program)

                if input_program.show_coordinator_email_input:
                    show_coordinator_email_input()

            show_description_box()
            req = show_submit_button()

            # send emails
            # if req:
            #     send_mail_requester(req)
            #     send_mail_team(req)
            #     if input_subcategory != None and input_subcategory.secondary_email:
            #         send_mail_secondary_email(req, input_subcategory.secondary_email)

            #     send_mail_coordinator(req)