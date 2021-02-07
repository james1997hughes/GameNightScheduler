import discord
from config import DISCORD_API_TOKEN
from discord.ext import commands
import sqlite3
from commands import events, servers
from waitloop import waitloop

bot = commands.Bot(command_prefix='^')
conn = sqlite3.connect('schedulerData.db')
cursor = conn.cursor()

cursor.execute(
    '''CREATE TABLE if not exists servers (id INTEGER PRIMARY KEY, name TEXT)'''
)
cursor.execute(
    'CREATE TABLE IF NOT EXISTS events ("id" INTEGER PRIMARY KEY, "fk_servers" INTEGER, "name" TEXT, "description" TEXT, "game" TEXT, "mentions" TEXT, "time" INTEGER, "channelId" TEXT, "author" TEXT)'
)
# ID | NAME | DESCRIPTION | GAME | MENTIONS | TIME
conn.close()

bot.load_extension('commands')
bot.add_cog(waitloop(bot))


@bot.event
async def on_guild_join(guild):
    conn = sqlite3.connect('schedulerData.db')
    cursor = conn.cursor()
    safeName = guild.name.replace("\'", "")
    serverId = guild.id
    statement = f"INSERT INTO servers VALUES ( {serverId} , '{safeName}')"
    print(statement)
    cursor.execute(statement)
    conn.commit()
    conn.close()


bot.run(DISCORD_API_TOKEN)