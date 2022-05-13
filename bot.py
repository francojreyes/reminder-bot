'''
The Reminder Bot bot client
'''
from bisect import insort
from datetime import datetime

import discord
from discord.ext import tasks

from prompt import ReminderPrompt
from reminder import Reminder
from paginator import ReminderList

class ReminderBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompts: list[ReminderPrompt] = []
        self.reminders: list[Reminder] = []
        self.lists: list[ReminderList] = []

        @self.command()
        @discord.option("reminder", description="Enter your reminder", required=True)
        async def set(ctx, reminder):
            """Set a new reminder"""
            # See if user currently has a prompt open
            for prompt in self.prompts:
                if prompt.ctx.author == ctx.author:
                    await ctx.respond("You are already setting a reminder, finish that one first!", ephemeral=True)
                    return

            # Open a new prompt
            prompt = ReminderPrompt(ctx, reminder)
            self.prompts.append(prompt)
            res = await prompt.run()

            # Set a reminder with completed prompt
            if not res and not prompt.cancelled:
                insort(self.reminders, Reminder.from_prompt(prompt))
            self.prompts.remove(prompt)
        
        @self.command()
        async def list(ctx):
            """List all reminders"""
            for list_ in self.lists:
                if list_.ctx.author == ctx.author:
                    await ctx.respond("You already have a list open", ephemeral=True)
                    return
            
            # Open a new list
            list_ = ReminderList(ctx, self.reminders)
            self.lists.append(list_)
            await list_.respond(ctx.interaction)
            await list_.wait()

            # After list is done, idk
            self.lists.remove(list_)

        @self.command()
        async def ping(ctx):
            """Ping the Reminder Bot"""
            await ctx.respond("Pong!")

        self.execute_reminders.start()

    async def on_ready(self):
        # Signal ready
        print('Logged on as {0}!'.format(self.user))

    async def on_message_delete(self, message):
        """Listen for deletion of UIs"""
        for prompt in self.prompts:
            if prompt.message.id == message.id:
                prompt.cancelled = True
                prompt._view.stop()

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
