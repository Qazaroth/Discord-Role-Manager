import platform
import random

import aiohttp
import discord

from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context

class General(commands.Cog, name="general"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.context_menu_user = app_commands.ContextMenu(
            name="Grab ID", callback=self.grab_id
        )
        self.bot.tree.add_command(self.context_menu_user)

    async def grab_id(
            self, interaction: discord.Interaction, user: discord.User
    ) -> None:
        embed = discord.Embed(
            description=f"The ID of {user.mention} is `{user.id}`.",
            color=0xBEBEFE
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)