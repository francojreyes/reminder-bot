"""
Cog for setting and removing reminders
"""
import discord
from discord.ext import commands

from src import constants
from src.classes.prompt import ReminderPrompt
from src.classes.reminder import Reminder
from src.classes.list import ReminderList
from src.data import data

class RemindersCog(commands.Cog, name='Reminders'):
    """
    Commands for setting and managing reminders
    """
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @commands.slash_command()
    @discord.option("reminder", type=str, description="Enter your reminder", required=True)
    async def set(self, ctx, reminder):
        """Set a new reminder"""
        # See if user currently has a prompt open
        for prompt in self.bot.prompts:
            if prompt.ctx.author == ctx.author:
                await ctx.respond("You are already setting a reminder, finish that one first!", ephemeral=True)
                return

        # Open a new prompt
        offset = data.get_offset(ctx.guild_id)
        prompt = ReminderPrompt(ctx, reminder, offset)
        self.bot.prompts.append(prompt)
        res = await prompt.run()

        # Set a reminder with completed prompt
        if not res and not prompt.cancelled:
            data.add_reminder(Reminder.from_prompt(prompt))
        self.bot.prompts.remove(prompt)
    
    @commands.Cog.listener('on_message_delete')
    async def prompt_deletion(self, message: discord.Message):
        """Listen for prompt deletion"""
        for prompt in self.bot.prompts:
            if prompt.message.id == message.id:
                prompt.cancelled = True
                prompt._view.stop()
    
    @commands.slash_command()
    async def list(self, ctx: discord.ApplicationContext):
        """List all reminders"""
        for list_ in self.bot.lists:
            if list_.ctx.author == ctx.author:
                await list_.close()
        
        # Open a new list
        list_ = ReminderList(ctx, data.guild_reminders(ctx.guild_id))
        self.bot.lists.append(list_)
        await list_.respond(ctx.interaction)
        await list_.wait()

        # After list is done
        self.bot.lists.remove(list_)
    
    @commands.Cog.listener('on_message_delete')
    async def list_deletion(self, message: discord.Message):
        """Listen for list deletion"""
        for list_ in self.bot.lists:
            if list_.message and list_.message.id == message.id:
                list_.stop()
    
    @commands.slash_command()
    @discord.option("id", type=int, description="ID of reminder to remove",
        min_value=1, required=True)
    async def remove(self, ctx: discord.ApplicationContext, id: int):
        """Remove a reminder (use /list to get the reminder ID)"""
        manager = data.get_role(ctx.guild_id)

        if manager and ctx.guild.get_role(manager):
            role = ctx.guild.get_role(manager)
            if not role in ctx.author.roles:
                await ctx.respond(f'You must have the {role.mention} role to remove reminders!',
                        epehemeral=True)
                return
        else:
            if not ctx.author.guild_permissions.manage_messages:
                await ctx.respond('You must have the `Manage Messages` permission to remove reminders!',
                    epehemeral=True)
                return

        reminders = data.guild_reminders(ctx.guild_id)
        if len(reminders) < id:
            await ctx.respond('No reminder exists with that ID', ephemeral=True)
            return
        reminder = reminders[id - 1]

        if ctx.author.id != reminder.author_id:
            await ctx.respond('You cannot remove a reminder that is not yours', ephemeral=True)
            return
        
        data.remove_reminder(reminder)

        embed = discord.Embed(
            colour=constants.RED,
            title='Reminder removed!',
            description=f'**{id}:** {reminder}'
        )
        await ctx.respond(embed=embed)