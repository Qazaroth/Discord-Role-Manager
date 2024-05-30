import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot : commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="sync",
        description="Synchronizes the slash commands"
    )
    @app_commands.describe(scope="The scope of the sync. Can be global or guild")
    @commands.is_owner()
    async def sync(self, context: Context, scope: str) -> None:
        if scope == "global":
            await context.bot.tree.sync()