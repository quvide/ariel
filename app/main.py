import random
import logging
import discord

from discord.ext import commands
from config import config
from league import League
from admin import Admin

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(**config["bot"])
bot.add_cog(League(bot))
bot.add_cog(Admin(bot))


@bot.event
async def on_ready():
    print("Logged in")

    await bot.edit_profile(username=config["username"])
    await bot.change_presence(game=discord.Game(name=config["playing"]))


@bot.command()
async def quote():
    """
    Displays a random quote
    """
    await bot.say(random.choice(config["quotes"]))

bot.run(config["discord_token"])
