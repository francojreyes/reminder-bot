"""
Cog that implements the modular help command
"""
import discord
from discord.ext import commands


def cog_commands(cog: discord.Cog):
    """Returns all commands of a cog (not groups)"""
    return [x for x in cog.walk_commands() if isinstance(x, discord.SlashCommand)]


def help_autocomplete(ctx: discord.AutocompleteContext):
    """Autocomplete with all cogs and commands"""

    # Gather all cogs and commands starting with input
    inp = ctx.value.lower()
    result = []
    for cog in ctx.bot.cogs:
        # Any cog
        if cog.lower().startswith(inp):
            result.append(cog)

        # Any command that starts with input or input without slash
        for command in cog_commands(ctx.bot.cogs[cog]):
            command_name = command.qualified_name.lower()
            if command_name.startswith(inp) or \
                    (inp.startswith('/') and command_name.startswith(inp[1:])):
                result.append(f'/{command.qualified_name}')

    return result


class HelpCog(commands.Cog, name='Other'):
    """
    Sends this help message
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command()
    @discord.option('topic', str, required=False, autocomplete=help_autocomplete,
                    description='Specific module or command')
    async def help(self, ctx: discord.ApplicationContext, topic: discord.Option(str),):
        """Help command"""
        if topic and topic.startswith('/'):
            _input = topic[1:]

        # If no parameter given, send overview
        if not topic:
            await ctx.respond(embed=OverviewEmbed(self.bot))
            return

        # iterate through cogs
        for cog in self.bot.cogs:
            # check if cog is the matching one
            if cog.lower() == topic.lower():
                await ctx.respond(embed=CogEmbed(self.bot.cogs[cog]))
                return

            # or look it in its commands to see if it's there
            for command in cog_commands(self.bot.cogs[cog]):
                if command.qualified_name.lower() == topic.lower():
                    await ctx.respond(embed=CommandEmbed(command))
                    return

        # if no matches found
        await ctx.respond(embed=discord.Embed(
            title="Not Found",
            description=f"No module or command found called `{topic}`",
            color=discord.Color.brand_red()))


class OverviewEmbed(discord.Embed):
    """Overview when help command has no option"""

    def __init__(self, bot: discord.Bot):
        # build Embed
        super().__init__(
            title=f'Help: {bot.user.name}',
            color=discord.Color.blurple(),
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
            name="About",
            value="This bot is developed by `@marshdapro`.\n"
                  "Feel free to report any issues or suggest new features [here](https://github.com/francojreyes/reminder-bot/issues).\n"
                  "If you like Reminder Bot, don't forget to [vote](https://top.gg/bot/973088919862263808/)!"
        )


class CogEmbed(discord.Embed):
    """Embed describing the commands in a cog"""

    def __init__(self, cog: discord.Cog):
        # build Embed
        super().__init__(
            title=f'Help: {cog.qualified_name} Module',
            description=f'{cog.description}.\n'
                        'Use `/help <command>` to gain more information about that command.',
            color=discord.Color.blurple())

        # getting commands from cog
        for command in cog_commands(cog):
            self.add_field(name=f"`/{command.qualified_name}`",
                           value=command.description, inline=False)


class CommandEmbed(discord.Embed):
    """Embed describing the options of a command"""

    def __init__(self, command: discord.SlashCommand):
        # Generate usage of the form `/command <opt1> <opt2>`
        usage = f"/{command.qualified_name} {' '.join(f'<{opt.name}>' for opt in command.options)}"

        # Build embed
        super().__init__(
            title=f'Help: /{command.qualified_name}',
            description=f"{command.description}.\n Usage: `{usage.strip(' ')}`",
            color=discord.Color.blurple(),
        )

        # Getting option from command
        for option in command.options:
            self.add_field(
                name=f'`<{option.name}>`' +
                     (' (Optional)' if not option.required else ''),
                value=option.description,
                inline=False
            )
