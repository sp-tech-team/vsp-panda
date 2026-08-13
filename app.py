import streamlit as st
import utils

from repository import VolunteerRepository, TeamRepository, CategoryRepository, SubCategoryRepository

volunteer_repository = VolunteerRepository()
team_repository = TeamRepository()
category_repository = CategoryRepository()
subcategory_repository = SubCategoryRepository()

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
        st.error("Category not selected.")
        return

    filtered_subcategories = subcategory_repository.get_by_category_id(selected_category.category_id)

    subcategory_options = {subcategory.name: subcategory for subcategory in filtered_subcategories}

    selected_subcategory_name = st.selectbox(
        "📌 Sub Category", # ** No longer relevant
        list(subcategory_options.keys()),
    )

    if (selected_subcategory_name is not None) and (selected_subcategory_name in subcategory_options):
        selected_subcategory = subcategory_options[selected_subcategory_name]
        st.session_state["selected_subcategory"] = selected_subcategory






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
            show_subcategory_selection()


    
        

    

    
