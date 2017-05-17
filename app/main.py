import logging
logging.basicConfig(level=logging.INFO)

import ruamel.yaml as yaml
with open("config.yaml") as file:
    CONFIG = yaml.safe_load(file)

import discord
from discord.ext import commands
bot = commands.Bot(**CONFIG["bot"])

from league import League
bot.add_cog(League(bot, CONFIG["riot_token"]))

from admin import Admin
bot.add_cog(Admin(bot, CONFIG["admin_role_names"], CONFIG["admin_user_ids"]))

@bot.event
async def on_ready():
    print("Logged in")

    await bot.edit_profile(username = CONFIG["username"])
    await bot.change_presence(game = discord.Game(name = CONFIG["playing"]))

bot.run(CONFIG["discord_token"])
