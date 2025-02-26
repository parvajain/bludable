import discord
import cassiopeia as cass
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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
    """
    This function runs when the bot is ready and connected to Discord.
    """
    logger.info(f"Logged in as {bot.user}!")

@bot.event
async def on_message(message):
    """
    This function runs whenever a message is sent in a channel the bot can see.
    """
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if the message starts with the command
    if message.content.startswith("!track"):
        logger.info(f"Received !track command from {message.author}: {message.content}")

        try:
            # Extract summoner name and tag
            parts = message.content.split(" ")
            if len(parts) < 2:
                logger.warning("Invalid format: No summoner name provided.")
                await message.channel.send("Invalid format! Use `!track SummonerName#Tag`.")
                return

            summoner_input = parts[1]  # Get the full input (e.g., "SummonerName#Tag")
            if "#" not in summoner_input:
                logger.warning(f"Invalid format: No '#' found in input '{summoner_input}'.")
                await message.channel.send("Invalid format! Use `!track SummonerName#Tag`.")
                return

            # Split summoner name and tag
            summoner_name, summoner_tag = summoner_input.split("#")
            logger.info(f"Fetching data for summoner: {summoner_name} (Tag: {summoner_tag})...")

            # Fetch account data
            account = cass.get_account(name=summoner_name, tagline=summoner_tag, region="NA")
            logger.info(f"Account data fetched: PUUID = {account.puuid}")

            # Get the summoner object
            summoner = cass.Summoner(name=summoner_name, region="NA")  # Updated line
            logger.info(f"Summoner data fetched: Summoner ID = {summoner.id}, Name = {summoner.name}")

            # Fetch match history
            match_history = summoner.match_history
            if not match_history:
                logger.warning("No match history found for this summoner.")
                await message.channel.send("No recent matches found for this summoner.")
                return

            # Get the most recent match
            match = match_history[0]
            logger.info(f"Most recent match found: Match ID = {match.id}")

            # Find the summoner in the match
            participant = match.participants[summoner]
            logger.info(f"Participant data fetched: Champion = {participant.champion.name}, KDA = {participant.stats.kills}/{participant.stats.deaths}/{participant.stats.assists}")

            # Check if they won
            result = "won" if participant.stats.win else "lost"
            await message.channel.send(f"{summoner.name} {result} their last game!")

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            await message.channel.send(f"Error: {e}")

# Run the bot
logger.info("Starting the bot...")
bot.run(DISCORD_TOKEN)
