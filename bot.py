# This example requires the 'members' privileged intents
import re

import discord

from prompt import ReminderPrompt


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
                if prompt.author.id == ctx.author.id:
                    await ctx.respond("You are already setting a reminder, finish that one first!", ephemeral=True)
                    return

            # Create a new prompt
            new = ReminderPrompt(ctx, reminder)
            self.prompts.append(new)
            res = await new.run()
            if not res and not new.cancelled:
                await ctx.respond("This is a lie, this bot doesn't set reminders yet, no reminder has been set")
            self.prompts.remove(new)
        
        @self.command()
        async def ping(ctx):
            await ctx.respond("Pong!")

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))


