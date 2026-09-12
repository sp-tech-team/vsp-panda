from datetime import date, datetime, timedelta
from pathlib import Path
import traceback
from typing import Any

import streamlit as st
import threading

import streamlit.components.v1 as components
import utils
import re
import time

from entities import Bathroom, FloorNum, Log, Request, Room, Shower, StayArea, SubCategory
from repository import BathroomRepository, BunkNumRepository, CategoryRepository, FloorNumRepository, LogRepository, ParameterRepository, RoomRepository, RequestRepository, SettingRepository, ShowerRepository, StayAreaRepository, SubCategoryRepository, VolunteerCategoryRepository, VolunteerRepository
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

import logging
import streamlit as st

from db_logger import PostgreSQLHandler


logger = logging.getLogger("vsp_panda")
logger.setLevel(logging.INFO)

def setup_logger():

    if logger.handlers:
        return

    # Terminal logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Neon PostgreSQL logging
    db_handler = PostgreSQLHandler()
    db_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    logger.addHandler(db_handler)


setup_logger()

st.set_page_config(
    page_title="VSP Panda",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Hide the entire Streamlit top-right toolbar */
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

bathroom_repo = BathroomRepository()
bunk_num_repo = BunkNumRepository()
category_repo = CategoryRepository()
floor_num_repo = FloorNumRepository()
setting_repo = SettingRepository()
parameter_repo = ParameterRepository()
room_repo = RoomRepository()
setting_repo = SettingRepository()
shower_repo = ShowerRepository()
stay_area_repo = StayAreaRepository ()
subcategory_repo = SubCategoryRepository()
vol_cat_repo = VolunteerCategoryRepository()
volunteer_repo = VolunteerRepository()
StayExtensionCatIdFromTable = utils.get_setting("StayExtensionCatIdFromTable")


if "volunteer_identified" in st.session_state and st.session_state["volunteer_identified"]:
    st.session_state["state"] = "Form"

    # These fields are requried for validating the form
    # Initializing the states, actual values would be put while the fields are rendered
    st.session_state["is_sub_cat_req"] = False
    st.session_state["is_program_selection"] = False
    st.session_state["is_program_date_req"] = False
    st.session_state["is_coordinator_email_req"] = False
elif "state" not in st.session_state or not st.session_state["state"]:
    st.session_state["state"] = "Identification"

def load_css() -> None:
    """Load application CSS."""

    css_path = Path(__file__).parent / "styles" / "style.css"
    css = css_path.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )

def load_js() -> None:
    """Load application JS."""

    js_path = Path(__file__).parent / "js" / "main.js"
    js = js_path.read_text(encoding="utf-8")

    components.html(
        f"""
        <script>
            {js}
        </script>
        """,
        height=0,
    )

def show_volunteer_email_identification() -> None:
    """Render the Volunteer identification flow."""
    # st.header("👤 Volunteer Identification")

    required_label("📧 Email ID")
    email = st.text_input(
        ".",
        placeholder="Enter your email ID",
        label_visibility="collapsed",
        key="email_id"
    )

    if email:
        if not email.strip():
            st.error("Please enter your email ID.")
            return

        volunteer, return_msg = volunteer_repo.get_latest_by_email(email)

        if volunteer is not None and not return_msg:
            st.session_state["volunteer"] = volunteer
            st.session_state["volunteer_identified"] = True

            if st.session_state.get("volunteer_identified"):
                volunteer = st.session_state["volunteer"]
                # Log the identification success
                logger.info(
                                    f"Identified user." + 
                                    f"Visit ID: {volunteer.visit_id} | " + 
                                    f"Person ID: {volunteer.person_id} | " + 
                                    f"Volunteer ID: {volunteer.volunteer_id}",
                                    extra={
                                        "ip_address": utils.get_client_ip(),
                                        "vol_email_id": volunteer.email_id if volunteer else "",
                                        "vol_phone_num": volunteer.phone_number if volunteer else "",
                                    }
                                )
                # log_repo = LogRepository()

                # now: datetime = datetime.now()
                # log: Log = Log(
                #     log_id = f"L-{now.strftime("%y%m%d-%H%M%S")}",
                #     ip_address = utils.get_client_ip(),
                #     email_id = volunteer.email_id,
                #     phone_number = volunteer.phone_number,
                #     message = f"Identified user." + 
                #                 f"Visit ID: {volunteer.visit_id} | " + 
                #                 f"Person ID: {volunteer.person_id} | " + 
                #                 f"Volunteer ID: {volunteer.volunteer_id}",
                #     timestamp = now
                # )
                # log_repo.write_to_sheet(log)

                st.rerun()

        st.error("❌ Email ID does not exist in the database.")

        # Log the identification failure

        logger.exception(
                        f"Failed to identify user. Email: {email}. {return_msg}",
                        extra={
                                "ip_address": utils.get_client_ip(),
                                "vol_email_id": email,
                                "vol_phone_num": "",
                                }
                    )

        # log_repo = LogRepository()

        # now: datetime = datetime.now()
        # log: Log = Log(
        #     log_id = f"L-{now.strftime("%y%m%d-%H%M%S")}",
        #     ip_address = utils.get_client_ip(),
        #     message = f"Failed to identify user. Email: {email}. {return_msg}",
        #     timestamp = now
        # )
        # log_repo.write_to_sheet(log)
        
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
    input_country = st.selectbox(".", country_codes, 
                                    index=default_country_code_index, 
                                    label_visibility="collapsed",
                                    placeholder="Select country code",
                                    key="country_code")
    input_country_code = input_country.country_code

    required_label("📞 Phone Number")
    phone_number = st.text_input(
        ".",
        placeholder="Enter phone number without country code",
        label_visibility="collapsed",
        key="phone_number"
    )

    if input_country_code and phone_number:
        if not phone_number.strip():
            st.error("Phone number is required.")
            return

        full_phone_number = f"+{input_country_code}{phone_number.strip()}"

        volunteer, return_msg = volunteer_repo.get_latest_by_phone(full_phone_number, input_country.region,input_country_code,phone_number.strip())

        if volunteer is None or return_msg:
            st.error("❌ Phone number does not exist in the database.")

            warning = setting_repo.get_by_key("REACH_OUT_TO_ADD_CREDENTIALS_FORM_MSG")
            st.warning(f"⚠️ {warning.value}")

            # Log the identification failure

            logger.error(
                            f"Failed to identify user. Phone: {phone_number}. {return_msg}",
                            extra={
                                    "ip_address": utils.get_client_ip(),
                                    "vol_email_id": "",
                                    "vol_phone_num": phone_number,
                                  }
                        )

            # log_repo = LogRepository()

            # now: datetime = datetime.now()
            # log: Log = Log(
            #     log_id = f"L-{now.strftime("%y%m%d-%H%M%S")}",
            #     ip_address = utils.get_client_ip(),
            #     message = f"Failed to identify user. Phone: {phone_number}. {return_msg}",
            #     timestamp = now
            # )
            # log_repo.write_to_sheet(log)

            if st.button("🔄 Retry"):
                st.session_state["forgot_email_clicked"] = False
                st.session_state["volunteer_identified"] = False
                st.session_state["volunteer"] = None
                st.rerun()

            return

        st.session_state["volunteer"] = volunteer
        st.session_state["volunteer_identified"] = True

        # Log the identification success

        logger.info(
                    f"Identified user." + 
                    f"Visit ID: {volunteer.visit_id} | " + 
                    f"Person ID: {volunteer.person_id} | " + 
                    f"Volunteer ID: {volunteer.volunteer_id}",
                        extra={
                                "ip_address": utils.get_client_ip(),
                                "vol_email_id": volunteer.email_id,
                                "vol_phone_num": volunteer.phone_number,
                              }
                    )

        # log_repo = LogRepository()

        # now: datetime = datetime.now()
        # log: Log = Log(
        #     log_id = f"L-{now.strftime("%y%m%d-%H%M%S")}",
        #     ip_address = utils.get_client_ip(),
        #     email_id = volunteer.email_id,
        #     phone_number = volunteer.phone_number,
        #     message = f"Identified user." + 
        #                 f"Visit ID: {volunteer.visit_id} | " + 
        #                 f"Person ID: {volunteer.person_id} | " + 
        #                 f"Volunteer ID: {volunteer.volunteer_id}",
        #     timestamp = now
        # )
        # log_repo.write_to_sheet(log)

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

def get_categories_with_subcategories(
    categories,
    volunteer,
    subcategory_repo
):
    valid_categories = []

    for category in categories:

        if category.has_programs:
            filtered_subcategories = (
                subcategory_repo.get_by_category_and_gender(
                    category.category_id,
                    volunteer.gender,
                    volunteer.volunteer_category
                )
            )
        else:
            filtered_subcategories = (
                subcategory_repo.get_by_category_id_for_vol_cat(
                    category.category_id,
                    volunteer.volunteer_category
                )
            )

        # Keep category only if it has at least one sub-category
        if filtered_subcategories:
            valid_categories.append(category)

    return valid_categories

def show_category_selection(col) -> None:
    """Render the category selection flow."""
    with col:
        volunteer = st.session_state.get("volunteer")
        if not volunteer:
            st.error("Volunteer not identified.")
            return

        categories = category_repo.get_active_categories()
        filtered_categories = get_categories_with_subcategories(
                            categories,
                            volunteer,
                            subcategory_repo
                        )
        category_options = {category.category: category for category in filtered_categories}

        # To debug what is there in the session state
        # st.write("CATEGORY STATE:", {
        #     k: v for k, v in st.session_state.items()
        #     if "categor" in k.lower()
        # })

        required_label("📌 I want to reach out to:")
        input_category_name = st.selectbox(
            ".", # ** No longer relevant
            list(category_options.keys()),
            index=None,
            key="input_category_name",
            label_visibility="collapsed",
            placeholder="Select Category",
        )

        if (input_category_name is not None) and (input_category_name in category_options):
            input_category = category_options[input_category_name]
            st.session_state["input_category"] = input_category
            return

        st.session_state.pop("input_category", None)
        st.session_state.pop("input_category_name", None)

def show_subcategory_selection(col) -> None:
    """Render the subcategory selection flow."""
    with col:
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

        filtered_subcategories = []
        if input_category.has_programs:
            filtered_subcategories = subcategory_repo.get_by_category_and_gender(
                                                input_category.category_id, 
                                                volunteer.gender,
                                                volunteer.volunteer_category)
        else:
            filtered_subcategories = subcategory_repo.get_by_category_id_for_vol_cat(
                                        input_category.category_id, 
                                        volunteer.volunteer_category)

        subcategory_options = {subcategory.name: subcategory for subcategory in filtered_subcategories}
        subcategory_names = list(subcategory_options.keys())

        subcategory_names = list(subcategory_options.keys())

        if not subcategory_names:
            # No subcategories
            options = ["No applicable values to select"]
            index = 0
            disabled = True
            placeholder = None

            st.warning("⚠️ The selected category is inapplicable to you, kindly change it. ")
            return        

        elif len(subcategory_names) == 1:
            # Only one subcategory - preselect it
            options = subcategory_names
            index = 0
            disabled = False
            placeholder = None

        else:
            # Multiple subcategories - ask user to select
            options = subcategory_names
            index = None
            disabled = False
            placeholder = "Select Sub Category"

        required_label("📌 Sub Category")
        input_subcategory_name = st.selectbox(
            ".",
            options,
            index=index,
            key="input_subcategory_name",
            label_visibility="collapsed",
            disabled=disabled,
            placeholder=placeholder
        )

        
        # input_subcategory_name = st.selectbox(
        #     "", # ** No longer relevant
        #     subcategory_names,
        #     index = 0 if len(list(subcategory_options.keys())) == 1 else None, # Preselect if only 1 option is there
        #     key = "input_subcategory_name",
        #     label_visibility = "collapsed",
        #     disabled=not bool(subcategory_options),
        #     placeholder = "Select Sub Category"
        # )

        if (input_subcategory_name is not None) and (input_subcategory_name in subcategory_options):
            input_subcategory = subcategory_options[input_subcategory_name]
            st.session_state["input_subcategory"] = input_subcategory

            show_help_text(input_subcategory.help_text)

            return

        st.session_state.pop("input_subcategory", None)
        st.session_state.pop("input_subcategory_name", None)

def render_dynamic_dropdowns(sub_cat: SubCategory) -> None:
    dynamic_dropdowns = []

    if sub_cat.dynamic_dropdown_fields != []:
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
                        label_visibility = "collapsed",
                        placeholder = f"Select {field["name"]}")

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

def show_accomodation_fields() -> None:
    """Render the accomodation fields."""
    # This field is used for form validation. 
    # I am assuming that if this function will be called only when accomodation fields is required.
    st.session_state["is_stay_area_req"] = True
    st.session_state["is_room_req"] = True
    st.session_state["is_bathroom_req"] = True
    st.session_state["is_floor_num_req"] = True
    st.session_state["is_shower_req"] = True

    col1, col2 = st.columns(2)

    with col1:
        # Stay Area
        stay_area_na = StayArea(
            stay_area_id = "N/A",
            stay_area_name = "N/A",
            is_active = True
        )

        stay_areas = [ stay_area_na ]
        stay_areas.extend(stay_area_repo.get_active_stay_areas())

        stay_areas_options = {stay_area.stay_area_name: stay_area for stay_area in stay_areas}

        required_label("Stay Area")
        input_stay_area_name = st.selectbox(
            ".", # ** No longer relevant
            list(stay_areas_options.keys()),
            index=None,
            key="input_stay_area_name",
            label_visibility="collapsed",
            placeholder="Select Stay Area",
        )
        st.caption("Please select 'N/A' if stay area is not applicable.")

        input_stay_area = None
        if (input_stay_area_name is not None) and (input_stay_area_name in stay_areas_options):
            input_stay_area = stay_areas_options[input_stay_area_name]
            st.session_state["input_stay_area"] = input_stay_area
        else:
            st.session_state.pop("input_stay_area", None)
            st.session_state.pop("input_stay_area_name", None)

        # Rooms

        room_na = Room(
            room_id = "N/A",
            stay_area_id = "N/A",
            room_num = "N/A",
            is_active = True
        )

        rooms = [ room_na ]
        rooms.extend(room_repo.get_active_rooms(input_stay_area))

        rooms_options = {room.room_num: room for room in rooms}

        required_label("Room")
        input_room_name = st.selectbox(
            "", # ** No longer relevant
            list(rooms_options.keys()),
            index=None,
            key="input_room_name",
            label_visibility="collapsed",
            placeholder="Select Room",
        )
        st.caption("Please select 'N/A' if room is not applicable.")

        if (input_room_name is not None) and (input_room_name in rooms_options):
            input_room = rooms_options[input_room_name]
            st.session_state["input_room"] = input_room
        else:
            st.session_state.pop("input_room", None)
            st.session_state.pop("input_room_name", None)

        # Bathrooms

        bathroom_na = Bathroom(
            bathroom_id = "N/A",
            stay_area_id = "N/A",
            bathroom_num = "N/A",
            is_active = True
        )

        bathrooms = [ bathroom_na ]
        bathrooms.extend(bathroom_repo.get_active_bathrooms(input_stay_area))

        bathrooms_options = {bathroom.bathroom_num: bathroom for bathroom in bathrooms}

        required_label("Bathrooms")
        input_bathroom_name = st.selectbox(
            ".", # ** No longer relevant
            list(bathrooms_options.keys()),
            index=None,
            key="input_bathroom_name",
            label_visibility="collapsed",
            placeholder="Select Bathroom",
        )
        st.caption("Please select 'N/A' if bathroom is not applicable.")

        if (input_bathroom_name is not None) and (input_bathroom_name in bathrooms_options):
            input_bathroom = bathrooms_options[input_bathroom_name]
            st.session_state["input_bathroom"] = input_bathroom
        else:
            st.session_state.pop("input_bathroom", None)
            st.session_state.pop("input_bathroom_name", None)

    with col2:
        # Floor Number
        floor_num_na = FloorNum(
            floor_id = "N/A",
            floor_num = "N/A",
            is_active = True
        )

        floor_nums = [ floor_num_na ]
        floor_nums.extend(floor_num_repo.get_active_floor_nums())

        floor_nums_options = {floor_num.floor_num: floor_num for floor_num in floor_nums}

        required_label("Floor Number")
        input_floor_num_name = st.selectbox(
            ".", # ** No longer relevant
            list(floor_nums_options.keys()),
            index=None,
            key="input_floor_num_name",
            label_visibility="collapsed",
            placeholder="Select Floor Number",
        )
        st.caption("Please select 'N/A' if floor number is not applicable.")

        if (input_floor_num_name is not None) and (input_floor_num_name in floor_nums_options):
            input_floor_num = floor_nums_options[input_floor_num_name]
            st.session_state["input_floor_num"] = input_floor_num
        else:
            st.session_state.pop("input_floor_num", None)
            st.session_state.pop("input_floor_num_name", None)

        # Showers

        shower_na = Shower(
            shower_id = "N/A",
            stay_area_id = "N/A",
            shower_num = "N/A",
            is_active = True
        )

        showers = [ shower_na ]
        showers.extend(shower_repo.get_active_showers(input_stay_area))

        showers_options = {shower.shower_num: shower for shower in showers}

        required_label("Showers")
        input_shower_name = st.selectbox(
            ".", # ** No longer relevant
            list(showers_options.keys()),
            index=None,
            key="input_shower_name",
            label_visibility="collapsed",
            placeholder="Select Shower",
        )
        st.caption("Please select 'N/A' if shower is not applicable.")

        if (input_shower_name is not None) and (input_shower_name in showers_options):
            input_shower = showers_options[input_shower_name]
            st.session_state["input_shower"] = input_shower
        else:
            st.session_state.pop("input_shower", None)
            st.session_state.pop("input_shower_name", None)

# def show_program_selection() -> None:
#     """Render the program selection flow."""
#     volunteer = st.session_state.get("volunteer")
#     if not volunteer:
#         st.error("Volunteer not identified.")
#         return

#     # This field is used for form validation. 
#     # I am assuming that if this function will be called only when program is required.
#     st.session_state["is_program_req"] = True
    
#     input_category = st.session_state.get("input_category")
#     if not input_category:
#         # st.error("Category not selected.")
#         return

#     programs = subcategory_repo.get_by_category_and_gender(
#                     input_category.category_id, 
#                     volunteer.gender)

#     program_options = {program.name: program for program in programs}

#     required_label("📌 Program")
#     input_program_name = st.selectbox(
#         "", # ** No longer relevant
#         list(program_options.keys()),
#         index=None,
#         key="input_program_name",
#         label_visibility="collapsed",
#     )

#     if (input_program_name is not None) and (input_program_name in program_options):
#         input_program = program_options[input_program_name]
#         st.session_state["input_program"] = input_program

#         show_help_text(input_program.help_text)

#         return

#     st.session_state.pop("input_program", None)

def show_program_dates_selection() -> None:
    """Render the program dates selection flow."""
    input_subcategory = st.session_state.get("input_subcategory")
    if not input_subcategory:
        # st.error("Program not selected.")
        return

    # This field is used for form validation. 
    # I am assuming that if this function will be called only when program date is required.
    st.session_state["is_program_date_req"] = True

    # Assuming you have a method to get program dates based on the selected program
    program_dates = subcategory_repo.get_program_dates_in_range(
                        input_subcategory.subcategory_id, 
                        volunteer.departure_date)

    info = setting_repo.get_by_key("PROGRAM_DATES_INFO_MSG")
    if info and not info.value.isspace():
        st.info(f"ℹ️ {info.value}")

    if not program_dates:
        #st.warning("No dates available for the selected program.")
        st.warning("Active program dates are beyond your departure date. Please select a different program or raise stay extension request.")
        return

    required_label("📅 Select Program Date")
    input_date = st.selectbox(
        ".",
        program_dates,
        index = None,
        key = "input_date",
        label_visibility = "collapsed",
        placeholder = "Select Program Date"
    )

    if input_date is not None:
        st.session_state["input_program_date"] = input_date
        return

    st.session_state.pop("input_date", None)
    st.session_state.pop("input_program_date", None)

def show_custom_date_fields(subcategory: SubCategory) -> None:
    """Render the from date fields, conditionally."""
    if not subcategory.show_from_date_input and not subcategory.show_to_date_input:
        return

    from_date, to_date = None, None
    col1, col2 = st.columns(2)
    to_date_value = None
    max_date_value = date.today() + timedelta(days=90)

    with col1:
        if subcategory.show_from_date_input:
            st.session_state["is_from_date_req"] = True

            required_label("📅 From Date")
            from_date = st.date_input("", format="DD/MM/YYYY", key="from_date",
                                      label_visibility="collapsed",
                                      max_value=max_date_value,
                                      min_value=date.today(),)

            to_date_value = from_date + timedelta(days = subcategory.duration_in_days - 1 if subcategory.duration_in_days - 1 > 0 else 1)

    with (col1 if not subcategory.show_from_date_input else col2): # both columns should be used only when both date fields need to be shown
        if subcategory.show_to_date_input:
            st.session_state["is_to_date_req"] = True

            required_label("📅 To Date")
            to_date = st.date_input("", value = to_date_value, format="DD/MM/YYYY", key="to_date",
                                    label_visibility="collapsed",
                                    max_value=max_date_value)

    if from_date:
        st.session_state["input_from_date"] = from_date
    else:
        st.session_state.pop("from_date", None)
        st.session_state.pop("input_from_date", None)

    if to_date:
        st.session_state["input_to_date"] = to_date
    else:
        st.session_state.pop("to_date", None)
        st.session_state.pop("input_to_date", None)

def show_coordinator_email_input() -> None:
    """Render the coordinator email input, validate and store in session state."""

    # This field is used for form validation. 
    # I am assuming that if this function will be called only when coordinator email is required.
    st.session_state["is_coordinator_email_req"] = True

    required_label("📧 Karma Sadhana Coordinator Mail ID")
    coordinator_email = st.text_input(
        ".",
        placeholder="Enter your Karma Sadhana Coordinator Mail ID",
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

    st.session_state.pop("coordinator_email", None)
    st.session_state.pop("input_coordinator_email", None)

def show_health_related_bool() -> None:
    """Render the health-related Yes/No input and store the value in session state."""

    # This field is required for form validation.
    st.session_state["is_health_related_bool_req"] = True

    required_label("🩺 Is it health related?")
    health_related = st.radio(
        "",
        options=["Yes, health related", "No, not health related"],
        index=1,
        key="health_related",
        label_visibility="collapsed",
    )

    # No selection yet
    if health_related is None:
        st.session_state.pop("input_health_related", None)
        return

    # Store as an actual boolean
    if health_related == "Yes, health related" :
        st.session_state["input_health_related"] = True
    else:
        st.session_state["input_health_related"] = False

def show_description_box() -> None:
    """Render the description box."""
    # To debug what is there in the session state
    # st.write("DESCRIPTION STATE:", {
    #     k: v for k, v in st.session_state.items()
    #     if "description" in k.lower()
    # })

    required_label("📝 Reason for your request")
    description = st.text_area(
        ".",
        placeholder="Please fill in with as much detail as possible",
        height=150,
        key="description",
        label_visibility="collapsed",
    )

    if description:
        st.session_state["input_description"] = description
        return

    st.session_state.pop("description", None)
    st.session_state.pop("input_description", None)

def show_submit_button():
    """Render the submit button"""
    submit = st.button("Submit Request", key = "submit")
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

    is_stay_area_req = st.session_state.get("is_stay_area_req", False)
    if is_stay_area_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_stay_area", ""), 
                "⚠️ Please select a Stay Area.")
        )

    is_room_req = st.session_state.get("is_room_req", False)
    if is_room_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_room", ""), 
                "⚠️ Please select a Room.")
        )

    is_bathroom_req = st.session_state.get("is_bathroom_req", False)
    if is_bathroom_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_bathroom", ""), 
                "⚠️ Please select a Bathroom.")
        )

    is_floor_num_req = st.session_state.get("is_floor_num_req", False)
    if is_floor_num_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_floor_num", ""), 
                    "⚠️ Please select a Floor.")
        )

    is_shower_req = st.session_state.get("is_shower_req", False)
    if is_shower_req:
        validation_results.append(
            validate_required(
                st.session_state.get("input_shower", ""), 
                "⚠️ Please select a Shower.")
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
       # logger.info("abs((date2 - date1).days): %s", str(abs((to_date - from_date).days)))
        
        if from_date >= to_date:
            st.error("❌ From Date cannot be later than To Date.")
            validation_results.append(False)

        if from_date >= volunteer.departure_date and st.session_state.get("input_category", "").category_id != StayExtensionCatIdFromTable:
            st.error("❌ From date cannot be later than your departure date. Please request extension if needed.")
            validation_results.append(False)

        if to_date >= volunteer.departure_date and st.session_state.get("input_category", "").category_id != StayExtensionCatIdFromTable:
            st.error("❌ To date cannot be later than your departure date. Please request extension if needed.")
            validation_results.append(False)

        if ( from_date != volunteer.departure_date or to_date <= volunteer.departure_date ) and st.session_state.get("input_category", "").category_id == StayExtensionCatIdFromTable:
            st.error("❌ From date should be your current depature date and To date should be later than your current depature date.")
            validation_results.append(False)

        if( st.session_state.get("input_subcategory", "").duration_in_days > 0 and abs((to_date - from_date).days) + 1 != st.session_state.get("input_subcategory", "").duration_in_days ):
            st.error(f"❌ The duration between From Date and To Date should be {st.session_state.get("input_subcategory", "").duration_in_days} days.")
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
        st.markdown(
            '<div id="request-validation-failed" style="display:none"></div>',
            unsafe_allow_html=True
        )
        return

    req: Request = None
    document_lock = threading.Lock()
    with document_lock:
        req = save_record()

    # time.sleep(10) # without delay appscript gets confused about whether request, or log table is modified

    # Log the request generation success

    logger.info(
                f"Request raised. Request ID: {req.request_id}",
                extra={
                        "ip_address": utils.get_client_ip(),
                        "vol_email_id": volunteer.email_id if volunteer else "",
                        "vol_phone_num": volunteer.phone_number if volunteer else "",
                      }
                )
    # log_repo = LogRepository()

    # now: datetime = datetime.now()
    # log: Log = Log(
    #     log_id = f"L-{now.strftime("%y%m%d-%H%M%S")}",
    #     ip_address = utils.get_client_ip(),
    #     email_id = volunteer.email_id,
    #     phone_number = volunteer.phone_number,
    #     message = f"Request raised. Request ID: {req.request_id}",
    #     timestamp = now
    # )
    # log_repo.write_to_sheet(log)

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

def reset_accomodation_req_flags():
    """
    Resets accomodation required flags, which are being used by validate method to be determine what is required.
    """

    st.session_state.pop("is_stay_area_req", None)
    st.session_state.pop("is_room_req", None)
    st.session_state.pop("is_bathroom_req", None)
    st.session_state.pop("is_floor_num_req", None)
    st.session_state.pop("is_shower_req", None)

def save_record():
    request_repo = RequestRepository()

    volunteer = st.session_state["volunteer"]
    vol_cat = vol_cat_repo.get_by_id(volunteer.volunteer_category)
                                           
    category = st.session_state["input_category"]
    subcategory = st.session_state.get("input_subcategory", None)

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

    is_health_related = False
    if subcategory is not None:
        if subcategory.show_from_date_input:
            from_date = st.session_state["input_from_date"]
        if subcategory.show_to_date_input:
            to_date = st.session_state["input_to_date"]
        if subcategory.show_coordinator_email_input:
            coordinator_email = st.session_state["input_coordinator_email"]
        if subcategory.show_health_related_bool_input:
            is_health_related = st.session_state["input_health_related"]

        team_id = subcategory.team_id

    # if program is not None:
    #     if program.show_from_date_input:
    #         from_date = st.session_state["input_from_date"]
    #     if program.show_to_date_input:
    #         to_date = st.session_state["input_to_date"]
    #     if program.show_coordinator_email_input:
    #         coordinator_email = st.session_state["input_coordinator_email"]

    #     team_map = program_repo.get_assigned_team(program.program_id, volunteer.volunteer_category)
    #     team_id = team_map.team_id

    # Prepare description

    description = st.session_state["input_description"]

    is_stay_area_req = st.session_state.get("is_stay_area_req", False)
    if is_stay_area_req:
        input_stay_area = st.session_state.get("input_stay_area", "")
        description += f"\nStay Area: {input_stay_area.stay_area_name}"

    is_room_req = st.session_state.get("is_room_req", False)
    if is_room_req:
        input_room = st.session_state.get("input_room", "")
        description += f"\nRoom: {input_room.room_num}"

    is_bathroom_req = st.session_state.get("is_bathroom_req", False)
    if is_bathroom_req:
        input_bathroom = st.session_state.get("input_bathroom", "")
        description += f"\nBathroom: {input_bathroom.bathroom_num}"

    is_floor_num_req = st.session_state.get("is_floor_num_req", False)
    if is_floor_num_req:
        input_floor_num = st.session_state.get("input_floor_num", "")
        description += f"\nFloor Number: {input_floor_num.floor_num}"

    is_shower_req = st.session_state.get("is_shower_req", False)
    if is_shower_req:
        input_shower = st.session_state.get("input_shower", "")
        description += f"\nShower: {input_shower.shower_num}"


    

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
        description += f"\nKarma Sadhana Coordinator Mail ID: {coordinator_email}"

    if is_health_related == True:
        description += f"\n#Health"

    timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    #existing_request_ids = request_repo.get_existing_ids()
    req = Request(
        # request_id = utils.generate_request_id(vol_cat.request_label, existing_request_ids), old code for req id generation
        request_id = utils.generate_request_id(vol_cat.request_label, volunteer.visit_id),
        person_id = volunteer.person_id,
        visit_id = volunteer.visit_id,
        name = volunteer.name,
        gender = volunteer.gender,
        email_id = volunteer.email_id,
        phone_number = volunteer.phone_number,
        volunteer_category = volunteer.volunteer_category, # !! Need to ask if the code or full label should go here
        category_id= category.category_id,
        subcategory_id = subcategory.subcategory_id if subcategory != None else "",
        from_date = from_date,
        to_date = to_date,
        description = description,
        timestamp = timestamp,
        assigned_department = team_id,
        status = utils.get_setting("defaultRequestStatus"),
        status_sub_type = utils.get_setting("defaultRequestStatusSubType"), # to be left empty initially
        last_edited = timestamp,

        program_date_id = program_date.program_date_id if program_date is not None else None,
        coordinator_email_id = coordinator_email,
        is_health_related = is_health_related
    )

    request_repo.write_to_sheet(req)

    return req

def clear_form_state():
    """
    Clears all form-related session state.
    This must be called BEFORE the widgets are rendered.
    """

    mode = utils.get_setting("mode")

    if mode == "Development":
        st.session_state["state"] = "Form"
    else:
        st.session_state["state"] = "Identification"
        st.session_state["forgot_email_clicked"] = False
        st.session_state["volunteer"] = None
        st.session_state["volunteer_identified"] = False

    # Static fields
    for key in [
        "email_id",
        "country_code",
        "phone_number",
        "input_category_name",
        "input_category",
        "input_subcategory_name",
        "input_subcategory",
        "input_health_related",
        "coordinator_email",
        "input_coordinator_email",
        "description",
        "input_description",
    ]:
        st.session_state[key] = ""

    for key in [        
        "input_date",
        "input_program_date",
        "from_date",
        "input_form_date",
        "to_date",
        "input_to_date",
    ]:
        st.session_state.pop(key, None)

    # Dynamic dropdowns
    dynamic_dropdowns = st.session_state.pop("dynamic_dropdowns", None)

    if dynamic_dropdowns:
        for field in dynamic_dropdowns:
            st.session_state.pop(field["key_name"], None)

    # Dynamic textboxes
    dynamic_textbox = st.session_state.pop("dynamic_textbox", None)

    if dynamic_textbox:
        for field in dynamic_textbox:
            st.session_state.pop(field["key_name"], None)

def reset_form():
    """
    Requests a form reset.
    The actual clearing happens at the beginning of the next Streamlit run.
    """
    st.session_state["reset_form_requested"] = True
    st.rerun()

def reset_req_flags():
    """
    Resets required flag, which are being used by validate method to be determine what is required.
    """

    st.session_state.pop("is_sub_cat_req", None)
    st.session_state.pop("is_program_date_req", None)
    st.session_state.pop("is_from_date_req", None)
    st.session_state.pop("is_to_date_req", None)
    st.session_state.pop("is_health_related_bool_req", None)
    st.session_state.pop("is_coordinator_email_req", None)

    st.session_state.pop("is_stay_area_req", None)
    st.session_state.pop("is_room_req", None)
    st.session_state.pop("is_bathroom_req", None)
    st.session_state.pop("is_floor_num_req", None)
    st.session_state.pop("is_shower_req", None)

def required_label(label: str) -> None:
    st.markdown(
        f"""
        <label class="required-label">
            {label}&nbsp;<span class="required-star">*</span>
        </label>
        """,
        unsafe_allow_html=True,
    )

@st.dialog(
    "Request Registered",
    dismissible=False,
)
def show_success_popup(request_id,coordinator_email_required):
    if(coordinator_email_required and st.session_state.get("input_coordinator_email", None) != None):
        st.markdown(
                    f"""
                    <div style="text-align: center; padding: 10px 0 20px 0;">
                        <div style="font-size: 42px;">✅</div>
                        <div style="font-size: 18px; font-weight: 600; margin-top: 15px;">
                            🔹 Please request your department coordinator to send an approval reply to this request mail for us to process it further.
                                Once the reply email is received, We will respond within 48 hours.
                        </div>
                        <div style="font-size: 16px; font-weight: 600; margin-top: 10px;">
                            Your request ID is <u><strong>{request_id}</strong></u>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )    
    else :
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px 0 20px 0;">
                <div style="font-size: 42px;">✅</div>
                <div style="font-size: 18px; font-weight: 600; margin-top: 15px;">
                    Your request has been successfully registered.
                </div>
                <div style="font-size: 16px; font-weight: 600; margin-top: 10px;">
                    Your request ID is <u><strong>{request_id}</strong></u>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <style>
        div[data-testid="stDialog"] div[data-testid="stButton"] {
            display: flex;
            justify-content: center;
            width: 100%;
        }

        div[data-testid="stDialog"] div[data-testid="stButton"] button {
            background-color: #28a745;
            border-color: #28a745;
            color: white;
            width: 450px;
        }

        div[data-testid="stDialog"] div[data-testid="stButton"] button:hover {
            background-color: #218838;
            border-color: #218838;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.button("OK", type="primary"):
        st.session_state["reset_form_requested"] = True
        st.rerun()

# def send_mail_requester(request: Request) -> None:
#     """Send the request notification to the requester."""

#     email_service._send_template_email(
#         request=request,
#         # recipient=request.email_id,
#         recipient="yogesh.jaykar-ext@gmail.com",
#         template_name=email_service.TEMPLATE_REQUESTER,
#     )

# def send_mail_team(request: Request) -> None:
#     """Send the request notification to the assigned team."""

#     team = team_repo.get_by_id(request.assigned_department)

#     email_service._send_template_email(
#         request=request,
#         # recipient=team.contact_email,
#         recipient="yogesh.jaykar-ext@gmail.com",
#         template_name=email_service.TEMPLATE_TEAM,
#     )

# def send_mail_secondary_email(request: Request, secondary_email: str) -> None:
#     """Send the request notification to a secondary email address."""

#     email_service._send_template_email(
#         request=request,
#         # recipient=secondary_email,
#         recipient="yogesh.jaykar-ext@gmail.com",
#         template_name=email_service.TEMPLATE_SECONDARY_EMAIL,
#     )

# def send_mail_coordinator(request: Request) -> None:
#     """Send the request notification to the coordinator."""

#     coordinator_email = request.coordinator_email_id

#     email_service._send_template_email(
#         request=request,
#         # recipient=coordinator_email,
#         recipient="yogesh.jaykar-ext@gmail.com",
#         template_name=email_service.TEMPLATE_COORDINATOR,
#     )

if __name__ == "__main__":
    try:
        st.title("🔹 Raise a Request")
    
        reset_req_flags()

        # Clear widget state BEFORE creating any widgets
        if st.session_state.pop("reset_form_requested", False):
            clear_form_state()

        load_css()
        if st.session_state.get("state") == "Identification":
            show_volunteer_email_identification()
            show_forgot_email_button()
        
            if st.session_state.get("forgot_email_clicked"):
                show_volunteer_phone_identification()

        elif st.session_state.get("state") == "Form":
            load_js() # For disabling the form when submitted

            volunteer = st.session_state.get("volunteer")
            if volunteer:
                mode = utils.get_setting("mode")
                if mode == "Development":
                    show_volunteer_details()

                col1, col2 = st.columns(2)

                show_category_selection(col1)
                input_category = st.session_state.get("input_category")
                if input_category != None:
                    show_subcategory_selection(col2)

                    accomodation_id = setting_repo.get_by_key("ACCOMODATION_CATEGORY_ID")
                    if input_category.category_id == accomodation_id.value:
                        show_accomodation_fields()
                    else:
                        reset_accomodation_req_flags()

                input_subcategory = st.session_state.get("input_subcategory")
                if input_subcategory != None and input_subcategory != '':
                    render_dynamic_dropdowns(input_subcategory)
                    render_dynamic_textbox(input_subcategory)
                    if input_category.has_programs:
                        if (not input_subcategory.show_from_date_input and 
                            not input_subcategory.show_to_date_input):
                            show_program_dates_selection()
                        else:
                            show_custom_date_fields(input_subcategory)
                    else:
                        show_custom_date_fields(input_subcategory)

                    if input_subcategory.show_coordinator_email_input:
                        show_coordinator_email_input()

                    if input_subcategory.show_health_related_bool_input:
                        show_health_related_bool()

                # input_program = st.session_state.get("input_program")
                # if input_program != None:

                #     if input_program.show_coordinator_email_input:
                #         show_coordinator_email_input()

                show_description_box()
                req = show_submit_button()

                if req:
                    show_success_popup(req.request_id,input_subcategory.show_coordinator_email_input)

                # send emails
                # if req:
                #     send_mail_requester(req)
                #     send_mail_team(req)
                #     if input_subcategory != None and input_subcategory.secondary_email:
                #         send_mail_secondary_email(req, input_subcategory.secondary_email)

                #     send_mail_coordinator(req)
    except Exception as e: 
        # Log the error
        volunteer = st.session_state.get("volunteer")
        logger.exception(
                    "Failed while processing request",
                    extra={
                        "ip_address": utils.get_client_ip(),
                        "vol_email_id": volunteer.email_id if volunteer else "",
                        "vol_phone_num": volunteer.phone_number if volunteer else "",
                    }
                )
        
        # log_repo = LogRepository()

        # now: datetime = datetime.now()
        # log: Log = Log(
        #     log_id = f"L-{now.strftime("%y%m%d-%H%M%S")}",
        #     ip_address = utils.get_client_ip(),
        #     email_id = volunteer.email_id if volunteer else "",
        #     phone_number = volunteer.phone_number if volunteer else "",
        #     message = f"An error occurred. Error: {str(e)}",
        #     exception = traceback.format_exc(),
        #     timestamp = now
        # )
        # log_repo.write_to_sheet(log)
