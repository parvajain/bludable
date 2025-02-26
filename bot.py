import discord
import cassiopeia as cass
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

# Initialize Cassiopeia
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
            # [1] Parse input
            parts = message.content.split(" ", 1)
            if len(parts) < 2:
                await message.channel.send("Error: Use `!track SummonerName#Tag`")
                return

            summoner_input = parts[1].strip()
            if "#" not in summoner_input:
                await message.channel.send("Error: Missing # in summoner name!")
                return

            # [2] Split name/tag
            summoner_name, summoner_tag = summoner_input.split("#", 1)
            summoner_name = summoner_name.strip()
            summoner_tag = summoner_tag.strip()
            print(f"DEBUG: Tracking {summoner_name}#{summoner_tag}")

            # [3] Fetch account (region="NA" for Americas)
            print("DEBUG: Fetching account... (region=NA)")
            account = cass.get_account(name=summoner_name, tagline=summoner_tag, region="NA")
            print(f"DEBUG: Account fetched: {account.name}#{account.tagline} (PUUID={account.puuid})")

            # [4] Fetch summoner (region="NA1" for North America platform)
            print("DEBUG: Fetching summoner... (region=NA1)")
            summoner = cass.get_summoner(puuid=account.puuid, region="NA1")
            print(f"DEBUG: Summoner fetched: Level={summoner.level}, ID={summoner.id}")

            # [5] Get matches
            print("DEBUG: Fetching match history...")
            matches = summoner.match_history
            print(f"DEBUG: Found {len(matches)} matches")
            if not matches:
                await message.channel.send(f"{account.name} has no recent matches!")
                return

            # [6] Analyze match
            match = matches[0]
            print(f"DEBUG: Latest match ID={match.id}")
            print(f"DEBUG: Participants in match: {len(match.participants)}")

            # [7] Find participant
            participant = next((p for p in match.participants if p.puuid == account.puuid), None)
            if not participant:
                await message.channel.send("Error: Couldn't find player in match!")
                return

            # [8] Send result
            result = "won" if participant.stats.win else "lost"
            await message.channel.send(f"{account.name} {result} their last game!")
            print("DEBUG: Result sent successfully!")

        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {str(e)}")
            await message.channel.send(f"Error: {str(e)}")

# Run the bot
bot.run(DISCORD_TOKEN)
