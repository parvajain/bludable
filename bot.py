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
    print(f"Logged in as {bot.user}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("!track"):
        try:
            # Extract input
            parts = message.content.split(" ", 1)
            print("Split parts:", parts)  # Debug line

            if len(parts) < 2:
                await message.channel.send("Invalid format! Use `!track SummonerName#Tag`.")
                return

            summoner_input = parts[1].strip()
            print("Summoner input:", summoner_input)  # Debug line

            if "#" not in summoner_input:
                await message.channel.send("Invalid format! Use `!track SummonerName#Tag`.")
                return

            # Split name and tag
            summoner_name, summoner_tag = summoner_input.split("#", 1)
            print("Name:", summoner_name, "Tag:", summoner_tag)  # Debug line

            # Fetch account data
            account = cass.get_account(name=summoner_name, tagline=summoner_tag, region="NA")
            print("Account fetched:", account)  # Debug line

            # Get summoner
            summoner = cass.get_summoner(puuid=account.puuid, region="NA")
            print("Summoner fetched:", summoner)  # Debug line

            # Fetch match history
            match_history = summoner.match_history
            print("Match history length:", len(match_history))  # Debug line

            # Check last match result
            match = match_history[0]
            participant = match.participants[summoner]
            result = "won" if participant.stats.win else "lost"
            await message.channel.send(f"{summoner.name} {result} their last game!")

        except Exception as e:
            print("ERROR:", e)  # Debug line
            await message.channel.send(f"Error: {e}")

# Run the bot
bot.run(DISCORD_TOKEN)
