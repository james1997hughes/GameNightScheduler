import discord
from discord.ext import tasks, commands
import sqlite3
import time


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

            title = event[2]
            game = event[4]
            friendlyTime = event[6]
            description = event[3]
            creator = event[8]
            mentions = event[5]

            myEmbed = discord.Embed(
                title=title,
                description=description)
            myEmbed.add_field(name="Time",
                            value=friendlyTime,
                            inline=False)
            myEmbed.add_field(name="Mentions",
                            value=mentions,
                            inline=False)
            myEmbed.set_footer(text=f"Schedule another with ^schedule")
            myEmbed.set_author(name=game, icon_url="https://store-images.s-microsoft.com/image/apps.45782.9007199266731945.debbc4f1-cde0-491b-8c6f-b6b015eecab6.4716cccc-5f37-4bb5-9db1-0c1dbc99003f?mode=scale&q=90&h=200&w=200&background=%23000000")

            deleteStatement = f"DELETE FROM events WHERE id={event[0]}"
            self.cursor.execute(deleteStatement)
            self.conn.commit()
            print(f'Deleted event: {event[2]}')
            await channel.send(embed=myEmbed)

