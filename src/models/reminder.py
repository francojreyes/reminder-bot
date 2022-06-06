'''
Reminder object
'''
from functools import total_ordering
from datetime import datetime

import discord
from src import parsing
from src.models.prompt import ReminderPrompt


@total_ordering
class Reminder():
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
        time_str = prompt.time_

        # Get the time of reminder
        time = time_str[1].replace(', repeating', '')
        if time_str[0] == 'on':
            time = parsing.str_to_datetime(time, prompt.timezone)
            time = int(time.timestamp())
        else:  # time_str[0] == 'in'
            now = int(datetime.now().timestamp())
            time = parsing.relative_to_timestamp(time, now)

        # Get the repeat interval
        if 'never' in time_str:
            interval = None
        else:
            interval = time_str[-1]

        return Reminder(
            text=prompt.text,
            author_id=prompt.ctx.author.id,
            guild_id=prompt.ctx.guild_id,
            channel_id=prompt.ctx.channel_id,
            time=time,
            interval=interval
        )

    @classmethod
    def from_dict(cls, dic: dict):
        """Instantiate a reminder from a dict"""
        return Reminder(
            text=dic['text'],
            author_id=dic['author_id'],
            guild_id=dic['guild_id'],
            channel_id=dic['channel_id'],
            time=dic['time'],
            interval=dic['interval']
        )

    def generate_repeat(self):
        """Create reminder that is the repeat of self"""
        if not self.interval:
            raise ValueError('This reminder has no repeat interval set')

        time = parsing.relative_to_timestamp(self.interval, self.time)

        return Reminder(
            text=self.text,
            author_id=self.author_id,
            guild_id=self.guild_id,
            channel_id=self.channel_id,
            time=time,
            interval=self.interval
        )

    async def execute(self, bot, target=None):
        """Execute this reminder with given bot"""
        target_id = target if target else self.channel_id
        channel = bot.get_channel(target_id)
        if channel is None:
            # Check that channel still exists
            return
        await channel.send(f'<@{self.author_id}>\n> {self.text}',
                           allowed_mentions=discord.AllowedMentions(users=True))
    
    async def failure(self, bot, target=None):
        """DM user in case of failed reminder"""
        target_id = target if target else self.channel_id
        channel = bot.get_channel(target_id)
        guild = bot.get_guild(self.guild_id)
        user = bot.get_user(self.author_id)
        message = f'> {self.text}\n\n' \
                   'Hi! The above reminder failed to send to' \
                    f'{channel.mention} in {guild.name} due to missing access.\n' \
                   'Please ensure Reminder Bot has permissions to send messages and mention people\n' \
                   'If Reminder Bot does have correct permissions, please contact me @marsh#0943'
        await user.send(message)

    def __str__(self):
        """Discord syntax string representation for listing"""
        string = f'<t:{self.time}:R>'
        if self.interval:
            string += f' (repeats every {self.interval})'
        string += f'\n_"{self.text}"_ from <@!{self.author_id}>'
        return string 

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time < other.time
