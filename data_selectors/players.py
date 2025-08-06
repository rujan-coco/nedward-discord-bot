import os
import json
from dataclasses import dataclass

@dataclass
class Player:
    user_id: str
    player_tag: str

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "player_tag": self.player_tag,
        }

def get_players_data():
    folder_path = "./data"
    file_path = os.path.join(folder_path, "players.json")

    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Ensure the file exists
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)

    # Load data
    with open(file_path, "r") as f:
        players = json.load(f)

    return [Player(**entry) for entry in players]

def get_player_by_user_id(user_id):
    players = get_players_data()

    for player in players:
        if player.user_id == user_id:
            return player