import discord
from discord.ext import commands

from config import config

def is_authorized():
    """
    Decorator that checks if the user is an admin
    """
    def predicate(ctx):
        if isinstance(ctx.message.author, discord.Member):
            for role in ctx.message.author.roles:
                if role.name in config["admin_role_names"]:
                    return True

        return ctx.message.author.id in config["admin_user_ids"]

    return commands.check(predicate)

class Admin:
    """
    Commands available for admins only
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    @is_authorized()
    async def delete(self, ctx, _id: str, n: int):
        """
        [user_id] [n] Deletes last n messages by user from this channel
        """

        await self.bot.delete_message(ctx.message)

        user = await self.bot.get_user_info(_id)
        to_remove = set()

        async for message in self.bot.logs_from(ctx.message.channel):
            if message.author == user and len(to_remove) < n:
                to_remove.add(message)

        await self.bot.delete_messages(to_remove)
