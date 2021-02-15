import logging
import discord
from discord import embeds
from discord.ext import tasks, commands
import sqlite3
import time
from prettytable.prettytable import MARKDOWN, MSWORD_FRIENDLY, ORGMODE, PLAIN_COLUMNS
import texttable
import datetime
from embedFactory import embedFactory
from prettytable import PrettyTable

class eventObj:
    def __init__(self, eventRow):
        self.id = eventRow[0]
        self.eventId = eventRow[1]
        self.serverId = eventRow[2]
        self.title = eventRow[3]
        self.description = eventRow[4]
        self.game = eventRow[5]
        self.mentions = eventRow[6]
        self.time = eventRow[7]
        self.channelId = eventRow[8]
        self.author = eventRow[9]

        self.friendlyTime = datetime.datetime.fromtimestamp(int(self.time)).strftime('%Y-%m-%d %H:%M:%S')

    
    def toEmbed(self):
        return embedFactory(self.title,
                            self.description,
                            self.game,
                            self.time,
                            self.mentions,
                            self.author,
                            f"Event scheduled by {self.author}")



class events(commands.Cog):
    def __init__(self, bot, conn):
        self.bot = bot
        self.conn = conn
        self.cursor = self.conn.cursor()

    def cog_unload(self):
        self.conn.close()

    async def generateEventsTable(self, serverId, ctx):

        tableTest = PrettyTable(field_names=["Id", "Title", "When"])
        tableTest.set_style(ORGMODE)
        statement = f"SELECT * FROM events WHERE fk_servers = {serverId}"
        results = self.cursor.execute(statement).fetchall()
        eventList = "**ID**\t|\t**Title**\t|\t**When**\n"
        for result in results:
            event = eventObj(result)
            unixTimeTill = event.time - time.time()
            timeTill = datetime.timedelta(seconds=unixTimeTill)
            eventList += f"```{event.eventId}\t{event.title}\t{event.friendlyTime}\n```"
            tableTest.add_row([event.eventId, event.title[:30], str(timeTill)[:-10]])
        
        serverName = ctx.message.guild.name
        desc = f"Events Schedule for {serverName}\n```{tableTest}```"
        return desc

    @commands.command()
    async def events(self, ctx):
        print("events")
        serverId = ctx.guild.id
        eventsTable = await self.generateEventsTable(serverId, ctx)
        await ctx.send(eventsTable)

    @commands.command()
    async def testCommand(self, ctx, message):
        await ctx.send(message)

    @commands.command()
    async def describe(self, ctx, message):
        try:
            event = int(message)
            statement = f"SELECT * FROM events WHERE event_id = {event} AND fk_servers = {int(ctx.guild.id)}"
            results = self.cursor.execute(statement).fetchall()
            for result in results:
                toSend = eventObj(result)
                await ctx.send(embed=toSend.toEmbed())
        except:
            await ctx.send("Pls provide a valid event id")
