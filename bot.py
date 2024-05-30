import json
import logging
import os
import platform
import random
import sys

import aiosqlite
import discord

from datetime import datetime
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv

if not os.path.isfile("{}/config.json".format(os.path.realpath(os.path.dirname(__file__)))):
    sys.exit("\"config.json\" not found! Please add it and try again.")
else:
    with open("{}/config.json".format(os.path.realpath(os.path.dirname(__file__)))) as file:
        config = json.load(file)

intents = discord.Intents.all()

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)
    
logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())

file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

def getRank(rank:str) -> str:
    rank = rank.lower()

    match rank:
        case "cadet":
            return "[REC]"
        case "private":
            return "[PTE]"
        case "private first class":
            return "[PFC]"
        case "specialist":
            return "[SPC]"
        case "corporal":
            return "[CPL]"
        case "sergeant":
            return "[SGT]"
        case "staff sergeant":
            return "[SSG]"
        case "sergeant first class":
            return "[SFC]"
        case "master sergeant":
            return "[MSG]"
        case "first sergeant":
            return "[1SG]"
        case "sergeant major":
            return "[SGM]"
        case "command sergeant major":
            return "[CSM]"
        case "warrant officer 1":
            return "[WO1]"
        case "chief warrant officer 2":
            return "[CW2]"
        case "chief warrant officer 3":
            return "[CW3]"
        case "chief warrant officer 4":
            return "[CW4]"
        case "chief warrant officer 5":
            return "[CW5]"
        case "second lieutenant":
            return "[2LT]"
        case "first lieutenant":
            return "[1LT]"
        case "captain":
            return "[CPT]"
        case "major":
            return "[MAJ]"
        case "lieutenant colonel":
            return "[LTC]"
        case "colonel":
            return "[COL]"
        case "brigadier general":
            return "[Brig. Gen]"
        case "major general":
            return "[Maj. Gen]"
        case "lieutenant general":
            return "[Lt. Gen]"
        case "general":
            return "[Gen]"

    return ""

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(config["prefix"]),
            intents=intents,
            help_command=None,
        )

        self.logger = logger
        self.config = config
        self.database = None

    async def init_db(self) -> None:
        async with aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
        ) as db:
            with open(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
            ) as file:
                await db.executescript(file.read())

            await db.commit()
        
    async def load_cogs(self) -> None:
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension \"{extension}\"")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )
    
    @tasks.loop(minutes=.25)
    async def status_task(self) -> None:
        statuses = ["with the NCR."]
        thisGuild = self.get_guild(1213830412334534666)

        start = datetime.now().timestamp()
        print("Checking roles and nicknames...")
        if thisGuild is not None:
            members = thisGuild.members

            for m in members:
                memberRoles = m.roles
                highestRole = memberRoles[-1]
                rank = getRank(highestRole.name)
                nicknameExempt = False

                if m.guild_permissions.administrator:
                    nicknameExempt = True
                
                if m._user.bot:
                    nicknameExempt = True

                for role in memberRoles:
                    if role.name.lower() == "ss nickname exempt":
                        nicknameExempt = True

                if highestRole.name in ["My Daughter(s)"]:
                    nicknameExempt = True

                if not nicknameExempt:
                    # print("{} {} [{}]".format(rank, m._user.display_name, highestRole))

                    oldNickname = m.display_name
                    newNickname = "{} {}".format(rank, m._user.display_name)

                    if oldNickname != newNickname:
                        await m.edit(nick=newNickname)
        end = datetime.now().timestamp()
        timeDiff = start-end

        print("Check done. Time taken: {}s".format(timeDiff))

        await self.change_presence(activity=discord.Game(random.choice(statuses)))

    @status_task.before_loop
    async def before_status_task(self) -> None:
        await self.wait_until_ready()

    async def setup_hook(self) -> None:
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        
        # await self.init_db()
        await self.load_cogs()
        
        self.status_task.start()
        #self.database = DatabaseManager(
        #    connection=await aiosqlite.connect(
        #        f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
        #   )
        #)

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])

        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            hours = hours % 24
            embed = discord.Embed(
                description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                description="You are not the owner of the bot!", color=0xE02B2B
            )
            await context.send(embed=embed)
            if context.guild:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
                )
            else:
                self.logger.warning(
                    f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
                )
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="You are missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to execute this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="I am missing the permission(s) `"
                + ", ".join(error.missing_permissions)
                + "` to fully perform this command!",
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error!",
                # We need to capitalize because the command arguments have no capital letter in the code and they are the first word in the error message.
                description=str(error).capitalize(),
                color=0xE02B2B,
            )
            await context.send(embed=embed)
        else:
            raise error
        
load_dotenv()

bot = DiscordBot()
bot.run(os.getenv("TOKEN"))