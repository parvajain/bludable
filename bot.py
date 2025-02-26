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
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    if message.content.startswith("!track"):
        # Extract summoner name and tag
        try:
            summoner_input = message.content.split(" ")[1]  # Get the full input (e.g., "SummonerName#Tag")
            summoner_name, summoner_tag = summoner_input.split("#")  # Split into name and tag
        except ValueError:
            await message.channel.send("Invalid format! Use `!track SummonerName#Tag`.")
            return

        await message.channel.send(f"Fetching data for {summoner_name} ({summoner_tag})...")

        try:
            # Fetch account data using Cassiopeia
            account = cass.get_account(name=summoner_name, tag=summoner_tag, region="NA")
            summoner = account.summoner  # Get the summoner object

            # Fetch match history
            match_history = summoner.match_history
            match = match_history[0]  # Get most recent match
            participant = match.participants[summoner]  # Find the summoner in the match

            # Format the response
            response = (
                f"**{summoner.name}** played **{participant.champion.name}** and "
                f"**{'won' if participant.stats.win else 'lost'}**.\n"
                f"KDA: {participant.stats.kills}/{participant.stats.deaths}/{participant.stats.assists}"
            )
            await message.channel.send(response)

        except NotFoundError:
            await message.channel.send("Error: Summoner not found.")
        except Exception as e:
            print(f"Error: {e}")  # Print the full error to the console
            await message.channel.send(f"Error: {e}")

# Run the bot
bot.run(DISCORD_TOKEN)
