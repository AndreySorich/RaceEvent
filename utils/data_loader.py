import json

def load_races(file_path="data/races.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
