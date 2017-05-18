from config import config

import logging
logging.basicConfig(level=logging.INFO)

import discord
from discord.ext import commands
bot = commands.Bot(**config["bot"])

from league import League
bot.add_cog(League(bot))

from admin import Admin
bot.add_cog(Admin(bot))

@bot.event
async def on_ready():
    print("Logged in")

    await bot.edit_profile(username = config["username"])
    await bot.change_presence(game = discord.Game(name = config["playing"]))

bot.run(config["discord_token"])
