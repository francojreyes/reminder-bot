'''
Cog that implements the modular help command
'''
import discord
from discord.ext import commands
from src import constants


def cog_commands(cog: discord.Cog):
    """Returns all commands of a cog (not groups)"""
    return [x for x in cog.walk_commands() if not isinstance(x, discord.SlashCommandGroup)]


class HelpCog(commands.Cog, name='Other'):
    """
    Sends this help message
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command()
    @discord.option('input', str, required=False, description='Specific module or command')
    async def help(self, ctx: discord.ApplicationContext, inp: str):
        """Help command"""
        if inp and inp.startswith('/'):
            inp = inp[1:]

        # If no parameter given, send overview
        if not inp:
            await ctx.respond(embed=OverviewEmbed(self.bot))
            return

        # iterate through cogs
        for cog in self.bot.cogs:
            # check if cog is the matching one
            if cog.lower() == inp.lower():
                await ctx.respond(embed=CogEmbed(self.bot.cogs[cog]))
                return

            # or look it in its commands to see if its there
            for command in cog_commands(self.bot.cogs[cog]):
                if command.qualified_name.lower() == inp.lower():
                    await ctx.respond(embed=CommandEmbed(command))
                    return

        # if no matches found
        await ctx.respond(embed=discord.Embed(
            title="Not Found",
            description=f"No module or command found called `{inp}`",
            color=constants.RED))


class OverviewEmbed(discord.Embed):
    '''Overview when help command has no option'''

    def __init__(self, bot: discord.Bot):
        super().__init__(
            title='Help: Reminder Bot',
            color=constants.BLURPLE,
            description='Use `/help <module>` to gain more information about that module.'
        )

        # iterating trough cogs, gathering descriptions
        cogs_desc = ''
        for cog in bot.cogs:
            cogs_desc += f'`{cog}` {bot.cogs[cog].__doc__}\n'

        # adding 'list' of cogs to embed
        self.add_field(name='Modules', value=cogs_desc, inline=False)

        # setting information about author
        self.add_field(
            name="About", value="This bot is developed by @marsh#0943. Add me to report any bugs!")


class CogEmbed(discord.Embed):
    """Embed describing the commands in a cog"""

    def __init__(self, cog: discord.Cog):
        super().__init__(
            title=f'Help: {cog.qualified_name} Module',
            description=f'{cog.description}.\n'
                        'Use `/help <command>` to gain more information about that command.',
            color=constants.BLURPLE)

        # getting commands from cog
        for command in cog_commands(cog):
            self.add_field(name=f"`/{command.qualified_name}`",
                           value=command.description, inline=False)


class CommandEmbed(discord.Embed):
    """Embed describing the options of a command"""

    def __init__(self, command: discord.ApplicationCommand):
        usage = f"/{command.qualified_name} {' '.join(f'<{opt.name}>' for opt in command.options)}"
        super().__init__(
            title=f'Help: /{command.qualified_name}',
            description=f"{command.description}.\n Usage: `{usage.strip(' ')}`",
            color=constants.BLURPLE,
        )

        for option in command.options:
            self.add_field(
                name=f'`<{option.name}>`' +
                (' (Optional)' if not option.required else ''),
                value=option.description,
                inline=False
            )
