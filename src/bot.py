"""
The Reminder Bot bot client
"""
import asyncio

import discord
from discord.ext import tasks

from src.data import data
from src.models.list import ReminderList
from src.models.prompt import ReminderPrompt


async def valid_channel_type(ctx: discord.ApplicationContext):
    """Ensure that command was not called in private channel"""
    if ctx.channel.type != discord.ChannelType.text:
        raise discord.DiscordException("Reminders are not supported for private channels")
    return True


class ReminderBot(discord.Bot):
    """Reminder bot client"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_mentions = discord.AllowedMentions.none()

        self.prompts: list[ReminderPrompt] = []
        self.promptsLock = asyncio.Lock()
        self.lists: list[ReminderList] = []
        self.listsLock = asyncio.Lock()

        from src.cogs.reminders import RemindersCog
        self.add_cog(RemindersCog(self))

        from src.cogs.settings import SettingsCog
        self.add_cog(SettingsCog(self))

        from src.cogs.help import HelpCog
        self.add_cog(HelpCog(self))

        self.add_check(valid_channel_type)

        self.execute_reminders.start()

    async def on_ready(self):
        """Log when ready"""
        print(f'Logged on as {self.user}!')
    
    async def on_application_command_error(
        self,
        ctx: discord.ApplicationContext,
        error: discord.DiscordException
    ):
        """Global error handler"""
        print(f"Error occurred with /{ctx.command.qualified_name}", ctx.selected_options)
        print(f"    {error}")
        await ctx.respond(
            f"**Error:** {error}\n"
            "If this seems like unintended behaviour, please contact me (`@marshdapro`) "
            "or report an issue on the [repo](https://github.com/francojreyes/reminder-bot/issues).",
            ephemeral=True
        )

    @tasks.loop(minutes=1)
    async def execute_reminders(self):
        """Execute all reminders that are in this minute"""
        for reminder in data.current_reminders():
            # Ensure still in guild
            guild = self.get_guild(reminder.guild_id)
            if not guild:
                print("Guild not found, continuing")
                data.remove_guild(reminder.guild_id)
                continue

            # Find target channel and check it exists
            channel_id = data.get_target(reminder.guild_id) or reminder.channel_id
            channel = self.get_channel(channel_id)
            if channel is None:
                print("Channel not found, continuing")
                continue
                
            # Check if author still in guild
            try:
                author = guild.get_member(reminder.author_id) or await guild.fetch_member(reminder.author_id)
            except discord.errors.NotFound:
                author = None
            if author is None:
                print("Author not found, continuing")
                continue

            try:
                print("Executing...")
                await reminder.execute(channel, author)
                print("Success")
            except discord.errors.Forbidden:
                print("Failed")
                await reminder.failure(channel, author)
            except discord.errors.DiscordServerError:
                print("Discord server error - waiting till next minute")
                break

            if reminder.interval:
                data.add_reminder(reminder.generate_repeat())

            await asyncio.sleep(1/25)

    @execute_reminders.before_loop
    async def before_my_task(self):
        """Wait until ready before executing reminders"""
        await self.wait_until_ready()
        data.ping()
