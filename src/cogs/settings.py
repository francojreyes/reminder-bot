'''
Cog for server settings commands
'''

import discord
from discord.ext import commands

from src import constants
from src.data import data


class SettingsCog(commands.Cog, name='Settings'):
    """
    Commands for changing the bot's settings
    """

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    settings_group = discord.commands.SlashCommandGroup(
        "settings", "Change the settings for this server")

    @settings_group.command()
    async def view(self, ctx: discord.ApplicationContext):
        """See information on the settings for this server"""
        offset = data.get_offset(ctx.guild_id)
        offset = constants.ISO_TZD(offset)

        target = data.get_target(ctx.guild_id)
        target = f'<#{target}>' if target else '`None`'

        role = data.get_role(ctx.guild_id)
        role = f'<@&{role}>' if role else '`None`'

        embed = {
            'color': constants.BLURPLE,
            'title': 'Reminder Bot Settings Help',
            'description': '\_\_\_\_\_\_\_\_\_\_\_\_\_\_',
            'fields': []
        }
        embed['fields'].append({
            'name': 'GMT Offset 🕒',
            'value': 'All times entered in this server will be assumed to have this GMT offset. '
                    'Find the GMT offset for your timezone [here](https://www.google.com/search?q=what+is+my+time+zone).\n\n'
                    f'Current GMT Offset: `GMT{offset}`\n\n'
                    'Use `/settings offset <offset>` to set the offset.\n\n'
                    '\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_'
        })
        embed['fields'].append({
            'name': 'Reminder Channel 📢',
            'value': 'If specified, all reminders will be sent in this channel. '
                    'Otherwise, reminders are sent to the channel they were set in.\n\n'
                    f'Current Reminder Channel: {target}\n\n'
                    'Use `/settings channel <#channel>` to set a channel.\n'
                    'Use `/settings channel` to unset the reminder channel.\n\n'
                    '\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_'
        })
        embed['fields'].append({
            'name': 'Manager Role 🛠️',
            'value': 'If specified, only users with this role will be able to remove reminders. '
                    'Otherwise, any user with the `Manage Messages` permissions can.\n\n'
                    f'Current Manager Role: {role}\n\n'
                    'Use `/settings role <@role>` to set a role.\n'
                    'Use `/settings role` to unset the manager role.\n\n'
        })

        await ctx.respond(embed=discord.Embed.from_dict(embed))

    @settings_group.command()
    @discord.option('offset', type=int, min_value=-12, max_value=12, required=True,
                    description='The number of hours to offset by')
    async def offset(self, ctx: discord.ApplicationContext, offset: int):
        """Set the GMT offset for this server"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond(
                "You must have the `Manage Guild` permission to edit settings!",
                ephemeral=True
            )
            return

        data.set_offset(ctx.guild_id, offset)
        embed = {
            'color': constants.BLURPLE,
            'title': 'Setting changed!',
            'description': f"New GMT Offset: `GMT{constants.ISO_TZD(offset)}`"
        }
        await ctx.respond(embed=discord.Embed.from_dict(embed))

    @settings_group.command()
    @discord.option('channel', type=str, required=False,
                    description='The channel to send reminders to. If no channel provided, unsets reminder channel.')
    async def channel(self, ctx: discord.ApplicationContext, channel):
        """Set the reminder channel for this server"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond(
                "You must have the `Manage Guild` permission to edit settings!",
                ephemeral=True
            )
            return

        if channel:
            try:
                channel_id = int(channel.strip(' <!#>'))
            except:
                await ctx.respond('Not a channel, please enter a channel using #channel-name', ephemeral=True)
                return

            # Channel must be in this guild
            channel = self.bot.get_channel(channel_id)
            if channel is None or channel.guild != ctx.guild:
                await ctx.respond(f'No channel {channel.mention} found in this server.', ephemeral=True)
                return

            data.set_target(ctx.guild_id, channel_id)
            description = f'New Reminder Channel: {channel.mention}'
        else:
            data.set_target(ctx.guild_id, None)
            description = 'Reminder channel unset.'

        embed = {
            'color': constants.BLURPLE,
            'title': 'Setting changed!',
            'description': description
        }
        await ctx.respond(embed=discord.Embed.from_dict(embed))

    @settings_group.command()
    @discord.option('role', type=discord.Role, required=False,
                    description='The role to set as manager. If no role provided, unsets manager role.')
    async def role(self, ctx: discord.ApplicationContext, role):
        """Set the manager role for this server"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond(
                "You must have the `Manage Guild` permission to edit settings!",
                ephemeral=True
            )
            return

        if role:
            if role.guild != ctx.guild:
                await ctx.respond(f'No role {role.mention} found in this server.', ephemeral=True)
                return

            data.set_role(ctx.guild_id, role.id)
            description = f'New Manager Role: {role.mention}'
        else:
            data.set_role(ctx.guild_id, None)
            description = 'Manager role unset.'

        embed = {
            'color': constants.BLURPLE,
            'title': 'Setting changed!',
            'description': description
        }
        await ctx.respond(embed=discord.Embed.from_dict(embed))
