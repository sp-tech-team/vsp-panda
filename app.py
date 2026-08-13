import streamlit as st
import utils

from repository import ProgramRepository, VolunteerRepository, TeamRepository, CategoryRepository, SubCategoryRepository

volunteer_repository = VolunteerRepository()
team_repository = TeamRepository()
category_repository = CategoryRepository()
subcategory_repository = SubCategoryRepository()
program_repository = ProgramRepository()

if "state" not in st.session_state:
    st.session_state["state"] = "Identification"
elif "volunteer_identified" in st.session_state and st.session_state["volunteer_identified"]:
    st.session_state["state"] = "Form"

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

    selected_country = st.selectbox("🌍 Select Country Code", 
        list(country_code_map.keys()), 
        index=list(country_code_map.keys()).index("IN (+91)"))
    selected_country_code = country_code_map[selected_country]

    phone_number = st.text_input(
        "📞 Phone Number",
        placeholder="Enter phone number without country code",
    )

    if selected_country_code and phone_number:
        if not phone_number.strip():
            st.error("Phone number is required.")
            return

        full_phone_number = f"{selected_country_code}{phone_number.strip()}"

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

    selected_category_name = st.selectbox(
        "📌 I want to reach out to:", # ** No longer relevant
        list(category_options.keys()),
        index=None
    )

    if (selected_category_name is not None) and (selected_category_name in category_options):
        selected_category = category_options[selected_category_name]
        st.session_state["selected_category"] = selected_category

def show_subcategory_selection() -> None:
    """Render the subcategory selection flow."""
    volunteer = st.session_state.get("volunteer")
    if not volunteer:
        st.error("Volunteer not identified.")
        return
    
    selected_category = st.session_state.get("selected_category")
    if not selected_category:
        # st.error("Category not selected.")
        return

    filtered_subcategories = subcategory_repository.get_by_category_id_for_vol_cat(
                                selected_category.category_id, 
                                volunteer.volunteer_category)

    subcategory_options = {subcategory.name: subcategory for subcategory in filtered_subcategories}

    selected_subcategory_name = st.selectbox(
        "📌 Sub Category", # ** No longer relevant
        list(subcategory_options.keys()),
        index=None
    )

    if (selected_subcategory_name is not None) and (selected_subcategory_name in subcategory_options):
        selected_subcategory = subcategory_options[selected_subcategory_name]
        st.session_state["selected_subcategory"] = selected_subcategory

        show_help_text(selected_subcategory.help_text)

def show_program_selection() -> None:
    """Render the program selection flow."""
    volunteer = st.session_state.get("volunteer")
    if not volunteer:
        st.error("Volunteer not identified.")
        return
    
    selected_category = st.session_state.get("selected_category")
    if not selected_category:
        # st.error("Category not selected.")
        return

    programs = program_repository.get_active_programs_for_gender(volunteer.gender)

    program_options = {program.program_name: program for program in programs}

    selected_program_name = st.selectbox(
        "📌 Program", # ** No longer relevant
        list(program_options.keys()),
        index=None
    )

    if (selected_program_name is not None) and (selected_program_name in program_options):
        selected_program = program_options[selected_program_name]
        st.session_state["selected_program"] = selected_program

        show_help_text(selected_program.help_text)

def show_program_dates_selection() -> None:
    """Render the program dates selection flow."""
    selected_program = st.session_state.get("selected_program")
    if not selected_program:
        # st.error("Program not selected.")
        return

    # Assuming you have a method to get program dates based on the selected program
    program_dates = program_repository.get_program_dates_in_range(
                        selected_program.program_id, 
                        volunteer.departure_date)

    if not program_dates:
        st.warning("No dates available for the selected program.")
        return

    selected_date = st.selectbox(
        "📅 Select Program Date",
        program_dates,
        index=None
    )

    if selected_date is not None:
        st.session_state["selected_program_date"] = selected_date

def show_from_to_date_fields() -> None:
    """Render the from and to date fields."""
    from_date = st.date_input("📅 From Date")
    to_date = st.date_input("📅 To Date")

    if from_date and to_date:
        if from_date > to_date:
            st.error("From Date cannot be later than To Date.")
            return

        st.session_state["from_date"] = from_date
        st.session_state["to_date"] = to_date

def show_description_box() -> None:
    """Render the description box."""
    description = st.text_area(
        "📝 Description",
        placeholder="Enter a brief description of your request",
        height=150,
    )

    if description:
        st.session_state["description"] = description

def show_help_text(help_text: str) -> None:
    """Render the help text."""
    if help_text:
        st.markdown(f"""
            <div style='color: #555555; background-color: #f8f9fa; padding: 12px; border-radius: 8px; font-size: 14px;'>
                {help_text}
            </div>""", 
            unsafe_allow_html=True)







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
            selected_category = st.session_state.get("selected_category")
            if selected_category != None:
                if selected_category.has_programs:
                    show_program_selection()
                else:
                    show_subcategory_selection()

            selected_program = st.session_state.get("selected_program")
            if selected_program != None:
                if selected_program.load_program_dates:
                    show_program_dates_selection()
                else:
                    show_from_to_date_fields()

            show_description_box()
                


    
        

    

    
