import json
import os

USER_EVENTS_PATH = "data/user_events.json"

def load_user_events():
    if not os.path.exists(USER_EVENTS_PATH):
        return {}
    with open(USER_EVENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_events(data):
    with open(USER_EVENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def add_event_for_user(user_id: str, race_id: str):
    data = load_user_events()
    user_events = data.get(user_id, [])
    if race_id not in user_events:
        user_events.append(race_id)
        data[user_id] = user_events
        save_user_events(data)
        return True
    return False


def get_user_events(user_id: str):
    data = load_user_events()
    return data.get(user_id, [])


