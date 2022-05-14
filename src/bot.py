'''
The Reminder Bot bot client
'''
from bisect import insort
from datetime import datetime

import discord
from discord.ext import tasks

from src.cogs.reminders import RemindersCog

class ReminderBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompts = []
        self.reminders = []
        self.lists = []

        self.add_cog(RemindersCog(self))

        @self.command()
        async def ping(ctx):
            """Ping the Reminder Bot"""
            await ctx.respond("Pong!")

        self.execute_reminders.start()

    async def on_ready(self):
        # Signal ready
        print('Logged on as {0}!'.format(self.user))        

    @tasks.loop(minutes=1)
    async def execute_reminders(self):
        '''Execute all reminders that are in this minute'''
        for reminder in self.reminders:
            # Loop until a reminder is no longer this minute
            if reminder.time // 60 != int(datetime.now().timestamp()) // 60:
                break
            self.reminders.remove(reminder)

            # Send reminder
            channel = self.get_channel(reminder.channel_id)
            await channel.send(f'<@{reminder.author_id}> {reminder.text}')

            # If reminder repeats, add repeat
            if reminder.interval:
                insort(self.reminders, reminder.generate_repeat())

    @execute_reminders.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()
