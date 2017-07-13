import random
import logging
import discord
import asyncio
import datetime

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

    for server in bot.servers:
        await bot.change_nickname(server.me, config["username"])

    await bot.change_presence(game=discord.Game(name=config["playing"]))

    while True:
        for server in bot.servers:
            for channel in server.channels:
                if channel.id in config["autodel_channel_ids"]:
                    time = datetime.datetime.utcnow()
                    d = datetime.timedelta(seconds=config["autodel_time"])
                    await bot.purge_from(channel, before=time-d)

        await asyncio.sleep(1)


@bot.command()
async def quote():
    """
    Displays a random quote
    """
    await bot.say(random.choice(config["quotes"]))

bot.run(config["discord_token"])
