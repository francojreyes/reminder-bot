'''Main file to run bot from'''
import os

import discord
import dotenv

from bot import ReminderBot

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
client = ReminderBot(intents=intents)

dotenv.load_dotenv()
client.run(os.getenv('DISCORD_TOKEN'))
