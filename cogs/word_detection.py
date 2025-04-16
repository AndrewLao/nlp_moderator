import discord
from discord.ext import commands
from discord import app_commands
from  dotenv import load_dotenv
import os
import re

GUILD_ID = int(os.getenv('GUILD_ID'))


class WordDetectionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="word_detection", description="Detects a word in a message.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def word_detection(self, interaction: discord.Interaction, word: str):
        await interaction.response.send_message(f"Word detection is set to: {word}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.lower()
        #need to embed the regex and the data seet so I can parese it    
        # Get the word to detect from the command
        word = self.bot.get_cog("WordDetectionCog").word_to_detect

        # Check if the word is in the message content
        if re.search(rf'\b{re.escape(word)}\b', message.content, re.IGNORECASE):
            await message.channel.send(f"Detected the word '{word}' in your message!")




async def setup(bot: commands.Bot):
    await bot.add_cog(WordDetectionCog(bot))
