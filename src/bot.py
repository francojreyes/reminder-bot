'''
The Reminder Bot bot client
'''
import discord
from discord.ext import tasks

from src.cogs.reminders import RemindersCog
from src.cogs.settings import SettingsCog
from src.cogs.help import HelpCog
from src.data import data


class ReminderBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_mentions = discord.AllowedMentions.none()
        self.prompts = []
        self.lists = []

        self.add_cog(RemindersCog(self))
        self.add_cog(SettingsCog(self))
        self.add_cog(HelpCog(self))

        self.execute_reminders.start()

    async def on_ready(self):
        # Signal ready
        print('Logged on as {0}!'.format(self.user))        

    @tasks.loop(minutes=1)
    async def execute_reminders(self):
        '''Execute all reminders that are in this minute'''
        for reminder in data.current_reminders():
            # Find target channel
            target = data.get_target(reminder.guild_id)
            if self.get_channel(target) is None:
                target = None

            await reminder.execute(self, target)

            if reminder.interval:
                data.add_reminder(reminder.generate_repeat())

    @execute_reminders.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()
        data.ping()
