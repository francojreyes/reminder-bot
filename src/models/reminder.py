"""
Reminder object
"""
from functools import total_ordering
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from src import parsing
from src.models.prompt import ReminderPrompt


@total_ordering
class Reminder:
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
        else:  # time_str[0] == 'in'
            time = parsing.add_interval(time, datetime.now(tz=ZoneInfo(prompt.timezone)))

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
            time=int(time.timestamp()),
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

    def generate_repeat(self, tz: str = "UTC"):
        """Create reminder that is the repeat of self"""
        if not self.interval:
            raise ValueError('This reminder has no repeat interval set')

        time = parsing.add_interval(self.interval, datetime.fromtimestamp(self.time, tz=ZoneInfo(tz)))

        return Reminder(
            text=self.text,
            author_id=self.author_id,
            guild_id=self.guild_id,
            channel_id=self.channel_id,
            time=int(time.timestamp()),
            interval=self.interval
        )

    async def execute(self, channel: discord.TextChannel, author: discord.Member):
        """Execute this reminder in given channel with author's allowed mentions"""
        # Calculate the allowed mentions of the author
        author_perms = channel.permissions_for(author)
        allowed_mentions = discord.AllowedMentions(
            users=True,
            everyone=author_perms.mention_everyone,
            roles=author_perms.mention_everyone
        )

        await channel.send(f'<@{self.author_id}>\n> {self.text}',
                           allowed_mentions=allowed_mentions)
    
    async def failure(self, channel: discord.TextChannel, author: discord.Member):
        """DM user in case of failed reminder"""
        try:
            await author.send(
                f'The following reminder failed to send to {channel.mention} in `{channel.guild.name}`'
                ' as the bot does not have permission to send messages.\n'
                f'> {self.text}'
            )
        except discord.Forbidden as e:
            print(f'The following reminder failed to send, and failed to notify author: {repr(self)}\n'
                  f'The cause was: {e}')

    def __str__(self):
        """Discord syntax string representation for listing"""
        string = f'<t:{self.time}:R>'
        if self.interval:
            string += f' (repeats every {self.interval})'
        string += f'\n_"{self.text}"_ for <@!{self.author_id}>'
        return string

    def __repr__(self):
        return (f'Reminder(text={self.text}, author_id={self.author_id}, guild_id={self.guild_id}, '
                f'channel_id={self.channel_id}, time={self.time}, interval={self.interval})')

    def __eq__(self, other):
        return self.time == other.time

    def __lt__(self, other):
        return self.time < other.time
