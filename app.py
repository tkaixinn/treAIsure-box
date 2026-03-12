import streamlit as st
import streamlit_authenticator as stauth
import json
from utils import generate_startup_ideas
from pathlib import Path
from streamlit_tags import st_tags


USER_FILE = Path("users.json")

with open(USER_FILE, "r") as f:
    users_data = json.load(f)

user_dict = {
    "usernames": {
        u: {"name": users_data["users"][u]["name"], "password": users_data["users"][u]["password"]}
        for u in users_data["users"]
    }
}

authenticator = stauth.Authenticate(
    user_dict,
    "cookie_name",
    "super-long-random-signature-key-32chars!",
    cookie_expiry_days=30
)

st.title("treAIsure box")

if "authentication_status" in st.session_state and st.session_state["authentication_status"]:

    username = st.session_state["username"]
    name = st.session_state["name"]
    st.success(f"Welcome {name}!")

    profile = users_data["users"][username]

    tab_ideas, tab_profile = st.tabs(["Startup Ideas", "Profile"])

    with tab_profile:
        st.subheader("Update Your Profile")
        skills = st_tags(
            label='Enter your skills',
            text='Press enter to add more',
            value=profile.get("skills", []) if isinstance(profile.get("skills", []), list) else profile.get("skills", "").split(", "),
            )

        interests = st_tags(
            label='Enter your interests',
            text='Press enter to add more',
            value=profile.get("interests", []) if isinstance(profile.get("interests", []), list) else profile.get("interests", "").split(", "),
        )

        startup_type_options = [
                "Tech",
                "Social Impact",
                "E-commerce",
                "SaaS",
                "FinTech",
                "HealthTech",
                "EdTech",
                "AI/ML",
                "Gaming",
                "Travel & Tourism",
                "Food & Beverage",
                "Lifestyle",
                "Media & Entertainment",
                "CleanTech",
                "Other (Specify your startup type)"
        ]

        startup_type = st.selectbox(
            "Startup Type",
            startup_type_options,
            key="signup_startup_type"
        )

        if startup_type == "Other (Specify your startup type)":
            startup_type = st.text_input("Specify your startup type")
            
        resources = st.selectbox(
            "Resources",
            ["Solo", "Small Team (2-50 people)", "Medium Team (51-100 people)", "Large Team (100+ people)"],
            index=["Solo", "Small Team (2-50 people)", "Medium Team (51-100 people)", "Large Team (100+ people)"].index(profile.get("resources", "Solo")),
            key="profile_resources"
        )

        if st.button("Update Profile"):
            users_data["users"][username]["skills"] = skills
            users_data["users"][username]["interests"] = interests
            users_data["users"][username]["startup_type"] = startup_type
            users_data["users"][username]["resources"] = resources
            with open(USER_FILE, "w") as f:
                json.dump(users_data, f, indent=4)
            st.success("Profile updated!")


    with tab_ideas:
        skills = profile.get("skills", [])
        interests = profile.get("interests", [])
        startup_type = profile.get("startup_type", "Tech")
        resources = profile.get("resources", "Solo")

        if st.button("Generate Startup Ideas"):
  
            users_data["users"][username]["skills"] = skills
            users_data["users"][username]["interests"] = interests
            users_data["users"][username]["startup_type"] = startup_type
            users_data["users"][username]["resources"] = resources
            with open(USER_FILE, "w") as f:
                json.dump(users_data, f, indent=4)

            ideas = generate_startup_ideas(
                        ", ".join(skills),
                        ", ".join(interests),
                        startup_type,
                        resources
            )
            st.text_area("Your AI-generated startup ideas", ideas, height=400)


    authenticator.logout("Logout", "main")

else:

    tab_login, tab_signup = st.tabs(["🔐 Login", "🆕 Sign Up"])

    with tab_login:
        authenticator.login("main", "Login")

        if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
            st.session_state["rerun"] = True

        if "authentication_status" in st.session_state:
            if st.session_state["authentication_status"] is False:
                st.error("Username/password is incorrect")
            elif st.session_state["authentication_status"] is None:
                st.warning("Please enter your username and password")

    with tab_signup:
        st.subheader("Create your account")
        new_username = st.text_input("Username")
        new_name = st.text_input("Your Name")
        new_password = st.text_input("Password", type="password")
        skills = st_tags(
            label='Enter your skills',
            text='Press enter to add more',
            value=[],
        )

        interests = st_tags(
            label='Enter your interests',
            text='Press enter to add more',
            value=[],
        )

        startup_type_options = [
                "Tech",
                "Social Impact",
                "E-commerce",
                "SaaS",
                "FinTech",
                "HealthTech",
                "EdTech",
                "AI/ML",
                "Gaming",
                "Travel & Tourism",
                "Food & Beverage",
                "Lifestyle",
                "Media & Entertainment",
                "CleanTech",
                "Other (Specify your startup type)"
        ]
        startup_type = st.selectbox(
            "Startup Type",
            startup_type_options,
            key="signup_startup_type"
        )

        if startup_type == "Other (Specify your startup type)":
            startup_type = st.text_input("Specify your startup type")

        resources = st.selectbox(
            "Resources",
            ["Solo", "Small Team (2-50 people)", "Medium Team (51-100 people)", "Large Team (100+ people)"],
            key="signup_resources"
        )

        if st.button("Register"):
            if new_username in users_data["users"]:
                st.error("Username already exists!")
            else:
                hashed_password = stauth.Hasher.hash(new_password)
                users_data["users"][new_username] = {
                    "name": new_name,
                    "password": hashed_password,
                    "skills": skills,
                    "interests": interests,
                    "startup_type": startup_type,
                    "resources": resources
                }
                with open(USER_FILE, "w") as f:
                    json.dump(users_data, f, indent=4)
                st.success("Account created! You can now login.")