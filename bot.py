# This example requires the 'members' privileged intents

import os
import re

import discord
import dotenv
from discord.ext import commands

from prompt import ReminderPrompt

class Reminder():
    def __init__(self) -> None:
        pass


intents = discord.Intents.default()
intents.messages = True

client = commands.Bot(command_prefix='r!', intents=intents)
client.prompts = []
client.reminders = []


@client.command()
async def set(ctx, *args):
    # See if user currently has a prompt open
    for prompt in client.prompts:
        if prompt.author.id == ctx.author.id:
            return

    # Create a new prompt
    new = ReminderPrompt(ctx, ' '.join(args))
    await new.start()
    client.prompts.append(new)


@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))


@client.event
async def on_message(message: discord.Message):
    """Attempts to take in input for prompts requring text input"""
    await client.process_commands(message)

    for prompt in client.prompts:
        if prompt.author.id == message.author.id and prompt.is_awaiting_input():
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


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Attempts to respond to reaction to prompts"""
    for prompt in client.prompts:
        if prompt.author.id == payload.user_id and prompt.is_awaiting_react():
            target = prompt
            break
    else:
        return

    if payload.emoji.name in prompt.message.reactions:
        await target.update(emoji=payload.emoji.name)
    else:
        await target.message.clear_reaction(payload.emoji)


dotenv.load_dotenv()
client.run(os.getenv('DISCORD_TOKEN'))
