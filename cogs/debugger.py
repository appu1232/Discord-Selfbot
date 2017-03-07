import contextlib
import sys
import inspect
import os
import shutil
import appuselfbot
import glob
import math
import json
import gc
from discord.ext import commands
from io import StringIO

# Common imports that can be used by the debugger.
import datetime
import time
import traceback
import prettytable
import re
import io
import asyncio
import discord
import random
import subprocess
from bs4 import BeautifulSoup
import urllib
import requests

# Used to get the output of exec()
@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

class Debugger:

    def __init__(self, bot):
        self.bot = bot

    # Standalone can be used for quick evals/execs.
    @commands.group(pass_context=True)
    async def py(self, ctx):

        # Got the idea from RoboDanny bot by Rapptz. RoboDanny uses eval() but I use exec() to cover a wider scope of possible inputs.
        if ctx.invoked_subcommand is None:
            code = ctx.message.content[3:].strip('` ')
            python = '```py\n{}\n```'

            env = {
                'bot': self.bot,
                'ctx': ctx,
                'message': ctx.message,
                'server': ctx.message.server,
                'channel': ctx.message.channel,
                'author': ctx.message.author
            }
            env.update(globals())
            try:
                result = eval(code, env)
                if inspect.isawaitable(result):
                    result = await result
            except SyntaxError:
                try:
                    with stdoutIO() as s:
                        result = exec(code, env)
                        if inspect.isawaitable(result):
                            result = await result
                    result = s.getvalue()
                except Exception as g:
                    return await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + python.format(type(g).__name__ + ': ' + str(g)))

            except Exception as e:
                return await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + python.format(type(e).__name__ + ': ' + str(e)))

            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + python.format(result))

    # Load an extension
    @commands.command(pass_context=True)
    async def load(self, ctx, *, msg):
        try:
            self.bot.load_extension(msg)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Failed to load module: `{}`'.format(msg))
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + '{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Loaded module: `{}`'.format(msg))
        await self.bot.delete_message(ctx.message)

    # Unload an extension
    @commands.command(pass_context=True)
    async def unload(self, ctx, *, msg):
        try:
            self.bot.unload_extension(msg)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Failed to unload module: `{}`'.format(msg))
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + '{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Unloaded module: `{}`'.format(msg))
        await self.bot.delete_message(ctx.message)


def setup(bot):
    bot.add_cog(Debugger(bot))
