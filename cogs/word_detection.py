import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import pandas as pd
import re

import emoji
from transformers import AutoTokenizer


GUILD_ID = int(os.getenv("GUILD_ID"))


class WordDetectionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.flagged_words = set()
        self.load_flagged_words()
        self.tokenizer = AutoTokenizer.from_pretrained(
            "bert-base-uncased", do_lower_case=True
        )

    def load_flagged_words(self):
        """Load flagged words from a text file"""
        try:
            # Path to the flagged words file
            file_path = os.path.join(
                os.path.dirname(__file__), "..", "flagged_words.txt"
            )

            with open(file_path, "r", encoding="utf-8") as file:
                # Read all lines, strip whitespace, and convert to lowercase
                words = [line.strip().lower() for line in file if line.strip()]
                self.flagged_words = set(words)
                print(f"Loaded {len(self.flagged_words)} flagged words")
        except FileNotFoundError:
            print("flagged_words.txt not found. Creating empty set.")
            self.flagged_words = set()
        except Exception as e:
            print(f"Error loading flagged words: {e}")
            self.flagged_words = set()

    # Function for parsing discord stuff and urls to make the tokenization easier
    def clean_text(self, text: str) -> str:
        """
        1) Replace URLs with [URL]
        2) Replace user mentions (<@12345>) with [USER]
        3) Convert emojis to :short_codes:
        4) Collapse repeated punctuation (e.g. "!!!"→"!")
        5) Normalize whitespace
        """

        # 1) URLs
        text = re.sub(r"https?://\S+|www\.\S+", "[URL]", text)

        # 2) Discord mentions
        text = re.sub(r"<@!?\d+>", "[USER]", text)

        # 3) Emojis → :emoji_name:
        text = emoji.demojize(text, delimiters=(":", ";"))

        # 4) Collapse repeated punctuation
        text = re.sub(r"([!?.,])\1{1,}", r"\1", text)

        # 5) Whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def tokenize_words(self, words):
        if isinstance(words, str):
            words = [words]
        else:
            raise TypeError("Input must be a string or a list of strings")

        cleaned = [self.clean_text(w) for w in words]
        
        print(f"Raw Cleaned Text:\n{cleaned}")

        # note that doing it this way the shape of each tensor isn't guaranteed to be
        # the same size so you will end up needing to make sure each bath is dimensionally equal
        encoding = self.tokenizer(
            cleaned,
            padding=True,
            truncation=True,  # needed b/c max BERT model size is 512 tokens
            return_tensors="pt",  # pytorch tensor. Change if different model is used.
            return_offsets_mapping=True,
        )

        return encoding["input_ids"], encoding["attention_mask"]

    @app_commands.command(
        name="reload_words", description="Reload the flagged words from the text file."
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def reload_words(self, interaction: discord.Interaction):
        """Command to reload the flagged words file"""
        self.load_flagged_words()
        await interaction.response.send_message(
            f"Reloaded {len(self.flagged_words)} flagged words from file."
        )

    @app_commands.command(
        name="word_count",
        description="Show how many words are currently being monitored.",
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def word_count(self, interaction: discord.Interaction):
        """Command to show the number of flagged words"""
        await interaction.response.send_message(
            f"Currently monitoring {len(self.flagged_words)} flagged words."
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not self.flagged_words:
            return

        content = message.content.lower()

        # BERT tokenizer comes with a few classes token maps.
        # Input ID is just the numerical representation
        # There are others but since we are only doing 1 message at a time
        # That shouldn't be an issue until we start training
        input_ids, attention_mask = self.tokenize_words(message.content)
        print(f"Input ID:\n{input_ids}")
        # print(f"Attention Mask:\n{attention_mask}")

        detected_words = []
        # Check for each flagged word in the message
        for word in self.flagged_words:
            # Use word boundaries to match whole words only
            pattern = rf"\b{re.escape(word)}\b"
            if re.search(pattern, content, re.IGNORECASE):
                detected_words.append(word)

        # If any flagged words were found, take action
        # Got to change where these msgs are being posted
        if detected_words:
            embed = discord.Embed(
                title="Flagged Content Detected",
                description=f"Detected flagged word(s): {', '.join(detected_words)}",
                color=discord.Color.red(),
            )
            embed.add_field(name="User", value=message.author.mention, inline=True)
            embed.add_field(name="Channel", value=message.channel.mention, inline=True)

            # Send to a moderation channel or respond in the same channel
            await message.channel.send(embed=embed)

            # Optional: Delete the message
            # await message.delete()


async def setup(bot: commands.Bot):
    await bot.add_cog(WordDetectionCog(bot))
