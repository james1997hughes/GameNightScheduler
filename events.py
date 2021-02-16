import logging
import discord
from discord import embeds
from discord.ext import tasks, commands
import sqlite3
import time
from prettytable.prettytable import MARKDOWN, MSWORD_FRIENDLY, ORGMODE, PLAIN_COLUMNS
import texttable
import datetime
from embedFactory import embedFactory, getAttendees
from prettytable import PrettyTable

class eventObj:
    def __init__(self, eventRow):
        self.id = eventRow[0]
        self.eventId = eventRow[1]
        self.serverId = eventRow[2]
        self.title = eventRow[3]
        self.description = eventRow[4]
        self.game = eventRow[5]
        self.time = eventRow[6]
        self.channelId = eventRow[7]
        self.author = eventRow[8]
        #TODO Add author friendly name

        self.friendlyTime = datetime.datetime.fromtimestamp(int(self.time)).strftime('%Y-%m-%d %H:%M:%S')

    
    def toEmbed(self, preview: bool, active: bool):
        return embedFactory(self.title,
                            self.description,
                            self.game,
                            self.time,
                            self.author,
                            f"Event scheduled by {self.author}",
                            self.eventId,
                            self.serverId,
                            preview,
                            active)



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
        statement = f"SELECT * FROM events WHERE fk_servers = (SELECT id FROM servers WHERE server_id = '{serverId}')"
        results = self.cursor.execute(statement).fetchall()
        logging.info(results)
        for result in results:
            event = eventObj(result)
            unixTimeTill = event.time - time.time()
            timeTill = datetime.timedelta(seconds=unixTimeTill)
            tableTest.add_row([event.eventId, event.title[:30], str(timeTill)[:-10]])
        
        serverName = ctx.message.guild.name
        desc = f"Events Schedule for {serverName}\n```{tableTest}```"
        return desc

    @commands.command()
    async def events(self, ctx):
        serverId = ctx.guild.id
        eventsTable = await self.generateEventsTable(serverId, ctx)
        await ctx.send(eventsTable)

    @commands.command()
    async def ping(self, ctx, message):
        await ctx.send("pong!")

    @commands.command()
    async def describe(self, ctx, message):
        try:
            event = int(message)
            statement = f"SELECT * FROM events WHERE event_id = {event} AND fk_servers = (SELECT id FROM servers WHERE server_id = '{ctx.guild.id}')"
            results = self.cursor.execute(statement).fetchall()
            for result in results:
                toSend = eventObj(result)
                await ctx.send(embed=toSend.toEmbed(preview=False, active=False))
        except:
            await ctx.send("Pls provide a valid event id")

    async def getMentions(self, eventId, serverId):
        statement = f'''SELECT eu.userId FROM events_users eu 
                JOIN events e on eu.fk_events = e.id 
                JOIN servers s on s.id = e.fk_servers
                WHERE e.event_id = {eventId} AND s.server_id = "{serverId}"'''
        results = self.cursor.execute(statement).fetchall()
        return results

    @commands.command()
    async def join(self, ctx, message):
        try:
            eventId = int(message)
            selectStatement = f'''SELECT id, name FROM events WHERE event_id = {eventId} AND fk_servers = (SELECT id FROM servers WHERE server_id = "{ctx.guild.id}")'''
            results = self.cursor.execute(selectStatement).fetchone()
            existingMembers = await self.getMentions(eventId=eventId, serverId=ctx.guild.id)
            logging.info(str(ctx.author.id))
            logging.info(existingMembers)
            logging.info(len([]))
            if len(existingMembers) > 0:
                testArr = [item[0] for item in existingMembers]
                logging.info(testArr)
                if ctx.author.id in testArr:
                    await ctx.send(f"You are already in this event. Leave with ^leave {eventId}")
                    return False

            insertStatement = f'''INSERT INTO events_users 
                                                (id,
                                                fk_events, 
                                                fk_servers,
                                                userId, 
                                                userName)
                                        VALUES (NULL, 
                                                {results[0]},
                                                (SELECT id FROM servers WHERE server_id = "{ctx.guild.id}"),
                                                {ctx.author.id}, 
                                                '{str(ctx.author)}')'''
            logging.info(insertStatement)
            logging.info(self.cursor.execute(insertStatement))
            self.conn.commit()
            await ctx.send(f"{str(ctx.author)} has joined {results[1]}!")
        except:
            await ctx.send('Something went wrong joining. Try again...?')

    @commands.command()
    async def leave(self, ctx, message):
        try:
            eventId = int(message)
            existingMembers = await self.getMentions(eventId=eventId, serverId=ctx.guild.id)
            logging.info(existingMembers)
            if len(existingMembers) > 0:
                testArr = [item[0] for item in existingMembers]
                if ctx.author.id in testArr:
                    statement = f'''DELETE FROM events_users WHERE id IN(
                                                    SELECT eu.id FROM events_users eu 
                                                    JOIN events e on eu.fk_events = e.id 
                                                    JOIN servers s on s.id = e.fk_servers
                                                    WHERE e.event_id = {eventId} 
                                                    AND s.server_id = "{ctx.guild.id}"
                                                    AND eu.userId = {ctx.author.id})'''
                    await ctx.send(f"{ctx.author.name} removed.")
                    self.cursor.execute(statement)
                    self.conn.commit()
                    return
        except:
            await ctx.send('Something went wrong leaving. Try again...?')
