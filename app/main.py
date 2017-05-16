import asyncio

import logging
logging.basicConfig(level=logging.INFO)

import ruamel.yaml as yaml
with open("config.yaml") as file:
    CONFIG = yaml.safe_load(file)

from cassiopeia import riotapi
riotapi.set_region("EUW")
riotapi.set_api_key(CONFIG["riot_token"])

import discord
from discord.ext import commands
client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
    print("Logged in")

    await asyncio.sleep(1)
    await client.edit_profile(username = CONFIG["username"])
    await client.change_presence(game = discord.Game(name = CONFIG["playing"]))

@client.command()
async def lastgame(username: str):
    summoner = riotapi.get_summoner_by_name(username)
    game = riotapi.get_recent_games(summoner)[0]
    stats = game.stats

    def format_timestamp(seconds):
        minutes = seconds//60
        seconds -= minutes*60

        return "{}:{:0>2}".format(minutes, seconds)

    await client.say((
        "```\n" +
        "Game: {win} in {time}\n"
        "Champion: {champion} in {lane} \n" +
        "Stats: {kills}/{deaths}/{assists} and {cs} cs\n" +
        "Spells: {spell_d} and {spell_f}\n" +
        "```"
    ).format(
        win = "won" if stats.win else "lost",
        time = format_timestamp(stats.time_played),

        champion = game.champion,
        lane = stats.lane.value,
        kills = stats.kills,
        deaths = stats.deaths,
        assists = stats.assists,
        cs = stats.minion_kills,

        spell_d = game.summoner_spell_d.name,
        spell_f = game.summoner_spell_f.name,
    ))

#@client.command()
#async def stats(username: str):
#    summoner = riotapi.get_summoner_by_name(username)
#    await client.say((
#        "```\n" +
#        "{name} is in {rank} with {wins} / {losses}\n" +
#        "```"
#    ).format(
#        name = summoner.name
#        rank = summoner.ranked_stats1
#    )
#    ))

@client.command(pass_context=True)
async def close(ctx):
    if (ctx.message.author.id in CONFIG["admins"]):
        await client.close()
        exit()

client.run(CONFIG["discord_token"])
