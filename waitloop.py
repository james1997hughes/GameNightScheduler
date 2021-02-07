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
            await channel.send(f'Hello! Event "{event[2]}" about to start.')
            deleteStatement = f"DELETE FROM events WHERE id={event[0]}"
            self.cursor.execute(deleteStatement)
            self.conn.commit()
            print(f'Deleted event: {event[2]}')
