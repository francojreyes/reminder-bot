'''
Cog for server settings commands
'''

import discord
from discord.ext import commands

from src import constants
from src.data import data


async def get_countries(ctx: discord.AutocompleteContext):
    inp = ctx.value.lower()
    return [x for x in constants.TZ_COUNTRIES if x.lower().startswith(inp)]


async def country_timezones(ctx: discord.AutocompleteContext):
    inp = ctx.value.lower()
    country = ctx.options['country']
    if country and country in constants.TZ_COUNTRIES:
        country_timezones = constants.TZ_COUNTRIES[country]
        return [tz for tz in country_timezones if inp in tz.lower()]

    return [tz for tz in constants.TZ_ALL if inp in tz.lower()]


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
        timezone = data.get_timezone(ctx.guild_id)

        target = data.get_target(ctx.guild_id)
        target = f'<#{target}>' if target else '`None`'

        role = data.get_role(ctx.guild_id)
        role = f'<@&{role}>' if role else '`None`'

        embed = {
            'color': constants.BLURPLE,
            'title': 'Reminder Bot Settings Help',
            'description': r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_',
            'fields': []
        }
        embed['fields'].append({
            'name': 'Server Timezone 🕒',
            'value': 'All times entered in this server will be assumed to be in this timezone.\n\n'
                    f'Current Timezone: `{timezone}`\n\n'
                    'Use `/settings timezone <country> <timezone>` to set the timezone.\n\n'
                    r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_'
        })
        embed['fields'].append({
            'name': 'Reminder Channel 📢',
            'value': 'If specified, all reminders will be sent in this channel. '
                    'Otherwise, reminders are sent to the channel they were set in.\n\n'
                    f'Current Reminder Channel: {target}\n\n'
                    'Use `/settings channel <#channel>` to set a channel.\n'
                    'Use `/settings channel` to unset the reminder channel.\n\n'
                    r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_'
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
    @discord.option('country', autocomplete=get_countries, required=True,
        description='Enter a country to filter timezone list')
    @discord.option('timezone', autocomplete=country_timezones, required=True,
        description='Select a timezone')
    async def timezone(self, ctx: discord.ApplicationContext, country: str, timezone: str):
        """Set the timezone for this server"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond(
                "You must have the `Manage Guild` permission to edit settings!",
                ephemeral=True
            )
            return
        
        if timezone in constants.TZ_ALL:
            data.set_timezone(ctx.guild_id, timezone)
            embed = {
                'color': constants.BLURPLE,
                'title': 'Setting changed!',
                'description': f"New Timezone: `{timezone}`"
            }
            await ctx.respond(embed=discord.Embed.from_dict(embed))
        else:
            await ctx.respond(f'No timezone `{timezone}` found! Please select one from the list', ephemeral=True)

    @settings_group.command()
    @discord.option('channel', type=discord.TextChannel, required=False,
                    description='The channel to send reminders to.'
                                'If no channel provided, unsets reminder channel.')
    async def channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        """Set the reminder channel for this server"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.respond(
                "You must have the `Manage Guild` permission to edit settings!",
                ephemeral=True
            )
            return

        if channel:
            if channel.guild != ctx.guild:
                await ctx.respond(
                    f'No channel {channel.mention} found in this server.', ephemeral=True)
                return

            data.set_target(ctx.guild_id, channel.id)
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
                    description='The role to set as manager. '
                                'If no role provided, unsets manager role.')
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
