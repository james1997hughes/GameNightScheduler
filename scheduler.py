import discord
from discord.ext import commands
import sqlite3
import time
import asyncio
import dateparser
import datetime
from embedFactory import embedFactory
import logging


class scheduler(commands.Cog):
    def __init__(self, bot, cursor, conn):
        self.bot = bot
        self.cursor = cursor
        self.conn = conn
        self.messagesStack = []

    async def awaitInput(self, ctx, author):
        def check(m):
            return m.author == author
        
        try:
            message = await self.bot.wait_for('message',
                                              timeout=30.0,
                                              check=check)
        except asyncio.TimeoutError:
            raise Exception('Timed out')
        else:
            logging.getLogger('__name__').debug('Worked')
            self.cleanUpMessages()
            return message.content

    async def awaitReaction(self, ctx, msg):
        def check(reaction, user):
            if reaction.message == msg and user == ctx.author:
                return str(reaction.emoji) == '✅' or '❌'

        try:
            event = await self.bot.wait_for('reaction_add',
                                            timeout=30.0,
                                            check=check)
        except asyncio.TimeoutError:
            raise Exception('Timed out')
        else:

            return str(event[0].emoji)

    async def askForInput(self, ctx, author, question):
        q = await ctx.send(question)
        self.messagesStack.append(q)
        def check(m):
            return m.author == author
        
        try:
            message = await self.bot.wait_for('message',
                                              timeout=30.0,
                                              check=check)
        except asyncio.TimeoutError:
            raise Exception('Timed out')
        else:
            await self.cleanUpMessages()
            return message.content

    async def saveEvent(self, serverId, eventName, desc, game, mentions,
                        unixTime, channelId, author):
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

    async def confirmEvent(self, ctx):
        confirmMessage = await ctx.send(
            'This is what your event will look like. Confirm or Cancel by reacting to this message.'
        )
        self.messagesStack.append(confirmMessage)
        await confirmMessage.add_reaction('✅')
        await confirmMessage.add_reaction('❌')

        response = await self.awaitReaction(ctx, confirmMessage)

        return response == '✅'

    @commands.command()
    async def schedule(self, ctx):
        serverId = ctx.guild.id
        channelId = ctx.channel.id
        author = ctx.author.id
        try:
            eventName = await self.askForInput(ctx, ctx.author, "Event Name?")
            desc = await self.askForInput(ctx, ctx.author, "Description?")
            game = await self.askForInput(ctx, ctx.author, "What game/activity?")
            mentions = await self.askForInput(
                ctx, ctx.author, "Who do you want to notify? @ mention them here")
            time = await self.askForInput(ctx, ctx.author, "When is the event?")

            try:  #need to implement retry for time
                timeUnix = int(dateparser.parse(time).timestamp())
            except Exception as e:
                print(e)

            eventPreview = await ctx.send(embed=embedFactory(
                eventName=eventName,
                desc=desc,
                game=game,
                unixTime=timeUnix,
                mentions=mentions,
                creator=f'{author}',
                footerText='Schedule another with ^schedule'))
            self.messagesStack.append(eventPreview)

            
            confirmed = await self.confirmEvent(ctx)
            await self.cleanUpMessages()
            if confirmed:
                await self.saveEvent(serverId=serverId,
                                    eventName=eventName,
                                    desc=desc,
                                    game=game,
                                    mentions=mentions,
                                    unixTime=timeUnix,
                                    channelId=channelId,
                                    author=author)
                await ctx.send('Event scheduled')
            else:
                await ctx.send('Event cancelled.')

        except:
            await ctx.send('Scheduling timed out, try again with ^schedule')
            await self.cleanUpMessages()