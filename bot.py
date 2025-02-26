import discord
import cassiopeia as cass
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# Configure Cassiopeia with debug logging
logging.basicConfig(level=logging.DEBUG)  # <-- Enable verbose logging
cass.apply_settings({
    "logging": {
        "print_calls": True,  # Show API calls
        "print_riot_api_key": False,
        "core": "DEBUG"
    }
})
cass.set_riot_api_key(RIOT_API_KEY)

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"DEBUG: Bot logged in as {bot.user}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!track"):
        try:
            # Parse input
            parts = message.content.split(" ", 1)
            if len(parts) < 2:
                await message.channel.send("Error: Invalid format!")
                return

            summoner_input = parts[1].strip()
            if "#" not in summoner_input:
                await message.channel.send("Error: Missing #!")
                return

            summoner_name, summoner_tag = summoner_input.split("#", 1)
            print(f"\n=== DEBUG: INPUT PARSED ===")
            print(f"Name: {repr(summoner_name)}")
            print(f"Tag: {repr(summoner_tag)}")

            # Fetch account
            account = cass.get_account(
                name=summoner_name,
                tagline=summoner_tag,
                region="AMERICAS"
            )
            print("\n=== DEBUG: ACCOUNT RESPONSE ===")
            print(f"PUUID: {account.puuid}")
            print(f"Raw data: {account._data[AccountData]}")  # Print internal data structure

            # Fetch summoner
            summoner = cass.get_summoner(puuid=account.puuid, platform="NA1")
            print("\n=== DEBUG: SUMMONER RESPONSE ===")
            print(f"Summoner ID: {summoner.id}")
            print(f"Raw data: {summoner._data[SummonerData]}")  # Print internal data

            # Rest of your code...

        except Exception as e:
            print(f"\n=== CRITICAL ERROR ===")
            print(f"Type: {type(e).__name__}")
            print(f"Message: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")  # Full traceback
            await message.channel.send(f"Error: {str(e)}")

bot.run(DISCORD_TOKEN)
