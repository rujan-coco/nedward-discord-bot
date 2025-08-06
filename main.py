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
from random_facts import get_donations_fact

# Load environment variables from .env file
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
COC_API_TOKEN = os.getenv("COC_API_TOKEN")

# Logging
# handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

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
  welcome_channel = discord.utils.get(member.guild.text_channels, name='welcome')
  await welcome_channel.send(f"Welcome to the server, Chief {member.mention}! 🫡")

def generate_fake_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

funny_song_titles = [
    "Peppa Pig Intro (Nightcore Version)",
    "Baby Shark Lofi Study Mix",
    "Shrek's Swamp Serenade (feat. Donkey)",
    "Thomas the Tank Engine Drill Remix",
    "Barbie Girl but it's 8D and You're in a Blender",
    "Cocomelon Theme – Trap Remix",
    "My Cat Walked on My Synth and Made This",
    "iCarly Theme Slowed + Reverb + Existential Dread",
    "SpongeBob’s Laugh on a 10-Hour Loop",
    "Elmo Sings WAP (Explicit)",
    "Moaning in C Minor",
    "Among Us But It's Opera",
    "Crab Rave (Gregorian Chant Edition)",
    "Toilet Flush Symphony No. 2 in E Flat",
    "Rick Astley but He’s Auto-Tuned to the ABCs",
    "Minecraft Cave Sounds IRL (Why Did I Do This)",
    "Zoom Call from Hell – The Musical",
    "Yeet Me Gently (Lullaby Edition)",
    "We Are Number One but Every 'One' is a Vine Boom",
    "Never Gonna Give You Up (Kazoo Cover)",
    "Gas Gas Gas but it's Actually a Car Horn",
    "Megalovania Played on a Printer",
    "Running in the 90s (Horse Neigh Remix)",
    "He-Man Sings 'What’s Up' (4 Non Blondes)",
    "Big Chungus National Anthem",
    "John Cena Theme but it’s Just ‘And His Name Is...’ for 10 Minutes",
    "Nyan Cat but It Gets Slower Every Meow",
    "Let It Go (Goat Screaming Version)",
    "Shooting Stars but It's Played on Flute by a 5-Year-Old",
    "Careless Whisper on Recorder with Emotional Damage"
]

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  
  if "stupid bot" in message.content.lower():
    fake_locations = ["Jack Grealish's Basement", "Gulag Server Room", "Your Mom’s Basement", "Right behind you 👀"]
    fake_names = ["Chad McThreat", "Agent 00FBI", "Detective Suspicious", "Sir Hacksalot"]

    response = (
        f"You said what?\n"
        f"IP: {generate_fake_ip()}\n"
        f"Location: {random.choice(fake_locations)}\n"
        f"Full Name: {random.choice(fake_names)}\n"
    )

    await message.reply(response)

  if re.match(r"bot what is (.+?) listening to \?", message.content.lower()):
    await message.reply(f"They are listening to {random.choice(funny_song_titles)} right now.")
  
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

  if not res.ok:
    await ctx.reply("""
❌ There was an error fetching the player stats.
Some possible reasons:
- The player tag is invalid.
- funky's IP address got blocked by SuperCell (RIP).
""")
    return

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

FACT_TYPE_SELECTOR_MAP = {
  "DONATIONS": get_donations_fact,
}

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply("❌ That command doesn't exist. Please check your spelling or use `!help` for a list of commands.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply("❌ That command requires an argument. Please check your spelling or use `!help` for a list of commands.")
    else:
        raise error

@bot.command()
async def random_fact(ctx):
  FACT_TYPES = [
    "DONATIONS",
  ]
  random_fact_type = random.choice(FACT_TYPES)

  fact = FACT_TYPE_SELECTOR_MAP[random_fact_type]()

  await ctx.send(f"""
**Sure, here is a random fact about the clan:**
{fact}
""")


# Run Bot
# bot.run(DISCORD_BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)
bot.run(DISCORD_BOT_TOKEN, log_level=logging.DEBUG)