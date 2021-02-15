import discord
from config import DISCORD_API_TOKEN
from discord.ext import commands as discCommands
import sqlite3
import commands
from waitloop import waitloop
from scheduler import scheduler
from events import events
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s:%(message)s')

bot = discCommands.Bot(command_prefix='^')
conn = sqlite3.connect('schedulerData.db')
cursor = conn.cursor()

cursor.execute(
    '''CREATE TABLE if not exists servers (id INTEGER PRIMARY KEY, name TEXT, total_events INTEGER)'''
)
cursor.execute(
    'CREATE TABLE IF NOT EXISTS events ("id" INTEGER PRIMARY KEY, "event_id" INTEGER, "fk_servers" INTEGER, "name" TEXT, "description" TEXT, "game" TEXT, "mentions" TEXT, "time" INTEGER, "channel_id" TEXT, "author" TEXT)'
)
# ID | FK_SERVERS | NAME | DESCRIPTION | GAME | MENTIONS | TIME | CHANNELID | AUTHORID

bot.load_extension('commands')
bot.add_cog(waitloop(bot))
bot.add_cog(scheduler(bot, cursor, conn))
bot.add_cog(events(bot, conn))


@bot.event
async def on_guild_join(guild):
    conn = sqlite3.connect('schedulerData.db')
    cursor = conn.cursor()
    safeName = guild.name.replace("\'", "")
    serverId = guild.id
    statement = f"INSERT INTO servers VALUES ( {serverId} , '{safeName}', 0)"
    print(statement)
    cursor.execute(statement)
    conn.commit()
    conn.close()


bot.run(DISCORD_API_TOKEN)