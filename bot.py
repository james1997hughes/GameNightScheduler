import discord
from config import DISCORD_API_TOKEN
from discord.ext import commands
import sqlite3

bot = commands.Bot(command_prefix='^')
conn = sqlite3.connect('schedulerData.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE if not exists servers (id INTEGER PRIMARY KEY, name TEXT)''')
cursor.execute('CREATE TABLE IF NOT EXISTS events ("id" INTEGER PRIMARY KEY, "fk_servers" INTEGER, "name" TEXT, "description" TEXT, "game" TEXT, "mentions" TEXT, "time" INTEGER)')
# ID | NAME | DESCRIPTION | GAME | MENTIONS | TIME


@bot.command()
async def register(ctx):
    safeName = ctx.guild.name.replace("\'", "")
    serverId = ctx.guild.id
    statement = f"INSERT INTO servers VALUES ( {serverId} , '{safeName}')"
    cursor.execute(statement)
    conn.commit()
    await ctx.send("Server Registered")

@bot.command()
async def schedule(ctx, eventName, desc, game, when, *people):
    serverId = ctx.guild.id
    who = ''
    for user in people:
        who = who + user + ' '
    statement = f'INSERT INTO events VALUES (NULL, {serverId}, "{eventName}", "{desc}", "{game}", "{who}", "{when}")'
    print(statement)
    cursor.execute(statement)
    conn.commit()
    await ctx.send(statement)


@bot.command()
async def events(ctx):
    print("events")
    serverId = ctx.guild.id
    statement = f"SELECT * FROM events WHERE fk_servers = {serverId}"
    results = cursor.execute(statement).fetchall()
    print(results)
    await ctx.send(results)

@bot.command()
async def servers(ctx):
    statement = "SELECT * FROM servers"
    await ctx.send(cursor.execute(statement).fetchall())

@bot.event
async def on_guild_join(guild):
    safeName = guild.name.replace("\'", "")
    serverId = guild.id
    statement = f"INSERT INTO servers VALUES ( {serverId} , '{safeName}')"
    print(statement)
    cursor.execute(statement)
    conn.commit()

bot.run(DISCORD_API_TOKEN)