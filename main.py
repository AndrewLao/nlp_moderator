import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
GUILD_ID = int(os.getenv('GUILD_ID'))
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded cog: {filename[:-3]}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await load_cogs()
    #remove the bottom 3 lines to make it global
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    
    await bot.tree.sync(guild=guild)

    #await bot.tree.sync()
    print("Synced commands with Discord")
    
bot.run(os.getenv("DISCORD_TOKEN"))