'''Main file to run bot from'''
import os

import discord
import dotenv

from src.data import data
from src.bot import ReminderBot

ping = data.db.command('ping')
print('Connected to MongoDB', ping)

intents = discord.Intents.default()
intents.messages = True
client = ReminderBot(intents=intents)

dotenv.load_dotenv()
client.run(os.getenv('DISCORD_TOKEN'))
