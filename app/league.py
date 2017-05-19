import cassiopeia
from cassiopeia import riotapi

import discord
from discord.ext import commands

from enum import Enum
from config import config
import random

def add_random_footer(em):
    em.set_footer(text=random.choice(config["quotes"]))

def format_rank(league):
    """
    Formats a given league nicely. Doesn't work yet if there's multiple entries in the league.
    """

    def is_challenger_or_master(tier):
        return tier == cassiopeia.type.core.common.Tier.challenger or tier == cassiopeia.type.core.common.Tier.master

    return "{tier}{tier_num} ({lp} LP)".format(
        tier = league.tier.value[0] + league.tier.value[1:].lower(),
        tier_num = (" " + league.entries[0].division.value) if not is_challenger_or_master(league.tier) else "",
        lp = league.entries[0].league_points
    )

def format_winrate(wins, losses):
    return "{}W/{}L ({:.1f}%)".format(
        wins,
        losses,
        100*wins/(wins+losses)
    )

def champion_image_url(file):
    return "http://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}".format(
        config["lol_version"],
        file
    )

def profile_icon_url(id):
    return "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(
        config["lol_version"],
        id
    )


class Lanes(Enum):
    top_lane = "top"
    jungle = "jungle"
    mid_lane = "mid"
    bot_lane = "bot"

class League:
    """
    Commands related to League of Legends
    """

    def __init__(self, bot):
        riotapi.set_region("EUW")
        riotapi.set_api_key(config["riot_token"])

        self.bot = bot

    @commands.command(pass_context = True)
    async def lastgame(self, ctx, username: str, n: int=1):
        """
        [summoner] (n) Shows brief statistics from the player's last game
        """

        # We expect this command to take a while to run
        self.bot.send_typing(ctx.message.channel)

        n = n-1

        try:
            summoner = riotapi.get_summoner_by_name(username)
        except:
            await self.bot.say("Couldn't find that summoner!")
            return

        try:
            game = summoner.recent_games()[n]
        except:
            await self.bot.say("Couldn't find recent games!")
            return

        stats = game.stats

        def format_timestamp(seconds):
            """
            Formats seconds as m:ss timestamp
            """
            minutes = seconds//60
            seconds -= minutes*60

            return "{}:{:0>2}".format(minutes, seconds)


        em = discord.Embed(title=("Victory" if game.stats.win else "Defeat") + " in {}".format(format_timestamp(stats.time_played)), description="{} in {}".format(game.champion.name, Lanes[stats.lane.name].value), colour=config["embed_colour"])

        em.set_thumbnail(url=champion_image_url(game.champion.image.link))

        em.add_field(name="Stats", value="{}/{}/{} ({})".format(
            stats.kills,
            stats.deaths,
            stats.assists,
            stats.minion_kills
        ))

        em.add_field(name="Spells", value="{} and {}".format(game.summoner_spell_d.name, game.summoner_spell_f.name))

        add_random_footer(em)

        await self.bot.say(embed=em)

    @commands.command(pass_context = True)
    async def stats(self, ctx, username: str):
        """
        Shows solo ranked standing of player
        """

        # We expect this command to take a while to run
        self.bot.send_typing(ctx.message.channel)

        try:
            summoner = riotapi.get_summoner_by_name(username)
        except:
            await self.bot.say("Couldn't find that summoner!")
            return

        try:
            leagues = summoner.league_entries()
        except:
            await self.bot.say("That summoner isn't ranked!")
            return

        ranked = None
        for league in leagues:
            if league.queue == cassiopeia.type.core.common.Queue.ranked_solo:
                ranked = league
                break

        em = discord.Embed(title=summoner.name, description="Level {}".format(summoner.level), colour=config["embed_colour"])

        em.set_thumbnail(url=profile_icon_url(summoner.profile_icon_id))

        if ranked:
            em.add_field(
                name="Ranked",
                value="{}\n{}".format(
                    format_rank(league),
                    format_winrate(league.entries[0].wins, league.entries[0].losses)
                )
            )

        add_random_footer(em)

        await self.bot.say(embed=em)

    @commands.command(pass_context=True)
    async def livegame(self, ctx, username: str):
        """
        Shows champions and their ranks in the current game
        """

        # We expect this command to take a while to run
        self.bot.send_typing(ctx.message.channel)

        try:
            summoner = riotapi.get_summoner_by_name(username)
        except:
            await self.bot.say("Couldn't find that summoner!")
            return

        try:
            game = summoner.current_game()
        except:
            await self.bot.say("Seems like that summoner is not in a game!")
            return

        participants = game.participants

        entries = riotapi.get_league_entries_by_summoner([p.summoner for p in participants])
        tiers = {}
        for n, leagues in enumerate(entries):
            for league in leagues:
                if league.queue == cassiopeia.type.core.common.Queue.ranked_solo:
                    tiers[participants[n].summoner] = league
                    break

        team_blue = []
        team_red = []

        for p in participants:
            if p.side == cassiopeia.type.core.common.Side.blue:
                team_blue.append(p)
            elif p.side == cassiopeia.type.core.common.Side.red:
                team_red.append(p)

        lines = []
        for blue, red in zip(team_blue, team_red):
            def format_player(participant):
                rank = format_rank(tiers[participant.summoner]) if participant.summoner in tiers else "UNRANKED"
                return "{:<10}{}".format(participant.champion.name, rank)

            formatted_blue = format_player(blue)
            formatted_red = format_player(red)
            lines.append("{:<38}{}".format(formatted_blue, formatted_red))

        await self.bot.say(
            "```\n" +
            "\n".join(lines) +
            "```"
        )
