'''
ReminderPrompt class
'''

import discord

from states import STATES

class ReminderPrompt():
    def __init__(self, ctx, reminder):
        self.author = ctx.author
        self.send = ctx.send

        self.reminder = reminder
        self.time = '...'

        self.prev_state = None
        self.state = 'init'
        self.embed = {
            'title': 'Setting reminder...',
            'description': f'__"{self.reminder}"__\n{self.time}',
            'fields': [STATES[self.state]['field']]
        }

        self.message = None
    

    async def start(self):
        self.message = await self.send(embed=discord.Embed.from_dict(self.embed))
        for react in STATES[self.state]['options']:
            await self.message.add_reaction(react)


    async def update(self, emoji=None, inp=None):
        # Invalid call
        if emoji is None and inp is None:
            return

        # Add to the string
        if isinstance(STATES[self.state]['append'], str):
            # Only one next state
            self.time = self.time[:-3] + STATES[self.state]['append'].format(inp)
        elif isinstance(STATES[self.state]['append'], dict):
            # Choose based on emoji
            self.time = self.time[:-3] + STATES[self.state]['append'][emoji]

        # Get next state
        self.prev_state = self.state
        if isinstance(STATES[self.state]['next_state'], str):
            # Only one next state
            self.state = STATES[self.state]['next_state']
        elif isinstance(STATES[self.state]['next_state'], dict):
            # Choose based on emoji
            self.state = STATES[self.state]['next_state'][emoji]
        else:
            # End
            return
        
        await self.message.clear_reactions()
        
        self.embed['description'] = f'"__{self.reminder}__"\n{self.time}'
        self.embed['fields'] = [STATES[self.state]['field']]
        await self.message.edit(embed=discord.Embed.from_dict(self.embed))
        
        for react in STATES[self.state]['options']:
            await self.message.add_reaction(react)