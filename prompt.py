'''
Reminder prompt UI that uses the Discord Interaction API
to take user input on a reminder.
'''
import datetime
import re

import discord


class ReminderPrompt():
    def __init__(self, ctx: discord.ApplicationContext, reminder: str):
        '''Opens a new ReminderPrompt'''
        self.author = ctx.author
        self.ctx = ctx
        self.reminder = reminder
        self._time = []

        self.prev_state = None
        self._view: PromptView = PromptView(self)
        self.message: discord.InteractionMessage = None
        self.interaction: discord.Interaction = None

        self.cancelled = False

    def embed(self):
        return discord.Embed.from_dict({
            'title': 'Setting reminder...',
            'description': f'_"{self.reminder}"_\n{self.time()}...',
            'color': 0x5865f2
        })

    def time(self):
        return ' '.join(self._time)
    
    def view(self, no_back=False):
        self._view.add_item(BackButton(self, disabled=no_back))
        self._view.add_item(CancelButton(self))
        return self._view

    async def run(self):
        # Send on/in select
        self._view.clear_items()
        self._view.add_item(InitialSelect(self))
        res = await self.ctx.respond(embed=self.embed(), view=self.view(no_back=True))
        self.message = await res.original_message()
        return await self._view.wait()
    
    async def restart(self):
        # For returning to initial state via back
        self._view.clear_items()
        self._view.add_item(InitialSelect(self))
        self.prev_state = None
        await self.interaction.response.edit_message(embed=self.embed(), view=self.view(no_back=True))

    async def on(self):
        # Add the word 'on' to message, send date and time form
        self._view.clear_items()
        self.prev_state = self.restart
        await self.message.edit(embed=self.embed(), view=self.view())
        await self.interaction.response.send_modal(DateTimeModal(self))

    async def in_amount(self):
        # Add the word 'in' to message, send amount form
        self._view.clear_items()
        self.prev_state = self.restart
        await self.message.edit(embed=self.embed(), view=self.view())
        await self.interaction.response.send_modal(AmountModal(self, 'in'))

    async def in_select(self):
        # Update embed with given amount, send period select
        self._view.clear_items()
        self._view.add_item(PeriodSelect(self, 'in'))
        self.prev_state = self.in_amount
        await self.interaction.response.edit_message(embed=self.embed(), view=self.view())

    async def repeat(self):
        # Two buttons, yes or no
        self._view.clear_items()
        self._view.add_item(NoRepeatButton(self))
        self._view.add_item(YesRepeatButton(self))

        # Determine how this state was reached
        if 'in' in self._time:
            self.prev_state = self.in_select
        elif 'on' in self._time:
            self.prev_state = self.on

        await self.interaction.response.edit_message(embed=self.embed(), view=self.view())

    async def repeat_amount(self):
        # Add the word 'every' to message, send amount form
        self._view.clear_items()
        self.prev_state = self.repeat
        await self.message.edit(embed=self.embed(), view=self.view())
        await self.interaction.response.send_modal(AmountModal(self, 'repeat'))

    async def repeat_select(self):
        # Update embed with given amount, send period select
        self._view.clear_items()
        self._view.add_item(PeriodSelect(self, 'repeat'))
        self.prev_state = self.repeat_amount
        await self.interaction.response.edit_message(embed=self.embed(), view=self.view())

    async def back(self):
        self._time = self._time[:-1]
        await self.prev_state()

    async def confirm(self):
        self._view.clear_items()
        self._view.add_item(ConfirmButton(self))
        
        # Embed finishes with full stop
        embed = discord.Embed.from_dict({
            'title': 'Setting reminder...',
            'description': f'_"{self.reminder}"_\n{self.time()}.',
            'color': 0x5865f2
        })
        
        if 'never' in self._time:
            self.prev_state = self.repeat
        else:
            self.prev_state = self.repeat_select
        
        await self.interaction.response.edit_message(embed=embed, view=self.view())

    async def finish(self):
        self._view.clear_items()
        embed = discord.Embed.from_dict({
            'title': 'Reminder set!',
            'description': f'_"{self.reminder}"_\n{self.time()}.',
            'color': 0x57f287
        })
        await self.interaction.response.edit_message(embed=embed, view=self._view)
        self._view.stop()

    async def cancel(self):
        self._view.clear_items()
        embed = discord.Embed.from_dict({
            'title': 'Reminder cancelled!',
            'description': f'_"{self.reminder}"_\n{self.time()}...',
            'color': 0xed4245
        })
        await self.interaction.response.edit_message(embed=embed, view=self._view)
        self.cancelled = True
        self._view.stop()

    async def timeout(self):
        self._view.clear_items()
        embed = discord.Embed.from_dict({
            'title': 'Reminder timed out!',
            'description': f'_"{self.reminder}"_\n{self.time()}...',
            'color': 0xed4245
        })
        await self.message.edit(embed=embed, view=self._view)
        self._view.stop()


class PromptView(discord.ui.View):
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(timeout=120)
        self.prompt = prompt

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user == self.prompt.author:
            return True
        else:
            await interaction.response.send_message(
                "This isn't your reminder! Go away!", ephemeral=True)

    async def on_timeout(self):
        await self.prompt.timeout()


class InitialSelect(discord.ui.Select):
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
        self.prompt.interaction = interaction
        self.prompt._time.append(selection)
        if selection == 'on':
            await self.prompt.on()
        elif selection == 'in':
            await self.prompt.in_amount()


class DateTimeModal(discord.ui.Modal):
    def __init__(self, prompt: ReminderPrompt):
        super().__init__('Reminder Bot')
        self.prompt = prompt
        self.add_item(discord.ui.InputText(
            label="Enter a date",
            placeholder="DD-MM-YYYY"
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
        if not re.fullmatch(r'[0-9]{2}-[0-9]{2}-[0-9]{4}', date):
            await self.prompt.ctx.respond('Invalid date format! Please use the format DD-MM-YYYY', ephemeral=True)
            await self.prompt.back()
            return

        # Enforce valid input format
        if not re.fullmatch(r'[0-9]{2}:[0-9]{2}', time):
            await self.prompt.ctx.respond('Invalid time format! Please use the format HH:MM', ephemeral=True)
            await self.prompt.back()
            return

        # Enforce valid datetime
        try:
            dt = datetime.datetime.strptime(date + time, "%d-%m-%Y%H:%M")
        except ValueError:
            await self.prompt.ctx.respond('Date or time does not exist!', ephemeral=True)
            await self.prompt.back()
            return

        self.prompt._time.append(f'{date} at {time}, repeating')
        await self.prompt.repeat()


class AmountModal(discord.ui.Modal):
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
        if not inp.isnumeric():
            await self.prompt.ctx.respond('Invalid format! Please enter a number', ephemeral=True)
            await self.prompt.back()
            return

        self.prompt._time.append(inp)
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
        self.prompt.interaction = interaction

        if self.state == 'in':
            self.prompt._time.append(f'{self.values[0]}, repeating')
            await self.prompt.repeat()
        elif self.state == 'repeat':
            self.prompt._time.append(self.values[0])
            await self.prompt.confirm()


class CancelButton(discord.ui.Button):
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(emoji="❌", label="Cancel")
        self.prompt = prompt

    async def callback(self, interaction: discord.Interaction):
        self.prompt.interaction = interaction
        await self.prompt.cancel()


class BackButton(discord.ui.Button):
    def __init__(self, prompt: ReminderPrompt, disabled: bool = False):
        super().__init__(emoji="↩️", label="Back", disabled=disabled)
        self.prompt = prompt
    
    async def callback(self, interaction: discord.Interaction):
        self.prompt.interaction = interaction
        await self.prompt.back()


class YesRepeatButton(discord.ui.Button):
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(label="Repeat every...", emoji="🔁")
        self.prompt = prompt
    
    async def callback(self, interaction):
        self.prompt.interaction = interaction
        self.prompt._time.append('every')
        await self.prompt.repeat_amount()


class NoRepeatButton(discord.ui.Button):
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(label="Do not repeat", emoji="1️⃣")
        self.prompt = prompt
    
    async def callback(self, interaction: discord.Interaction):
        self.prompt.interaction = interaction
        self.prompt._time.append('never')
        await self.prompt.confirm()


class ConfirmButton(discord.ui.Button):
    def __init__(self, prompt: ReminderPrompt):
        super().__init__(style=discord.ButtonStyle.success, label="Confirm", emoji="✅")
        self.prompt = prompt
    
    async def callback(self, interaction: discord.Interaction):
        self.prompt.interaction = interaction
        await self.prompt.finish()
