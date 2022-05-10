# This example requires the 'members' privileged intents
import re

import discord
from discord.ext import commands

from reminders import ReminderPrompt


class ReminderBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompts = []
        self.reminders = []

        @self.command()
        async def set(ctx, *args):
            # See if user currently has a prompt open
            for prompt in self.prompts:
                if prompt.author.id == ctx.author.id:
                    return

            # Create a new prompt
            new = ReminderPrompt(ctx, ' '.join(args))
            await new.start()
            self.prompts.append(new)


    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message: discord.Message):
        """Attempts to take in input for prompts requring text input"""
        await self.process_commands(message)

        for prompt in self.prompts:
            if prompt.author.id == message.author.id and not prompt.options:
                target = prompt
                break
        else:
            return

        inp = message.content.strip()
        if ('_amount' in target.state and inp.isnumeric()) or \
        (target.state == 'date' and re.fullmatch(r'[0-9]{2}-[0-9]{2}-[0-9]{4}', inp)) or \
        (target.state == 'time' and re.fullmatch(r'[0-9]{2}:[0-9]{2}', inp)):
            await message.delete()
            await target.update(inp=inp)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Attempts to respond to reaction to prompts"""
        for prompt in self.prompts:
            if prompt.author.id == payload.user_id:
                target = prompt
                break
        else:
            return
        
        if payload.emoji.name in prompt.options:
            await target.update(emoji=payload.emoji.name)
        else:
            await target.message.clear_reaction(payload.emoji)

