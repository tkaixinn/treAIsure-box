import streamlit as st
import streamlit_authenticator as stauth
from utils.ai import generate_startup_ideas, refine_startup_idea
from utils.users import load_users, save_users, save_idea, delete_idea, edit_idea_notes
from pathlib import Path
from streamlit_tags import st_tags

users_data = load_users()

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

    if "idea_saved" in st.session_state:
        st.toast("Idea saved!")
        del st.session_state["idea_saved"]

    if "notes_saved" in st.session_state:
        st.toast("💾 Notes saved!")
        del st.session_state["notes_saved"]

    if "idea_deleted" in st.session_state:
        st.toast("🗑 Idea deleted!")
        del st.session_state["idea_deleted"]

    if "refined_notes" in st.session_state:
        st.toast("### ✨ Refined Idea")
        del st.session_state["refined_notes"]

    profile = users_data["users"][username]

    tab_ideas, tab_profile, tab_my_ideas = st.tabs(["Startup Ideas", "Profile", "My Ideas"])

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
            save_users(users_data)
            st.success("Profile updated!")


    with tab_ideas:
        skills = profile.get("skills", [])
        interests = profile.get("interests", [])
        startup_type = profile.get("startup_type", "Tech")
        resources = profile.get("resources", "Solo")

        if st.button("Generate Startup Ideas"):

            ideas_raw = generate_startup_ideas(
                ", ".join(skills),
                ", ".join(interests),
                startup_type,
                resources
            )

            # split the AI text into individual ideas
            ideas_list = [i.strip() for i in ideas_raw.split("\n") if i.strip()]

            st.session_state["generated_ideas"] = ideas_list


        if "generated_ideas" in st.session_state:

            for i, idea in enumerate(st.session_state["generated_ideas"]):

                with st.container():

                    col1, col2 = st.columns([8,1])

                    with col1:
                        st.markdown(f"### 💡 Idea {i+1}")
                        st.info(idea)

                    with col2:
                        if st.button("💾", key=f"save_generated_{i}"):
                            save_idea(username, {
                                "description": idea,
                                "notes": ""
                            })
                            st.session_state["idea_saved"] = True
                            st.rerun()

                st.divider()

    with tab_my_ideas:
        saved_ideas = users_data["users"][username].get("saved_ideas", [])

        if not saved_ideas:
                st.info("You haven't saved any ideas yet.")

        else:
            for i, idea in enumerate(saved_ideas):
                with st.container():
                    st.markdown(f"### 💡 Idea {i + 1}")
                    st.info(idea['description'])

                    with st.expander("📝 Show Notes / Actions", expanded=False):
                        notes = st.text_area(
                            f"Notes for Idea {i + 1}",
                            value=idea.get("notes", ""),
                            key=f"notes_{i}"
                        )

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("💾 Save Notes", key=f"save_notes_{i}"):
                                edit_idea_notes(username, i, notes)
                                st.session_state["notes_saved"] = True
                                st.rerun()

                        with col2:
                            if st.button("🗑 Delete Idea", key=f"delete_{i}"):
                                delete_idea(username, i)
                                st.session_state["idea_deleted"] = True
                                st.rerun()

                            if st.button("💡 Refine Idea", key=f"refine_{i}"):
                                refined_idea = refine_startup_idea(idea['description'], notes)
                                st.session_state[f"refined_{i}"] = refined_idea
                                st.session_state["refined_toast"] = True  
                                st.rerun()

          
                            if f"refined_{i}" in st.session_state:
                                if st.button("💾 Save Refined Idea", key=f"save_refined_{i}"):
                                    users_data["users"][username]["saved_ideas"][i]["description"] = st.session_state[f"refined_{i}"]
                                    save_users(users_data)
                                    st.session_state["idea_saved"] = True
                                    st.rerun()

                        if f"refined_{i}" in st.session_state:
                            st.markdown("### ✨ Refined Idea")
                            st.info(st.session_state[f"refined_{i}"])

                        st.divider()

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
                save_users(users_data)
                st.success("Account created! You can now login.")