import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import requests
import urllib.parse

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

# Run Bot
bot.run(DISCORD_BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)