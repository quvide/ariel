import discord
from discord.ext import commands

class Admin:
    """
    Commands available for admins only
    """

    def __init__(self, bot, admin_role_names, admin_user_ids):
        self.bot = bot
        self.admin_role_names = admin_role_names
        self.admin_user_ids = admin_user_ids

    def __check(self, ctx):
        if isinstance(ctx.message.author, discord.Member):
            for role in ctx.message.author.roles:
                if role.name in self.admin_role_names:
                    return True

        if ctx.message.author.id in self.admin_user_ids:
            return True

        return False

    @commands.command()
    async def close(self):
        """
        Disconnects the bot from Discord
        """

        await self.bot.reply("Farewell!")
        await self.bot.logout()
        await self.bot.close()
        exit()

    @commands.command(pass_context = True)
    async def delete(self, ctx, _id: str, n: int):
        """
        [user_id] [n] Deletes last n messages by user from this channel
        """
        await self.bot.delete_message(ctx.message)
        
        user = await self.bot.get_user_info(_id)
        to_remove = set()

        async for message in self.bot.logs_from(ctx.message.channel):
            if message.author == user and len(to_remove) < n:
                print(to_remove)
                to_remove.add(message)

        await self.bot.delete_messages(to_remove)
