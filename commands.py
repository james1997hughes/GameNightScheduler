from discord.embeds import Embed
from discord.ext import commands
import sqlite3
import time
import discord
conn = sqlite3.connect('schedulerData.db')
cursor = conn.cursor()


@commands.command()
async def events(ctx):
    print("events")
    serverId = ctx.guild.id
    statement = f"SELECT * FROM events WHERE fk_servers = {serverId}"
    results = cursor.execute(statement).fetchall()
    print(results)
    await ctx.send(results)


@commands.command()
async def test(ctx):
    print("test")
    Title = "📆 ⏰ Game Night Test Event"
    game = "Minecraft"
    friendlyTime = "22-01-2021 19:30 GMT"
    description = "Let's build some shit"
    creator = "<@!185514524449701888>"
    myEmbed = discord.Embed(
        title=Title,
        description=description)
    myEmbed.add_field(name="Time",
                      value=friendlyTime,
                      inline=False)
    myEmbed.add_field(name="Mentions",
                      value="<@!185514524449701888> <@!185514524449701888> <@!185514524449701888>",
                      inline=False)
    myEmbed.set_footer(text=f"Event scheduled by: {creator}")
    myEmbed.set_author(name=game, icon_url="https://store-images.s-microsoft.com/image/apps.45782.9007199266731945.debbc4f1-cde0-491b-8c6f-b6b015eecab6.4716cccc-5f37-4bb5-9db1-0c1dbc99003f?mode=scale&q=90&h=200&w=200&background=%23000000")
    await ctx.send(embed=myEmbed)


@commands.command()
async def servers(ctx):
    statement = "SELECT * FROM servers"
    await ctx.send(cursor.execute(statement).fetchall())


@commands.command()
async def register(ctx):
    safeName = ctx.guild.name.replace("\'", "")
    serverId = ctx.guild.id
    statement = f"INSERT INTO servers VALUES ( {serverId} , '{safeName}')"
    cursor.execute(statement)
    conn.commit()
    await ctx.send("Server Registered")

def check(author):
    def inner_check(message): 
        if message.author != author:
            return False
    return inner_check

def setup(bot):
    bot.add_command(events)
    bot.add_command(servers)
    bot.add_command(register)
    bot.add_command(test)