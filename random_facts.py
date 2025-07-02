import requests
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()
COC_API_TOKEN = os.getenv("COC_API_TOKEN")

def get_donations_fact():
  encoded_clan_tag = urllib.parse.quote("#2LJ80LRCR")
  res = requests.get(
    f"https://api.clashofclans.com/v1/clans/{encoded_clan_tag}/members", 
    headers={"Authorization": f"Bearer {COC_API_TOKEN}"}
  )

  donations_per_member = [{
    "name": member["name"],
    "donations": member["donations"],
    "donations_received": member["donationsReceived"],
    "donations_ratio": round(member["donations"] / member["donationsReceived"] if member["donationsReceived"] != 0 else member["donations"], 2),
  } for member in res.json()["items"]]

  highest_donor = max(donations_per_member, key=lambda x: x["donations"])
  worst_donor = max(donations_per_member, key=lambda x: x["donations_received"])
  best_ratio = max(donations_per_member, key=lambda x: x["donations_ratio"])

  return f"""
**Most Generous Member:** {highest_donor["name"]}
> **{highest_donor["name"]}** is the most generous member, with **{highest_donor["donations"]}** donations and **{highest_donor["donations_received"]}** donations received. They have donated **{highest_donor["donations_ratio"]}** times more than they have received.


**Most Greedy Member:** {worst_donor["name"]}
> **{worst_donor["name"]}** is the greediest member, with **{worst_donor["donations"]}** donations and **{worst_donor["donations_received"]}** donations received. They have only donated **{worst_donor["donations_ratio"]}** times more than they have received.


**Honorable Mention:** {best_ratio["name"]}
> **{best_ratio["name"]}** has the best ratio of donations to donations received. They have donated **{best_ratio["donations_ratio"]}** times more than they have received.
"""

if __name__ == "__main__":
  get_donations_fact()