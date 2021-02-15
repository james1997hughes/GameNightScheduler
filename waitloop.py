import discord
from discord.ext import tasks, commands
import sqlite3
import time
from embedFactory import embedFactory


class waitloop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('schedulerData.db')
        self.cursor = self.conn.cursor()
        self.pollAndNotify.start()

    def cog_unload(self):
        self.conn.close()

    @tasks.loop(seconds=9.0)
    async def pollAndNotify(self):
        statement = f"SELECT * FROM events WHERE time <= {time.time() + 10} AND time >= {time.time()}"
        events = self.cursor.execute(statement).fetchall()
        for event in events:
            await self.bot.wait_until_ready()
            channel = self.bot.get_channel(int(event[7]))

            eventName = event[2]
            game = event[4]
            unixTime = event[6]
            desc = event[3]
            author= event[8]
            mentions = event[5]

            eventEmbed=embedFactory(eventName=eventName,
                                            desc=desc,
                                            game=game,
                                            unixTime=unixTime,
                                            mentions=mentions,
                                            creator=f'{author}',
                                            footerText='Schedule another with ^schedule.')

            deleteStatement = f"DELETE FROM events WHERE id={event[0]}"
            self.cursor.execute(deleteStatement)
            self.conn.commit()
            print(f'Deleted event: {event[2]}')
            await channel.send(embed=eventEmbed)