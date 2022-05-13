'''
The Reminder Bot bot client
'''
import discord

from prompt import ReminderPrompt
from reminder import Reminder

class ReminderBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompts = []
        self.reminders = []

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
                await ctx.respond("This is a lie, this bot doesn't set reminders yet, no reminder has been set", ephemeral=True)
                self.reminders.append(Reminder.from_prompt(prompt))

                ### TESTING ###
                for idx, reminder in enumerate(self.reminders):
                    channel = self.get_channel(reminder.channel)
                    await channel.send(f'**{idx + 1}**: {reminder}')
            self.prompts.remove(prompt)
        
        @self.command()
        async def ping(ctx):
            """Ping the Reminder Bot"""
            await ctx.respond("Pong!")

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message_delete(self, message):
        # If a prompt was deleted, cancel it
        for prompt in self.prompts:
            if prompt.message.id == message.id:
                prompt.cancelled = True
                prompt._view.stop()

