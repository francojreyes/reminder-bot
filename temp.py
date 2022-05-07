'''
Send a reminder to take bc
'''
import random
import traceback

from discord_webhook import DiscordEmbed, DiscordWebhook

URL = 'https://discord.com/api/webhooks/972188922488688670/bmcVHbI7YQ3ROLzUYbhSBVoFLxjJmlYSzTDCOCqDo6J01UM2miVTqtNYtPXwR-qNmSyf'
MESSAGES = [
    "Don't forget to take your birth control!",
    "Kill the child",
    "Abort the fetus",
    "Consume the pill",
]

try:
    DiscordWebhook(
        url=URL,
        content='<@585429992586870794> ' + random.choice(MESSAGES)
    ).execute()
except:
    traceback.print_exc()