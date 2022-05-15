'''
Cog for server settings commands
'''

import discord
from discord.ext import commands

from src import constants
from src.data import data

class SettingsCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
    
    @commands.slash_command()
    async def settingss(self, ctx: discord.ApplicationContext):
        """See the settings for this server"""
        offset = data.get_offset(ctx.guild_id)
        offset = f"{'+' if offset >= 0 else ''}{offset}"

        target = data.get_offset(ctx.guild_id)
        target = f'<#{target}>' if target else 'None'

        embed = {'title': 'Reminder Bot Settings'}
        embed['fields'] = [
            {
                'name': '🕒 GMT Offset',
                'value': 'All times entered in this server will be assumed to have this GMT offset. Find the GMT offset for your timezone [here](https://www.google.com/search?q=what+is+my+time+zone)\n\n'
                        f'Current GMT Offset: {offset}\n\n'
                        'Use `/settings offset <offset>` to set the offset.\n'
            },
            {
                'name': '📢 Reminder Channel',
                'value': 'If specified, all reminders will be sent in this channel. Otherwise, reminders are sent to the channel they were set in.\n\n'
                        f'Current Reminder Channel: {target}\n\n'
                        'Use `/settings channel <#channel>` to set a channel.\n'
                        'Use `/settings channel` to unset the reminder channel.\n' 
            },
        ]
        embed['color'] = constants.BLURPLE

        await ctx.respond(embed=discord.Embed.from_dict(embed))
    
    settings_group = discord.commands.SlashCommandGroup("settings", "Change the settings for this server")

    @settings_group.command()
    @discord.option('offset', type=int, min_value=-12, max_value=12, required=True,
        description='The number of hours to offset by')
    async def offset(self, ctx: discord.ApplicationContext, offset: int):
        """Set the GMT offset for this server"""
        data.set_offset(ctx.guild_id, offset)
        embed = {
            'color': constants.BLURPLE,
            'title': 'Setting changed!',
            'description': f"New GMT Offset: {'+' if offset >= 0 else ''}{offset}"
        }
        await ctx.respond(embed=discord.Embed.from_dict(embed))
    
    @settings_group.command()
    @discord.option('channel', type=str, required=False,
        description='The channel to send reminders to')
    async def channel(self, ctx: discord.ApplicationContext, channel):
        """Set the reminder channel for this server"""
        if channel:
            # Channel must be in this guild 
            channel_id = channel.strip(' <#>')
            channel = self.bot.get_channel(channel_id)
            if channel is None or channel.guild != ctx.guild:
                ctx.respond(f'No channel <#{channel_id}> found in this server.', ephemeral=True)


            data.set_target(ctx.guild_id, channel_id)
            description = f'New Reminder Channel: <#{channel_id}>'
        else:
            data.set_target(ctx.guild_id, None)
            description = 'Reminder channel unset.'
        
        embed = {
            'color': constants.BLURPLE,
            'title': 'Setting changed!',
            'description': description
        }
        await ctx.respond(embed=discord.Embed.from_dict(embed))    
