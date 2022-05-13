"""
Reminder list UI using pycord's pages module
"""

import discord
from discord.ext import pages

import constants

class ReminderList(pages.Paginator):
    def __init__(self, ctx, reminders):
        self.ctx = ctx

        page_list = []
        for i in range(0, len(reminders), 5):
            page_list.append(ReminderListPage(reminders[i:i+5]))
        
        if not reminders:
            page_list = [ReminderListPage(None)]
        
        buttons=[
            pages.PaginatorButton('prev', label='<', style=discord.ButtonStyle.blurple),
            pages.PaginatorButton('page_indicator', style=discord.ButtonStyle.gray, disabled=True),
            pages.PaginatorButton('next', label='>', style=discord.ButtonStyle.blurple),
        ]
        
        super().__init__(
            pages=page_list,
            use_default_buttons=False,
            custom_buttons=buttons,
            author_check=True,
            disable_on_timeout=True,
            timeout=60
        )



class ReminderListPage(pages.Page):
    """Page of a reminder list"""
    def __init__(self, reminders):
        if reminders:
            content = '\n\n'.join(f'**{idx+1}:** {reminder}' for idx, reminder in enumerate(reminders))
        else:
            content = 'Nothing to show here...'

        embed = discord.Embed(
            colour=constants.BLURPLE,
            title='Reminder List',
            description=content
        )
        embed.set_footer(
            text='Note: IDs may be inaccurate if reminders have been added/removed since this list was opened')
    
        super().__init__(embeds=[embed])

class ReminderListTimeoutPage(pages.Page):
    """Page to display on timeout"""
    pass