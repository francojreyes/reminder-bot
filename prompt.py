'''
Reminder prompt UI that uses the Discord Interaction API
to take user input on a reminder.
'''
from datetime import datetime
import re

import discord

import constants

class ReminderPrompt():
    def __init__(self, ctx: discord.ApplicationContext, text: str):
        '''Opens a new ReminderPrompt'''
        self.ctx = ctx
        self.text = text
        self._time = []

        self.prev_state = None
        self._view: PromptView = PromptView(self)
        self.message: discord.InteractionMessage = None
        self.interaction: discord.Interaction = None

        self.cancelled = False

    def embed(self):
        """Generates an embed for an in progress reminder prompt"""
        return discord.Embed.from_dict({
            'title': 'Setting reminder...',
            'description': f'_"{self.text}"_\n{self.time()}...',
            'color': constants.BLURPLE
        })

    def time(self):
        """Generates a string to represent the time of the reminder"""
        return ' '.join(self._time)
    
    def view(self, no_back=False):
        """
        Returns the current View with a back button and cancel button added

        no_back (bool)
            Whether or not the back button should be disabled
        """
        self._view.add_item(BackButton(self, disabled=no_back))
        self._view.add_item(CancelButton(self))
        return self._view

    async def run(self):
        """
        Sets up initial state and runs prompt
        Returns True after timeout, or False after natural end
        """
        self._view.clear_items()
        self._view.add_item(InitialSelect(self))
        res = await self.ctx.respond(embed=self.embed(), view=self.view(no_back=True))
        self.message = await res.original_message()
        return await self._view.wait()
    
    async def restart(self):
        """
        Sets up initial state
        Used when the initial states is accessed via back
        """
        self._view.clear_items()
        self._view.add_item(InitialSelect(self))
        self.prev_state = None
        await self.interaction.response.edit_message(embed=self.embed(), view=self.view(no_back=True))

    async def on(self):
        """Send a modal for the date and time to set a reminder 'on'"""
        self._view.clear_items()
        self.prev_state = self.restart
        await self.message.edit(embed=self.embed(), view=self.view())
        await self.interaction.response.send_modal(DateTimeModal(self))

    async def in_amount(self):
        """Send a modal for the amount of time to set a reminder 'in'"""
        self._view.clear_items()
        self.prev_state = self.restart
        await self.message.edit(embed=self.embed(), view=self.view())
        await self.interaction.response.send_modal(AmountModal(self, 'in'))

    async def in_select(self):
        """Send a select item for the time period corresponding to inputted amount"""
        self._view.clear_items()
        self._view.add_item(PeriodSelect(self, 'in'))
        self.prev_state = self.in_amount
        await self.interaction.response.edit_message(embed=self.embed(), view=self.view())

    async def repeat(self):
        """Choose between a non-recurring or recurring reminder"""
        self._view.clear_items()
        self._view.add_item(NoRepeatButton(self))
        self._view.add_item(YesRepeatButton(self))

        # State was reached either from 'in' or 'on' path
        if 'in' in self._time:
            self.prev_state = self.in_select
        elif 'on' in self._time:
            self.prev_state = self.on

        await self.interaction.response.edit_message(embed=self.embed(), view=self.view())

    async def repeat_amount(self):
        """Send a modal for the amount of the recurrence period"""
        self._view.clear_items()
        self.prev_state = self.repeat
        await self.message.edit(embed=self.embed(), view=self.view())
        await self.interaction.response.send_modal(AmountModal(self, 'repeat'))

    async def repeat_select(self):
        """Send a select item for the time period for the inputted amount"""
        self._view.clear_items()
        self._view.add_item(PeriodSelect(self, 'repeat'))
        self.prev_state = self.repeat_amount
        await self.interaction.response.edit_message(embed=self.embed(), view=self.view())

    async def back(self):
        """Removed the last most item from the string and return to previous state"""
        self._time = self._time[:-1]
        await self.prev_state()

    async def confirm(self):
        """Allow user to confirm or go back and edit"""
        self._view.clear_items()
        self._view.add_item(ConfirmButton(self))
        
        # Embed finishes with full stop
        embed = discord.Embed.from_dict({
            'title': 'Setting reminder...',
            'description': f'_"{self.text}"_\n{self.time()}.',
            'color': constants.BLURPLE
        })
        
        # State was reached from either non-recurring or recurring path
        if 'never' in self._time:
            self.prev_state = self.repeat
        else:
            self.prev_state = self.repeat_select
        
        await self.interaction.response.edit_message(embed=embed, view=self.view())

    async def finish(self):
        """End prompt and set reminder"""
        self._view.clear_items()

        # Embed ends with full stop, green highlight
        embed = discord.Embed.from_dict({
            'title': 'Reminder set!',
            'description': f'_"{self.text}"_\n{self.time()}.',
            'color': constants.GREEN
        })
        await self.interaction.response.edit_message(embed=embed, view=self._view)
        self._view.stop()

    async def cancel(self):
        """Prompt ended via user input"""
        self._view.clear_items()

        # Embed has red highlight
        embed = discord.Embed.from_dict({
            'title': 'Reminder cancelled!',
            'description': f'_"{self.text}"_\n{self.time()}...',
            'color': constants.RED
        })

        await self.interaction.response.edit_message(embed=embed, view=self._view)
        self.cancelled = True
        self._view.stop()

    async def timeout(self):
        """Prompt ended via timeout"""
        self._view.clear_items()

        # Embed has red highlight
        embed = discord.Embed.from_dict({
            'title': 'Reminder timed out!',
            'description': f'_"{self.text}"_\n{self.time()}...',
            'color': constants.RED
        })

        await self.message.edit(embed=embed, view=self._view)
        self._view.stop()


class PromptView(discord.ui.View):
    """
    Subclass for discord View model
    2 minute timeout
    Requires all interactions to be from author
    """
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(timeout=120)
        self.prompt = prompt

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user == self.prompt.ctx.author:
            self.prompt.interaction = interaction
            return True
        else:
            await interaction.response.send_message(
                "This isn't your reminder! Go away!", ephemeral=True)

    async def on_timeout(self):
        await self.prompt.timeout()


class InitialSelect(discord.ui.Select):
    """Select with the two reminder types as options"""
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(placeholder='Choose a reminder type')
        self.prompt = prompt
        self.add_option(
            label='on...',
            value='on',
            emoji="📅",
            description="a certain date, at a certain time"
        )
        self.add_option(
            label="in...",
            value='in',
            emoji="⌛",
            description="an amount of time from now"
        )

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        self.prompt._time.append(selection)

        # Choose path
        if selection == 'on':
            await self.prompt.on()
        elif selection == 'in':
            await self.prompt.in_amount()


class DateTimeModal(discord.ui.Modal):
    """Modal to take in date and time input"""
    def __init__(self, prompt: ReminderPrompt):
        super().__init__('Reminder Bot')
        self.prompt = prompt
        self.add_item(discord.ui.InputText(
            label="Enter a date",
            placeholder="DD/MM/YYYY"
        ))
        self.add_item(discord.ui.InputText(
            label="Enter a time (24 hour AEST)",
            placeholder="HH:MM"
        ))

    async def callback(self, interaction: discord.Interaction):
        self.prompt.interaction = interaction
        date = self.children[0].value.strip()
        time = self.children[1].value.strip()

        # Enforce valid input format
        if not re.fullmatch(r'[0-9]{2}/[0-9]{2}/[0-9]{4}', date):
            await self.prompt.ctx.respond('Invalid date format! Please use the format DD/MM/YYYY', ephemeral=True)
            await self.prompt.back()
            return

        # Enforce valid input format
        if not re.fullmatch(r'[0-9]{2}:[0-9]{2}', time):
            await self.prompt.ctx.respond('Invalid time format! Please use the format HH:MM', ephemeral=True)
            await self.prompt.back()
            return

        # Enforce valid datetime
        try:
            datetime.strptime(date + time, "%d/%m/%Y%H:%M")
        except ValueError:
            await self.prompt.ctx.respond('Date or time does not exist!', ephemeral=True)
            await self.prompt.back()
            return

        self.prompt._time.append(f'{date} at {time}, repeating')
        await self.prompt.repeat()


class AmountModal(discord.ui.Modal):
    """Modal to take in an amount"""
    def __init__(self, prompt: ReminderPrompt, state: str):
        super().__init__('Reminder Bot')
        self.prompt = prompt
        self.state = state
        self.add_item(discord.ui.InputText(
            label="Enter an amount",
            placeholder="123"
        ))

    async def callback(self, interaction: discord.Interaction):
        self.prompt.interaction = interaction
        inp = self.children[0].value.strip()

        # Enforce numeric
        if not inp.isnumeric():
            await self.prompt.ctx.respond('Invalid format! Please enter a number', ephemeral=True)
            await self.prompt.back()
            return

        self.prompt._time.append(inp)

        # Choose path based on what function sent this Modal
        if self.state == 'repeat':
            await self.prompt.repeat_select()
        elif self.state == 'in':
            await self.prompt.in_select()


class PeriodSelect(discord.ui.Select):
    def __init__(self, prompt: ReminderPrompt, state: str):
        super().__init__(placeholder='Choose a time period')
        self.prompt = prompt
        self.state = state
        self.add_option(label='hours', value='hours')
        self.add_option(label='days', value='days')
        self.add_option(label='weeks', value='weeks')
        self.add_option(label='months', value='months')

    async def callback(self, interaction: discord.Interaction):
        # Choose path based on what function sent this Select
        if self.state == 'in':
            self.prompt._time.append(f'{self.values[0]}, repeating')
            await self.prompt.repeat()
        elif self.state == 'repeat':
            self.prompt._time.append(self.values[0])
            await self.prompt.confirm()


class CancelButton(discord.ui.Button):
    """Button to cancel prompt"""
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(emoji="❌", label="Cancel")
        self.prompt = prompt

    async def callback(self, interaction: discord.Interaction):
        self.prompt.interaction = interaction
        await self.prompt.cancel()


class BackButton(discord.ui.Button):
    """Button to return to previous state"""
    def __init__(self, prompt: ReminderPrompt, disabled: bool = False):
        super().__init__(emoji="↩️", label="Back", disabled=disabled)
        self.prompt = prompt
    
    async def callback(self, interaction: discord.Interaction):
        await self.prompt.back()


class YesRepeatButton(discord.ui.Button):
    """Button to set recurring reminder"""
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(label="Repeat every...", emoji="🔁")
        self.prompt = prompt
    
    async def callback(self, interaction):
        self.prompt._time.append('every')
        await self.prompt.repeat_amount()


class NoRepeatButton(discord.ui.Button):
    """Button to set non-recurring reminder"""
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(label="Do not repeat", emoji="1️⃣")
        self.prompt = prompt
    
    async def callback(self, interaction: discord.Interaction):
        self.prompt._time.append('never')
        await self.prompt.confirm()


class ConfirmButton(discord.ui.Button):
    """Button to confirm setting reminder"""
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(style=discord.ButtonStyle.success, label="Confirm", emoji="✅")
        self.prompt = prompt
    
    async def callback(self, interaction: discord.Interaction):
        await self.prompt.finish()
