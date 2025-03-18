import discord
from discord.ext import commands
from discord import app_commands
from  dotenv import load_dotenv
import os
load_dotenv()
#I have to load the GUILD ID since it takes a while to sync globally 
#testing local you need the @app_commands.guilds(discord.Object(id=GUILD_ID)) decorator
GUILD_ID = int(os.getenv('GUILD_ID'))

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="List available commands.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def help(self, interaction: discord.Interaction):
        # Define the list of commands. Modify this list as needed.
        message = (
            "**Available Commands:**\n"
            "/help - Displays this help message.\n"
            "This is a random test msg"
            # Add other commands here if needed
        )
        await interaction.response.send_message(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))