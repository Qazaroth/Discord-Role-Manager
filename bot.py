import os
import sys
import json

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from dotenv import load_dotenv

if not os.path.isfile("{}/config.json".format(os.path.realpath(os.path.dirname(__file__)))):
    sys.exit("\"config.json\" not found! Please add it and try again.")
else:
    with open("{}/config.json".format(os.path.realpath(os.path.dirname(__file__)))) as file:
        config = json.load(file)

intents