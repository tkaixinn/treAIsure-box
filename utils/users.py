from pathlib import Path
import json

USER_FILE = Path("users.json")

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users_data):
    with open(USER_FILE, "w") as f:
        json.dump(users_data, f, indent=4)

def update_profile(username, skills, interests, startup_type, resources):
    users_data = load_users()
    users_data["users"][username].update({
        "skills": skills,
        "interests": interests,
        "startup_type": startup_type,
        "resources": resources
    })
    save_users(users_data)

def save_idea(username, idea):
    users_data = load_users()
    users_data["users"][username].setdefault("saved_ideas", []).append(idea)
    save_users(users_data)

def delete_idea(username, index):
    users_data = load_users()
    if "saved_ideas" in users_data["users"][username]:
        users_data["users"][username]["saved_ideas"].pop(index)
    save_users(users_data)

def edit_idea_notes(username, index, notes):
    users_data = load_users()
    users_data["users"][username]["saved_ideas"][index]["notes"] = notes
    save_users(users_data)