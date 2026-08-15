from datetime import datetime, timedelta
from typing import Any

import streamlit as st
import utils
import re

from entities import Program, Request
from repository import CategoryRepository, ProgramRepository, RequestRepository, SubCategoryRepository, TeamRepository, VolunteerRepository

volunteer_repository = VolunteerRepository()
team_repository = TeamRepository()
category_repository = CategoryRepository()
subcategory_repository = SubCategoryRepository()
program_repository = ProgramRepository()
request_repository = RequestRepository()

if "state" not in st.session_state:
    st.session_state["state"] = "Identification"
elif "volunteer_identified" in st.session_state and st.session_state["volunteer_identified"]:
    st.session_state["state"] = "Form"

    # These fields are requried for validating the form
    # Initializing the states, actual values would be put while the fields are rendered
    st.session_state["is_sub_cat_selection"] = False
    st.session_state["is_program_selection"] = False
    st.session_state["is_program_date_selection"] = False
    st.session_state["is_coordinator_email_req"] = False

def show_volunteer_email_identification() -> None:
    """Render the Volunteer identification flow."""
    # st.header("👤 Volunteer Identification")

    email = st.text_input(
        "📧 Email ID",
        placeholder="Enter your email ID",
    )

    if email:
        if not email.strip():
            st.error("Please enter your email ID.")
            return

        volunteer = volunteer_repository.get_latest_by_email(email)

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
    country_code_map = utils.get_country_code_map()

    input_country = st.selectbox("🌍 Select Country Code", 
        list(country_code_map.keys()), 
        index=list(country_code_map.keys()).index("IN (+91)"))
    input_country_code = country_code_map[input_country]

    phone_number = st.text_input(
        "📞 Phone Number",
        placeholder="Enter phone number without country code",
    )

    if input_country_code and phone_number:
        if not phone_number.strip():
            st.error("Phone number is required.")
            return

        full_phone_number = f"{input_country_code}{phone_number.strip()}"

        volunteer = volunteer_repository.get_latest_by_phone(
            full_phone_number,
        )

        if volunteer is None:
            st.error("❌ Phone number does not exist in the database.")
            st.warning(
                "⚠️ Please check your details and try again."
            )

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

    categories = category_repository.get_active_categories()
    category_options = {category.category: category for category in categories}

    input_category_name = st.selectbox(
        "📌 I want to reach out to:", # ** No longer relevant
        list(category_options.keys()),
        index=None
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
    st.session_state["is_sub_cat_selection"] = True
    
    input_category = st.session_state.get("input_category")
    if not input_category:
        # st.error("Category not selected.")
        return

    filtered_subcategories = subcategory_repository.get_by_category_id_for_vol_cat(
                                input_category.category_id, 
                                volunteer.volunteer_category)

    subcategory_options = {subcategory.name: subcategory for subcategory in filtered_subcategories}

    input_subcategory_name = st.selectbox(
        "📌 Sub Category", # ** No longer relevant
        list(subcategory_options.keys()),
        index=None
    )

    if (input_subcategory_name is not None) and (input_subcategory_name in subcategory_options):
        input_subcategory = subcategory_options[input_subcategory_name]
        st.session_state["input_subcategory"] = input_subcategory

        show_help_text(input_subcategory.help_text)

        return

    st.session_state.pop("input_subcategory", None)

def show_program_selection() -> None:
    """Render the program selection flow."""
    volunteer = st.session_state.get("volunteer")
    if not volunteer:
        st.error("Volunteer not identified.")
        return

    # This field is used for form validation. 
    # I am assuming that if this function will be called only when program is required.
    st.session_state["is_program_selection"] = True
    
    input_category = st.session_state.get("input_category")
    if not input_category:
        # st.error("Category not selected.")
        return

    programs = program_repository.get_by_category_and_gender(
                    input_category.category_id, 
                    volunteer.gender)

    program_options = {program.program_name: program for program in programs}

    input_program_name = st.selectbox(
        "📌 Program", # ** No longer relevant
        list(program_options.keys()),
        index=None
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
    st.session_state["is_program_date_selection"] = True

    # Assuming you have a method to get program dates based on the selected program
    program_dates = program_repository.get_program_dates_in_range(
                        input_program.program_id, 
                        volunteer.departure_date)

    if not program_dates:
        st.warning("No dates available for the selected program.")
        return

    input_date = st.selectbox(
        "📅 Select Program Date",
        program_dates,
        index=None
    )

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

    with col1:
        if program.show_from_date_input:
            from_date = st.date_input("📅 From Date", format="DD/MM/YYYY")
            to_date_value = from_date + timedelta(days = program.duration_in_days)

    with (col1 if not program.show_from_date_input else col2): # both columns should be used only when both date fields need to be shown
        if program.show_to_date_input:
            to_date = st.date_input("📅 To Date", value = to_date_value, format="DD/MM/YYYY")

    if from_date and to_date:
        if from_date > to_date:
            st.error("From Date cannot be later than To Date.")
            return

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

    coordinator_email = st.text_input(
        "📧 Seva Coordinator Mail ID",
        placeholder="Enter your Seva Coordinator Mail ID",
        value=st.session_state.get("coordinator_email", "")
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
    description = st.text_area(
        "📝  Reason for your request",
        placeholder="Please fill in with as much detail as possible",
        height=150,
    )

    if description:
        st.session_state["input_description"] = description
        return

    st.session_state.pop("input_description", None)

def show_submit_button():
    """Render the submit button"""
    submit = st.button("Submit Request")
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

    # save_record()

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

# def save_record():
#     volunteer = st.session_state["volunteer"]
#     category = st.session_state["input_category"]
#     subcategory = st.session_state.get("input_subcategory", None)
#     program = st.session_state.get("input_program", None)

#     from_date = None
#     to_date = None
#     coordinator_email = None
#     team = None

#     # from-to date assignment && coordinator assignment
#     is_program_date_req = st.session_state.get("is_program_date_req", False)
#     if is_program_date_req:
#         program_date = st.session_state["input_program_date"]
#         from_date, to_date = program_date.start_date, program_date.end_date

#     if subcategory is not None:
#         if subcategory.show_from_date_input:
#             from_date = st.session_state["input_from_date"]
#         if subcategory.show_to_date_input:
#             to_date = st.session_state["input_to_date"]
#         if subcategory.show_coordinator_email_input:
#             coordinator_email = st.session_state["input_coordinator_email"]

#         team = subcategory.team_id

#     if program is not None:
#         if program.show_from_date_input:
#             from_date = st.session_state["input_from_date"]
#         if program.show_to_date_input:
#             to_date = st.session_state["input_to_date"]
#         if program.show_coordinator_email_input:
#             coordinator_email = st.session_state["input_coordinator_email"]

#     description = st.session_state["input_description"]
#     if coordinator_email and not coordinator_email.isspace():
#         description += f"\nSeva Coordinator Mail ID: {coordinator_email}"

#     # team assignment

#     req = Request(
#         request_id = ,
#         person_id = volunteer.person_id,
#         visit_id = volunteer.visit_id,
#         name = volunteer.name,
#         gender = volunteer.gender,
#         email_id = volunteer.email_id,
#         phone_number = volunteer.phone_number,
#         volunteer_category = volunteer.volunteer_category, # !! Need to ask if the code or full label should go here
#         request_type = category.category,
#         sub_category = subcategory.name if subcategory != None else program.program_name,
#         from_date = from_date,
#         to_date = to_date,
#         description = description,
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         request_status = "New",
#         assigned_department = 
#         system_id = 
        
#     )

#     request_repository.write_to_sheet(req)



if __name__ == "__main__":
    st.title("🔹 Raise a Request")

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
            show_submit_button()
                


    
        

    

    
