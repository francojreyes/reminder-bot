"""
Reminder list UI using pycord's pages module
"""

import discord
from discord.ext import pages

from src import constants

BUTTONS = [
    pages.PaginatorButton('first', label='<<', style=discord.ButtonStyle.blurple, row=1),
    pages.PaginatorButton('prev', label='<', style=discord.ButtonStyle.blurple, row=1),
    pages.PaginatorButton('page_indicator', style=discord.ButtonStyle.gray, row=1, disabled=True),
    pages.PaginatorButton('next', label='>', style=discord.ButtonStyle.blurple, row=1),
    pages.PaginatorButton('last', label='>>', style=discord.ButtonStyle.blurple, row=1),
]


class ReminderList(pages.Paginator):
    def __init__(self, ctx: discord.ApplicationContext, reminders):
        self.ctx = ctx
        self.message = None
        self.reminders = list(enumerate(reminders))
        self.my_reminders = [
            r for r in self.reminders if r[1].author_id == ctx.author.id]

        page_groups = [
            ReminderListPageGroup('Show all reminders', self.reminders),
            ReminderListPageGroup('Show my reminders only', self.my_reminders)
        ]

        view = discord.ui.View(ReminderListMenu(page_groups))
        view.children[0].paginator = self

        super().__init__(
            pages=page_groups[0].pages,
            custom_buttons=BUTTONS,
            custom_view=view,
            use_default_buttons=False,
            disable_on_timeout=True,
            timeout=60
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user == self.user:
            return True
        else:
            await interaction.response.send_message("This isn't your reminder! Go away!", ephemeral=True)

    async def on_timeout(self):
        """Timeout message on list timeout"""
        embed = discord.Embed(
            color=constants.RED,
            title='Reminder List Timed Out!'
        )
        await self.message.edit(embed=embed, view=None)

    async def close(self):
        """Stop and delete list"""
        self.stop()
        await self.message.delete()


class ReminderListMenu(discord.ui.Select):
    def __init__(self, page_groups):
        self.page_groups = page_groups
        self.paginator = None
        opts = [
            discord.SelectOption(
                label=page_group.label,
                value=page_group.label
            )
            for page_group in self.page_groups
        ]
        super().__init__(placeholder='Showing all reminders...', options=opts)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        if selection == 'Show all reminders':
            self.placeholder = 'Showing all reminders...'
            await self.paginator.update(
                pages=self.page_groups[0].pages,
                use_default_buttons=False,
                custom_buttons=BUTTONS,
                custom_view=self.paginator.custom_view
            )
        else:  # 'Show my reminders'
            name = self.paginator.user.display_name
            self.placeholder = f"Showing {name}'s reminders..."
            await self.paginator.update(
                pages=self.page_groups[1].pages,
                use_default_buttons=False,
                custom_buttons=BUTTONS,
                custom_view=self.paginator.custom_view
            )


class ReminderListPageGroup(pages.PageGroup):
    def __init__(self, label, reminders):
        if reminders:
            page_list = []
            for i in range(0, len(reminders), 5):
                page_list.append(ReminderListPage(reminders[i:i+5]))
        else:
            page_list = [ReminderListPage(None)]

        super().__init__(
            pages=page_list,
            label=label,
            description=None,
            use_default_buttons=False,
            custom_buttons=BUTTONS,
        )


class ReminderListPage(pages.Page):
    """Page of a reminder list"""

    def __init__(self, reminders):
        if reminders:
            content = '\n'.join(
                f'**{idx+1}:** {reminder}\n' for idx, reminder in reminders)
        else:
            content = 'Nothing to show here...'

        embed = discord.Embed(
            colour=constants.BLURPLE,
            title='Reminder List',
            description=content
        )
        embed.set_footer(
            text='Note: IDs may be inaccurate if reminders have been added/removed since this list was opened.')

        super().__init__(embeds=[embed])
