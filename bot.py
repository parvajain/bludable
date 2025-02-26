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
intents.message_content = True  # Allow bot to read messages
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if the message starts with the command
    if message.content.startswith("!track"):
        try:
            # Extract summoner name and tag
            parts = message.content.split(" ")
            if len(parts) < 2:
                await message.channel.send("Invalid format! Use `!track SummonerName#Tag`.")
                return

            summoner_input = parts[1]  # Get the full input (e.g., "SummonerName#Tag")
            if "#" not in summoner_input:
                await message.channel.send("Invalid format! Use `!track SummonerName#Tag`.")
                return

            summoner_name, summoner_tag = summoner_input.split("#")

            # Fetch account data
            account = cass.get_account(name=summoner_name, tagline=summoner_tag, region="NA")

            # Get the summoner object
            summoner = cass.get_summoner(name=summoner_name, region="NA")

            # Fetch match history
            match_history = summoner.match_history
            if not match_history:
                await message.channel.send("No recent matches found for this summoner.")
                return

            # Get the most recent match
            match = match_history[0]

            # Find the summoner in the match
            participant = match.participants[summoner]

            # Check if they won
            result = "won" if participant.stats.win else "lost"
            await message.channel.send(f"{summoner.name} {result} their last game!")

        except Exception as e:
            await message.channel.send(f"Error: {e}")

# Run the bot
bot.run(DISCORD_TOKEN)
