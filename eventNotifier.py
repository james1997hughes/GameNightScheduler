import discord
from discord.ext import commands


class eventNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cogTest(self, ctx):
        await ctx.send("Hi cogs works")
    

def setup(bot):
    bot.add_cog(eventNotifier(bot))