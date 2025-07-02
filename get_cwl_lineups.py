import os
from dotenv import load_dotenv
import requests
import urllib.parse

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
COC_API_TOKEN = os.getenv("COC_API_TOKEN")

def get_cwl_lineups():
  encoded_clan_tag = urllib.parse.quote("#2LJ80LRCR")
  res = requests.get(
    f"https://api.clashofclans.com/v1/clans/{encoded_clan_tag}/currentwar/leaguegroup", 
    params={
      "limit": 3,
    },
    headers={"Authorization": f"Bearer {COC_API_TOKEN}"}
  )

  valid_rounds = [
    d for d in res.json()["rounds"] 
    if not (isinstance(d.get("warTags"), list) and all(tag == "#0" for tag in d["warTags"]))
  ]

  latest_round = valid_rounds[len(valid_rounds) - 1]['warTags']

  for item in latest_round:
    encoded_tag = urllib.parse.quote(item)

    cwl_war_res = requests.get(
      f"https://api.clashofclans.com/v1/clanwarleagues/wars/{encoded_tag}",
      headers={"Authorization": f"Bearer {COC_API_TOKEN}"}
    )

    clan = cwl_war_res.json()["clan"]
    opponent = cwl_war_res.json()["opponent"]

    if clan["tag"] == "#2LJ80LRCR":
      return opponent["name"], sorted(opponent["members"], key=lambda x: x["mapPosition"])
    
    if opponent["tag"] == "#2LJ80LRCR":
      return clan["name"], sorted(clan["members"], key=lambda x: x["mapPosition"])
    
    continue

if __name__ == "__main__":
  test = get_cwl_lineups()

  print(test)