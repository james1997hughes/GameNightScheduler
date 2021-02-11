import discord
from discord.ext import commands
import sqlite3
import time
import asyncio
import dateparser
import datetime
from embedFactory import embedFactory

class scheduler(commands.Cog):
    def __init__(self, bot, cursor, conn):
        self.bot = bot
        self.cursor = cursor
        self.conn = conn
        self.messagesStack = []
    
    async def askForInput(self, ctx, question):
        def check(m):
            return m.author == ctx.author
        q = await ctx.send(question)
        self.messagesStack.append(q)
        try:
            message = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            raise Exception(f'Timed out asking: {question}')
        else:
            return message.content

    async def saveEvent(self, serverId, eventName, desc, game, mentions, unixTime, channelId, author):
        statement = f'''INSERT INTO events VALUES (NULL, 
                                                {serverId}, 
                                                "{eventName}",
                                                "{desc}",
                                                "{game}",
                                                "{mentions}",
                                                "{unixTime}",
                                                "{channelId}",
                                                "<@!{author}>")'''
        self.cursor.execute(statement)
        self.conn.commit()

    async def cleanUpMessages(self):
        while len(self.messagesStack) > 0:
            await self.messagesStack.pop().delete()

    @commands.command()
    async def schedule(self, ctx):
        serverId = ctx.guild.id
        channelId = ctx.channel.id
        author = ctx.author.id
        try:
            eventName = await self.askForInput(ctx, "Event Name?")
            desc = await self.askForInput(ctx, "Description?")
            game = await self.askForInput(ctx, "What game/activity?")
            mentions = await self.askForInput(ctx, "Who do you want to notify? @ mention them here")
            time = await self.askForInput(ctx, "When is the event?")
            try: #need to implement retry for time
                timeUnix = int(dateparser.parse(time).timestamp())
            except Exception as e:
                print(e)
            await ctx.send(embed=embedFactory(eventName=eventName,
                                            desc=desc,
                                            game=game,
                                            unixTime=timeUnix,
                                            mentions=mentions,
                                            creator=f'{author}'))

            await self.saveEvent(serverId=serverId,
                                eventName=eventName,
                                desc=desc,
                                game=game,
                                mentions=mentions,
                                unixTime=timeUnix,
                                channelId=channelId,
                                author=author)
            await self.cleanUpMessages()
        except:
            await self.cleanUpMessages()
            await ctx.send('Scheduling timed out, try again with ^schedule')