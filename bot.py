import discord
import cassiopeia as cass
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")

cass.set_riot_api_key(RIOT_API_KEY)
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"DEBUG [1/6]: Bot logged in as {bot.user}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!track"):
        try:
            # [1] Parse input
            print("\nDEBUG [2/6]: Raw input:", message.content)
            parts = message.content.split(" ", 1)
            print("DEBUG [2/6]: Split parts:", parts)
            
            if len(parts) < 2:
                await message.channel.send("Error: Missing summoner name! Use `!track SummonerName#Tag`.")
                return

            summoner_input = parts[1].strip()
            print("DEBUG [2/6]: Trimmed input:", repr(summoner_input))  # Show hidden characters
            
            if "#" not in summoner_input:
                await message.channel.send("Error: Missing `#`! Use `!track SummonerName#Tag`.")
                return

            # [2] Split name/tag
            summoner_name, summoner_tag = summoner_input.split("#", 1)
            summoner_name = summoner_name.strip()
            summoner_tag = summoner_tag.strip()
            print(f"DEBUG [3/6]: Name: '{summoner_name}', Tag: '{summoner_tag}'")

            # [3] Fetch account
            print("DEBUG [4/6]: Fetching account...")
            account = cass.get_account(name=summoner_name, tagline=summoner_tag, region="NA")
            print(f"DEBUG [4/6]: Account fetched - PUUID: {account.puuid}")

            # [4] Fetch summoner
            print("DEBUG [5/6]: Fetching summoner...")
            summoner = cass.get_summoner(puuid=account.puuid, region="NA")
            print(f"DEBUG [5/6]: Summoner fetched - Name: {summoner.name}, Level: {summoner.level}")

            # [5] Fetch matches
            print("DEBUG [6/6]: Fetching matches...")
            matches = summoner.match_history
            print(f"DEBUG [6/6]: Found {len(matches)} matches")
            
            if not matches:
                await message.channel.send(f"{summoner.name} has no recent matches.")
                return

            # [6] Analyze match
            match = matches[0]
            print(f"DEBUG [7/6]: Latest match ID: {match.id}")
            print(f"DEBUG [7/6]: Participants count: {len(match.participants)}")
            
            # [7] Find participant
            participant = None
            for p in match.participants:
                print(f"DEBUG [7/6]: Checking participant {p.summoner.name} (PUUID: {p.puuid})")
                if p.puuid == summoner.puuid:
                    participant = p
                    break
            
            if not participant:
                await message.channel.send(f"Error: Couldn't find {summoner.name} in the match!")
                return

            # [8] Result
            result = "won" if participant.stats.win else "lost"
            await message.channel.send(f"{summoner.name} {result} their last game!")

        except Exception as e:
            print(f"CRITICAL ERROR: {type(e).__name__}: {str(e)}")
            await message.channel.send(f"Error: {str(e)}")

bot.run(DISCORD_TOKEN)
