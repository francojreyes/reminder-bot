"""
Cog for setting and removing reminders
"""
from bisect import insort

import discord
from discord.ext import commands

from src import constants
from src.classes.prompt import ReminderPrompt
from src.classes.reminder import Reminder
from src.classes.list import ReminderList

class RemindersCog(commands.Cog):
    def __init__(self, bot):
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
        prompt = ReminderPrompt(ctx, reminder)
        self.bot.prompts.append(prompt)
        res = await prompt.run()

        # Set a reminder with completed prompt
        if not res and not prompt.cancelled:
            insort(self.bot.reminders, Reminder.from_prompt(prompt))
        self.bot.prompts.remove(prompt)
    
    @commands.Cog.listener('on_message_delete')
    async def prompt_deletion(self, message):
        """Listen for prompt deletion"""
        for prompt in self.bot.prompts:
            if prompt.message.id == message.id:
                prompt.cancelled = True
                prompt._view.stop()
    
    @commands.slash_command()
    async def list(self, ctx):
        """List all reminders"""
        for list_ in self.bot.lists:
            if list_.ctx.author == ctx.author:
                await list_.close()
        
        # Open a new list
        list_ = ReminderList(ctx, self.bot.reminders)
        self.bot.lists.append(list_)
        await list_.respond(ctx.interaction)
        await list_.wait()

        # After list is done, idk
        self.bot.lists.remove(list_)
    
    @commands.Cog.listener('on_message_delete')
    async def prompt_deletion(self, message):
        """Listen for list deletion"""
        for list_ in self.bot.lists:
            if list_.message and list_.message.id == message.id:
                list_.stop()
    
    @commands.slash_command()
    @discord.option("id", type=int, description="ID of reminder to remove",
        min_value=1, required=True)
    async def remove(self, ctx: discord.ApplicationContext, id):
        """Remove a reminder (use /list to get the reminder ID)"""
        if len(self.bot.reminders) < id:
            await ctx.respond('No reminder exists with that ID', required=True)
            return
        reminder = self.bot.reminders[id - 1]

        if ctx.author.id != reminder.author_id:
            await ctx.respond('You cannot remove a reminder that is not yours', required=True)
            return
        
        self.bot.reminders.remove(reminder)

        embed = discord.Embed(
            colour=constants.RED,
            title='Reminder removed!',
            description=f'**{id}:** {reminder}'
        )
        await ctx.respond(embed=embed)