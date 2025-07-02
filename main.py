import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
import urllib.parse
import random
import re
from get_cwl_lineups import get_cwl_lineups

# Load environment variables from .env file
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
COC_API_TOKEN = os.getenv("COC_API_TOKEN")

# Logging
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

# Define Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Instantiate Bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
  print(f"Bot {bot.user.name} is ready!")

@bot.event
async def on_member_join(member):
  await member.send(f"Welcome to the server, Chief {member.name}! 🫡")

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  
  if "oliver the goat" in  message.content.lower():
    await message.delete()
    await message.channel.send(f"{message.author.mention} - You can't spread lies in this server!")

  match = re.match(r"bot how many times has (.+?) gooned this week\?", message.content.lower())
  if match:
      name = match.group(1).strip()
      times = random.randint(0, 20)  # You can change the range if you want
      await message.channel.send(f"{message.author.mention} - {name.title()} has gooned {times} times this week.")
      return
  
  await bot.process_commands(message)

@bot.command()
async def player_stats(ctx, player_tag: str):
  if not player_tag.startswith("#"):
    player_tag = f"#{player_tag}"

  encoded_player_tag = urllib.parse.quote(player_tag)
  res = requests.get(f"https://api.clashofclans.com/v1/players/{encoded_player_tag}", headers={"Authorization": f"Bearer {COC_API_TOKEN}"})

  # TODO: There has to be a better way to do this.  
  heroes = '\n'.join([f"- {hero['name']}: {hero['level']}/{hero['maxLevel']}" for hero in res.json()["heroes"]])

  await ctx.send(f"""
Hello {ctx.author.mention}! 👋. Here are some stats you may be interested in:

**Hero Levels:**
{heroes}
  """)

@bot.command()
async def raid(ctx):
  encoded_clan_tag = urllib.parse.quote("#2LJ80LRCR")

  res = requests.get(
    f"https://api.clashofclans.com/v1/clans/{encoded_clan_tag}/capitalraidseasons", 
    params={
      "limit": 3,
    },
    headers={"Authorization": f"Bearer {COC_API_TOKEN}"}
  )

  raids = res.json()["items"]

  all_raid_members = [raid.get("members", []) for raid in raids]

  flattened_all_raid_members = [member for raid_members in all_raid_members for member in raid_members]

  print(flattened_all_raid_members)

  total_looted_medals_per_member = {}

  for member in flattened_all_raid_members:
    name = member["name"]
    looted = member["capitalResourcesLooted"]

    total_looted_medals_per_member[name] = total_looted_medals_per_member.get(name, 0) + looted

  sorted_loot_data = dict(sorted(total_looted_medals_per_member.items(), key=lambda x:x[1], reverse=True))

  loot_data_str = "\n".join([f"- {key}: {value}" for key, value in sorted_loot_data.items()])
  await ctx.send(f"""
**Total looted medals per member in the last 3 raids:**
{loot_data_str}
  """)

@bot.command()
async def opponent_lineup(ctx):
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
  
  clan_name, members = get_cwl_lineups()

  lineup_str = "\n".join([f"- {i + 1} - {member['name']} (TH{member['townhallLevel']})" for i, member in enumerate(members)])

  await ctx.send(f"""
**{clan_name} lineup:**

{lineup_str}
  """)

# Run Bot
bot.run(DISCORD_BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)