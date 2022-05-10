'''Main file to run bot from'''
import os

import discord
import dotenv

from bot import ReminderBot

intents = discord.Intents.default()
intents.messages = True
client = ReminderBot(command_prefix='r!', intents=intents)

dotenv.load_dotenv()
client.run(os.getenv('DISCORD_TOKEN'))
