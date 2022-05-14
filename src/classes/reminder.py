'''
Reminder object
'''
from functools import total_ordering
from datetime import datetime

import discord
from src import constants
from src.classes.prompt import ReminderPrompt

@total_ordering
class Reminder(object):
    """
    Represents a reminder

    Attributes
    text: str
        The reminder text
    author_id: int
        User ID of the reminder author
    guild_id: int
        Guild ID of target guild
    channel_id: int
        Channel ID of the target channel
    time: int
        POSIX timestamp of the time of the reminder
    interval: str
        String describing the recurrence interval
    """
    def __init__(
            self, 
            text: str = '',
            author_id: int = 0,
            guild_id: int = 0,
            channel_id: int = 0,
            time: int = 0,
            interval: str = ''
        ):
        self.text = text
        self.author_id = author_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.time = time
        self.interval = interval

    @classmethod
    def from_prompt(cls, prompt: ReminderPrompt):
        """Create reminder from Prompt object"""
        # Decipher the prompt time string
        time_str = prompt._time

        # Get the time of reminder
        if time_str[0] == 'on':
            format_str = '%d/%m/%Y at %H:%M, repeating'
            time = int(datetime.strptime(time_str[1], format_str).timestamp())
        else: # time_str[0] == 'in'
            period = time_str[2].split(',')[0]
            if not period.endswith('s'):
                period += 's'
            dt = datetime.now() + int(time_str[1]) * constants.DELTA[period]
            time = int(dt.timestamp())

        # Get the repeat interval
        if 'never' in time_str:
            interval = None
        else:
            repeat_idx = time_str.index('every') + 1
            interval = ' '.join(time_str[repeat_idx:repeat_idx+2])
        
        return Reminder(
            text=prompt.text,
            author_id=prompt.ctx.author.id,
            guild_id=prompt.ctx.guild_id,
            channel_id=prompt.ctx.channel_id,
            time=time,
            interval=interval
        )
    
    @classmethod
    def from_dict(cls, dict):
        return Reminder(
            text=dict['text'],
            author_id=dict['author_id'],
            guild_id=dict['guild_id'],
            channel_id=dict['channel_id'],
            time=dict['time'],
            interval=dict['interval']
        )
    
    def generate_repeat(self):
        """Create reminder that is the repeat of self"""
        if not self.interval:
            raise ValueError('This reminder has no repeat interval set')

        amount, period = self.interval.split(' ')
        if not period.endswith('s'):
            period += 's'
        repeat_time = datetime.fromtimestamp(self.time) + int(amount) * constants.DELTA[period]
        return Reminder(
            text=self.text,
            author_id=self.author_id,
            guild_id=self.guild_id,
            channel_id=self.channel_id,
            time=int(repeat_time.timestamp()),
            interval=self.interval
        )
    
    async def execute(self, bot):
        """Execute this reminder with given bot"""
        channel = bot.get_channel(self.channel_id)
        if channel is None:
            # Check that channel still exists
            return
        await channel.send(f'<@{self.author_id}> {self.text}', allowed_mentions=discord.AllowedMentions(users=True))
    
    def __str__(self):
        """Discord syntax string representation for listing"""
        s = f'<t:{self.time}:R>\n_"{self.text}"_ from <@{self.author_id}>'
        if self.interval:
            s += f' (repeats every {self.interval})'
        return s
    
    def __eq__(self, other):
        return self.time == other.time
    
    def __lt__(self, other):
        return self.time < other.time