'''
Reminder object
'''
from functools import total_ordering
from datetime import datetime

import constants
from prompt import ReminderPrompt

@total_ordering
class Reminder():
    """
    Represents a reminder

    Attributes
    text: str
        The reminder text
    author_id: int
        User ID of the reminder author
    author_name: str
        name#id of the reminder author
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
            author: str = '',
            channel_id: int = 0,
            time: int = 0,
            interval: str = ''
        ):
        self.text = text
        self.author_id = author_id
        self.author = author
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
            author=str(prompt.ctx.author),
            channel_id=prompt.ctx.channel_id,
            time=time,
            interval=interval
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
            author=self.author,
            channel_id=self.channel_id,
            time=repeat_time,
            interval=self.interval
        )
    
    def __str__(self):
        """String representation for listing"""
        s = f'_"{self.text}"_ from `@{self.author}`\n\t'
        s += datetime.strftime(datetime.fromtimestamp(self.time), "%d/%m/%Y %H:%M")
        if self.interval:
            s += f', every {self.interval}'
        return s
    
    def __eq__(self, other):
        return self.time == other.time
    
    def __lt__(self, other):
        return self.time < other.time