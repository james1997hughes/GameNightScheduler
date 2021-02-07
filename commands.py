from discord.ext import commands
import sqlite3
import time
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


@commands.command()
async def schedule(ctx, eventName, desc, game, when, *people):
    serverId = ctx.guild.id
    channelId = ctx.channel.id
    author = ctx.author.id
    tempTime = int(time.time()) + int(when)  #currently currentTime + X seconds
    who = ''
    for user in people:
        who = who + user + ' '

    statement = f'''INSERT INTO events VALUES (NULL, 
                                            {serverId}, 
                                            "{eventName}",
                                            "{desc}",
                                            "{game}",
                                            "{who}",
                                            "{tempTime}",
                                            "{channelId}",
                                            "{author}")'''
    print(statement)
    cursor.execute(statement)
    conn.commit()
    await ctx.send(statement)


def setup(bot):
    bot.add_command(events)
    bot.add_command(servers)
    bot.add_command(register)
    bot.add_command(schedule)