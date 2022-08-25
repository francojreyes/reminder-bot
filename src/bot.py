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

        self.add_check(self.valid_channel_type)

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
        print(f"Error occured with /{ctx.command.qualified_name}", ctx.selected_options)
        print(f"    {error}")
        await ctx.respond(
            f"**Error:** {error}\n"
            "If this seems like unintended behaviour, please contact me (`@marsh#0943`) "
            "or report an issue on the [repo](https://github.com/francojreyes/reminder-bot/issues).",
            ephemeral=True
        )

    async def valid_channel_type(bot, ctx: discord.ApplicationContext):
        '''Ensure that command was not called in private channel'''
        if ctx.channel.type != discord.ChannelType.text:
            raise discord.DiscordException("Reminders are not supported for private channels")
        return True

    @tasks.loop(minutes=1)
    async def execute_reminders(self):
        '''Execute all reminders that are in this minute'''
        for reminder in data.current_reminders():
            # Ensure still in guild
            guild = self.get_guild(reminder.guild_id)
            if not guild:
                data.remove_guild(reminder.guild_id)
                continue

            # Find target channel and check it exists
            target = data.get_target(reminder.guild_id)
            channel_id = target if target else reminder.channel_id
            channel = self.get_channel(channel_id)
            if channel is None:
                continue
                
            # Check if author still in guild
            author = self.get_guild(reminder.guild_id).get_member(reminder.author_id)
            if author is None:
                continue

            try:
                await reminder.execute(channel, author)
            except discord.errors.Forbidden:
                await reminder.failure(channel, author)

            if reminder.interval:
                data.add_reminder(reminder.generate_repeat())

            await asyncio.sleep(1/25)

    @execute_reminders.before_loop
    async def before_my_task(self):
        '''Wait until ready before executing reminders'''
        await self.wait_until_ready()
        data.ping()
