'''
The Reminder Bot bot client
'''
import asyncio

import discord
from discord.ext import tasks

from src.cogs.help import HelpCog
from src.cogs.reminders import RemindersCog
from src.cogs.settings import SettingsCog
from src.data import data


class ReminderBot(discord.Bot):
    """Reminder bot client"""

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
        """Log when ready"""
        print(f'Logged on as {self.user}!')
        guilds = data.all_guilds()

        # Remove any guilds we no longer have access to
        for g in guilds:
            guild = self.get_guild(g['_id'])
            if not guild:
                data.remove_guild(g['_id'])
    
    async def on_application_command_error(
        self,
        ctx: discord.ApplicationContext,
        error: discord.DiscordException
    ):
        """Global error handler"""
        print(error)
        await ctx.respond(
            f"Unknown Error: {error}\n"
            "Please contact me (`@marsh#0943`) "
            "or report an issue on the [repo](https://github.com/francojreyes/reminder-bot/issues)."  
        )

    @tasks.loop(minutes=1)
    async def execute_reminders(self):
        '''Execute all reminders that are in this minute'''
        for reminder in data.current_reminders():
            # Ensure still in guild
            guild = self.get_guild(reminder.guild_id)
            if not guild:
                data.remove_guild(reminder.guild_id)
                continue

            # Find target channel
            target = data.get_target(reminder.guild_id)
            if self.get_channel(target) is None:
                target = None

            try:
                await reminder.execute(self, target)
            except discord.errors.Forbidden:
                await reminder.failure(self, target)

            if reminder.interval:
                data.add_reminder(reminder.generate_repeat())

            await asyncio.sleep(1/25)

    @execute_reminders.before_loop
    async def before_my_task(self):
        '''Wait until ready before executing reminders'''
        await self.wait_until_ready()
        data.ping()
    

