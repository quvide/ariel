import cassiopeia
from cassiopeia import riotapi

from discord.ext import commands

class League:
    """
    Commands related to League of Legends
    """

    def __init__(self, bot, token):
        riotapi.set_region("EUW")
        riotapi.set_api_key(token)

        self.bot = bot

    @staticmethod
    def format_rank(league):
        """
        Formats a given league nicely. Doesn't work yet if there's multiple entries in the league.
        """

        def is_challenger_or_master(tier):
            return tier == cassiopeia.type.core.common.Tier.challenger or tier == cassiopeia.type.core.common.Tier.master

        return "{tier}{tier_num} ({lp} LP)".format(
            tier = league.tier.value,
            tier_num = (" " + league.entries[0].division.value) if not is_challenger_or_master(league.tier) else "",
            lp = league.entries[0].league_points
        )

    @commands.command()
    async def lastgame(self, username: str):
        """
        Shows brief statistics from the player's last game
        """
        summoner = riotapi.get_summoner_by_name(username)
        game = summoner.recent_games()[0]
        stats = game.stats

        def format_timestamp(seconds):
            """
            Formats seconds as m:ss timestamp
            """
            minutes = seconds//60
            seconds -= minutes*60

            return "{}:{:0>2}".format(minutes, seconds)

        await self.bot.say((
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

    @commands.command()
    async def stats(self, username: str):
        """
        Shows solo ranked standing of player
        """

        summoner = riotapi.get_summoner_by_name(username)
        leagues = summoner.league_entries()

        league = None
        for league_ in leagues:
            if league_.queue == cassiopeia.type.core.common.Queue.ranked_solo:
                league = league_
                break

        if league:
            await self.bot.say((
                "```\n" +
                "{rank} with {wins}W/{losses}L ({percent:.1f}%)\n" +
                "```"
            ).format(
                name = summoner.name,
                rank = League.format_rank(league),
                wins = league.entries[0].wins,
                losses = league.entries[0].losses,
                percent = 100*league.entries[0].wins/(league.entries[0].wins+league.entries[0].losses)
            ))
        else:
            await self.bot.say("{name} is unranked!".format(name = summoner.name))

    @commands.command(pass_context = True)
    async def livegame(self, ctx, username: str):
        """
        Shows champions and their ranks in the current game
        """

        # We expect this command to take a while to run
        self.bot.send_typing(ctx.message.channel)

        summoner = riotapi.get_summoner_by_name(username)
        game = summoner.current_game()
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
                rank = League.format_rank(tiers[participant.summoner]) if participant.summoner in tiers else "UNRANKED"
                return "{:<10}{}".format(participant.champion.name, rank)

            formatted_blue = format_player(blue)
            formatted_red = format_player(red)
            lines.append("{:<38}{}".format(formatted_blue, formatted_red))

        await self.bot.say(
            "```\n" +
            "\n".join(lines) +
            "```"
        )
