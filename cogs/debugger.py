import pkg_resources
import contextlib
import sys
import inspect
import os
import shutil
import glob
import math
import textwrap
from discord.ext import commands
from io import StringIO
from traceback import format_exc
from cogs.utils.checks import *
from contextlib import redirect_stdout

# Common imports that can be used by the debugger.
import requests
import json
import gc
import datetime
import time
import traceback
import re
import io
import asyncio
import discord
import random
import subprocess
from bs4 import BeautifulSoup
import urllib
import psutil

'''Module for the python interpreter as well as saving, loading, viewing, etc. the cmds/scripts ran with the interpreter.'''


class Debugger:

    def __init__(self, bot):
        self.bot = bot
        self.stream = io.StringIO()
        self.channel = None
        self._last_result = None

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    # Executes/evaluates code.Pretty much the same as Rapptz implementation for RoboDanny with slight variations.
    async def interpreter(self, env, code, ctx):
        body = self.cleanup_code(code)
        stdout = io.StringIO()

        os.chdir(os.getcwd())
        with open('%s/cogs/utils/temp.txt' % os.getcwd(), 'w') as temp:
            temp.write(body)

        to_compile = 'async def func():\n{}'.format(textwrap.indent(body, "  "))

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send('```\n{}: {}\n```'.format(e.__class__.__name__, e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send('```\n{}{}\n```'.format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()

            result = None
            if ret is None:
                if value:
                    result = '```\n{}\n```'.format(value)
                else:
                    try:
                        result = '```\n{}\n```'.format(repr(eval(body, env)))
                    except:
                        pass
            else:
                self._last_result = ret
                result = '```\n{}{}\n```'.format(value, ret)

            if result:
                if len(str(result)) > 1950:
                    url = await hastebin(str(result).strip("`"), self.bot.session)
                    result = self.bot.bot_prefix + 'Large output. Posted to Hastebin: %s' % url
                    await ctx.send(result)

                else:
                    await ctx.send(result)
            else:
                await ctx.send("```\n```")

    @commands.command(pass_context=True)
    async def debug(self, ctx, *, option: str = None):
        """Shows useful informations to people that try to help you."""
        try:
            if embed_perms(ctx.message):
                em = discord.Embed(color=0xad2929, title='\ud83e\udd16 Appu\'s Discord Selfbot Debug Infos')
                system = ''
                if sys.platform == 'linux':
                    system = subprocess.run(['uname', '-a'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                    if 'ubuntu' in system.lower():
                        system += '\n'+subprocess.run(['lsb_release', '-a'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                elif sys.platform == 'win32':
                    try: platform
                    except: import platform
                    system = '%s %s (%s)'%(platform.system(), platform.version(), sys.platform)
                else:
                    system = sys.platform
                em.add_field(name='Operating System', value='%s' % system, inline=False)
                try:
                    foo = subprocess.run("pip show discord.py", stdout=subprocess.PIPE)
                    _ver = re.search(r'Version: (\d+.\d+.\w+)', str(foo.stdout)).group(1)
                except: _ver = discord.__version__
                em.add_field(name='Discord.py Version', value='%s'%_ver)
                em.add_field(name='PIP Version', value='%s'%pkg_resources.get_distribution('pip').version)
                if os.path.exists('.git'):
                    try: em.add_field(name='Bot version', value='%s' % os.popen('git rev-parse --verify HEAD').read()[:7])
                    except: pass
                em.add_field(name='Python Version', value='%s (%s)'%(sys.version,sys.api_version), inline=False)
                if option and 'deps' in option.lower():
                    dependencies = ''
                    dep_file = sorted(open('%s/requirements.txt' % os.getcwd()).read().split("\n"), key=str.lower)
                    for dep in dep_file:
                        if not '==' in dep: continue
                        dep = dep.split('==')
                        cur = pkg_resources.get_distribution(dep[0]).version
                        if cur == dep[1]: dependencies += '\✅ %s: %s\n'%(dep[0], cur)
                        else: dependencies += '\❌ %s: %s / %s\n'%(dep[0], cur, dep[1])
                    em.add_field(name='Dependencies', value='%s' % dependencies)
                cog_list = ["cogs." + os.path.splitext(f)[0] for f in [os.path.basename(f) for f in glob.glob("cogs/*.py")]]
                loaded_cogs = [x.__module__.split(".")[1] for x in self.bot.cogs.values()]
                unloaded_cogs = [c.split(".")[1] for c in cog_list if c.split(".")[1] not in loaded_cogs]
                if option and 'cogs' in option.lower():
                    if len(loaded_cogs) > 0: em.add_field(name='Loaded Cogs ({})'.format(len(loaded_cogs)), value='\n'.join(sorted(loaded_cogs)), inline=True)
                    if len(unloaded_cogs) > 0: em.add_field(name='Unloaded Cogs ({})'.format(len(unloaded_cogs)), value='\n'.join(sorted(unloaded_cogs)), inline=True)
                else: em.add_field(name='Cogs', value='{} loaded.\n{} unloaded'.format(len(loaded_cogs), len(unloaded_cogs)), inline=True)
                if option and 'path' in option.lower():
                    paths = "\n".join(sys.path).strip()
                    if len(paths) > 300:
                        url = await hastebin(str(paths), self.bot.session)
                        em.add_field(name='Import Paths', value=paths[:300]+' [(Show more)](%s)'%url)
                    else:
                        em.add_field(name='Import Paths', value=paths)

                user = subprocess.run(['whoami'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                if sys.platform == 'linux':
                    user += '@'+subprocess.run(['hostname'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                em.set_footer(text='Generated at {:%Y-%m-%d %H:%M:%S} by {}'.format(datetime.datetime.now(), user))
                try: await ctx.send(content=None, embed=em)
                except discord.HTTPException as e:
                    await ctx.send(content=None, embed=em)
            else:
                await ctx.send('No permissions to embed debug info.')
        except:
            await ctx.send('``` %s ```'%format_exc())

    @commands.group(pass_context=True, invoke_without_command=True)
    async def py(self, ctx, *, msg):
        """Python interpreter. See the wiki for more info."""

        if ctx.invoked_subcommand is None:
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'server': ctx.guild,
                'message': ctx.message,
                '_': self._last_result
            }

            env.update(globals())

            await self.interpreter(env, msg, ctx)


    # Save last [p]py cmd/script.
    @py.command(pass_context=True)
    async def save(self, ctx, *, msg):
        """Save the code you last ran. Ex: [p]py save stuff"""
        msg = msg.strip()[:-4] if msg.strip().endswith('.txt') else msg.strip()
        os.chdir(os.getcwd())
        if not os.path.exists('%s/cogs/utils/temp.txt' % os.getcwd()):
            return await ctx.send(self.bot.bot_prefix + 'Nothing to save. Run a ``>py`` cmd/script first.')
        if not os.path.isdir('%s/cogs/utils/save/' % os.getcwd()):
            os.makedirs('%s/cogs/utils/save/' % os.getcwd())
        if os.path.exists('%s/cogs/utils/save/%s.txt' % (os.getcwd(), msg)):
            await ctx.send(self.bot.bot_prefix + '``%s.txt`` already exists. Overwrite? ``y/n``.' % msg)
            reply = await self.bot.wait_for('message', check=lambda m: m.author == ctx.message.author and (m.content.lower() == 'y' or m.content.lower() == 'n'))
            if reply.content.lower().strip() != 'y':
                return await ctx.send(self.bot.bot_prefix + 'Cancelled.')
            if os.path.exists('%s/cogs/utils/save/%s.txt' % (os.getcwd(), msg)):
                os.remove('%s/cogs/utils/save/%s.txt' % (os.getcwd(), msg))

        try:
            shutil.move('%s/cogs/utils/temp.txt' % os.getcwd(), '%s/cogs/utils/save/%s.txt' % (os.getcwd(), msg))
            await ctx.send(self.bot.bot_prefix + 'Saved last run cmd/script as ``%s.txt``' % msg)
        except:
            await ctx.send(self.bot.bot_prefix + 'Error saving file as ``%s.txt``' % msg)

    # Load a cmd/script saved with the [p]save cmd
    @py.command(aliases=['start'], pass_context=True)
    async def run(self, ctx, *, msg):
        """Run code that you saved with the save commmand. Ex: [p]py run stuff parameter1 parameter2"""
        # Like in unix, the first parameter is the script name
        parameters = msg.split()
        save_file = parameters[0] # Force scope
        if save_file.endswith('.txt'):
            save_file = save_file[:-(len('.txt'))] # Temptation to put '.txt' in a constant increases
        else:
            parameters[0] += '.txt' # The script name is always full

        if not os.path.exists('%s/cogs/utils/save/%s.txt' % (os.getcwd(), save_file)):
            return await ctx.send(self.bot.bot_prefix + 'Could not find file ``%s.txt``' % save_file)

        script = open('%s/cogs/utils/save/%s.txt' % (os.getcwd(), save_file)).read()

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'server': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
            'argv': parameters
        }

        env.update(globals())

        await self.interpreter(env, script, ctx)

    # List saved cmd/scripts
    @py.command(aliases=['ls'], pass_context=True)
    async def list(self, ctx, txt: str = None):
        """List all saved scripts. Ex: [p]py list or [p]py ls"""
        try:
            if txt:
                numb = txt.strip()
                if numb.isdigit():
                    numb = int(numb)
                else:
                    await ctx.send(self.bot.bot_prefix + 'Invalid syntax. Ex: ``>py list 1``')
            else:
                numb = 1
            filelist = glob.glob('cogs/utils/save/*.txt')
            if len(filelist) == 0:
                return await ctx.send(self.bot.bot_prefix + 'No saved cmd/scripts.')
            filelist.sort()
            msg = ''
            pages = int(math.ceil(len(filelist) / 10))
            if numb < 1:
                numb = 1
            elif numb > pages:
                numb = pages

            for i in range(10):
                try:
                    msg += filelist[i + (10 * (numb-1))][16:] + '\n'
                except:
                    break

            await ctx.send(self.bot.bot_prefix + 'List of saved cmd/scripts. Page ``%s of %s`` ```%s```' % (numb, pages, msg))
        except Exception as e:
            await ctx.send(self.bot.bot_prefix + 'Error, something went wrong: ``%s``' % e)

    # View a saved cmd/script
    @py.group(aliases=['vi', 'vim'], pass_context=True)
    async def view(self, ctx, *, msg: str):
        """View a saved script's contents. Ex: [p]py view stuff"""
        msg = msg.strip()[:-4] if msg.strip().endswith('.txt') else msg.strip()
        try:
            if os.path.isfile('cogs/utils/save/%s.txt' % msg):
                f = open('cogs/utils/save/%s.txt' % msg, 'r').read()
                await ctx.send(self.bot.bot_prefix + 'Viewing ``%s.txt``: ```py\n%s```' % (msg, f.strip('` ')))
            else:
                await ctx.send(self.bot.bot_prefix + '``%s.txt`` does not exist.' % msg)

        except Exception as e:
            await ctx.send(self.bot.bot_prefix + 'Error, something went wrong: ``%s``' % e)

    # Delete a saved cmd/script
    @py.group(aliases=['rm'], pass_context=True)
    async def delete(self, ctx, *, msg: str):
        """Delete a saved script. Ex: [p]py delete stuff"""
        msg = msg.strip()[:-4] if msg.strip().endswith('.txt') else msg.strip()
        try:
            if os.path.exists('cogs/utils/save/%s.txt' % msg):
                os.remove('cogs/utils/save/%s.txt' % msg)
                await ctx.send(self.bot.bot_prefix + 'Deleted ``%s.txt`` from saves.' % msg)
            else:
                await ctx.send(self.bot.bot_prefix + '``%s.txt`` does not exist.' % msg)
        except Exception as e:
            await ctx.send(self.bot.bot_prefix + 'Error, something went wrong: ``%s``' % e)

    @commands.command(pass_context=True)
    async def load(self, ctx, *, msg):
        """Load a module."""
        await ctx.message.delete()
        try:
            if os.path.exists("custom_cogs/{}.py".format(msg)):
                self.bot.load_extension("custom_cogs.{}".format(msg))
            elif os.path.exists("cogs/{}.py".format(msg)):
                self.bot.load_extension("cogs.{}".format(msg))
            else:
                raise ImportError("No module named '{}'".format(msg))
        except Exception as e:
            await ctx.send(self.bot.bot_prefix + 'Failed to load module: `{}.py`'.format(msg))
            await ctx.send(self.bot.bot_prefix + '{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send(self.bot.bot_prefix + 'Loaded module: `{}.py`'.format(msg))

    @commands.command(pass_context=True)
    async def unload(self, ctx, *, msg):
        """Unload a module"""
        await ctx.message.delete()
        try:
            if os.path.exists("cogs/{}.py".format(msg)):
                self.bot.unload_extension("cogs.{}".format(msg))
            elif os.path.exists("custom_cogs/{}.py".format(msg)):
                self.bot.unload_extension("custom_cogs.{}".format(msg))
            else:
                raise ImportError("No module named '{}'".format(msg))
        except Exception as e:
            await ctx.send(self.bot.bot_prefix + 'Failed to unload module: `{}.py`'.format(msg))
            await ctx.send(self.bot.bot_prefix + '{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send(self.bot.bot_prefix + 'Unloaded module: `{}.py`'.format(msg))

    @commands.command(pass_context=True)
    async def loadall(self, ctx):
        """Loads all core modules"""
        await ctx.message.delete()
        errors = ""
        for cog in os.listdir("cogs"):
            if ".py" in cog:
                cog = cog.replace('.py', '')
                try:
                    self.bot.load_extension("cogs.{}".format(cog))
                except Exception as e:
                    errors += 'Failed to load module: `{}.py` due to `{}: {}`\n'.format(cog, type(e).__name__, e)
        if not errors:
            await ctx.send(self.bot.bot_prefix + "All core modules loaded")
        else:
            await ctx.send(self.bot.bot_prefix + errors)            
            
    @commands.command(pass_context=True)
    async def redirect(self, ctx):
        """Redirect STDOUT and STDERR to a channel for debugging purposes."""
        sys.stdout = self.stream
        sys.stderr = self.stream
        self.channel = ctx.message.channel
        await ctx.send(self.bot.bot_prefix + "Successfully redirected STDOUT and STDERR to the current channel!")

    @commands.command(pass_context=True)
    async def unredirect(self, ctx):
        """Redirect STDOUT and STDERR back to the console for debugging purposes."""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.channel = None
        await ctx.send(self.bot.bot_prefix + "Successfully redirected STDOUT and STDERR back to the console!")

    async def redirection_clock(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Debugger"):
            await asyncio.sleep(0.2)
            stream_content = self.stream.getvalue()
            if stream_content and self.channel:
                await self.channel.send("```" + stream_content + "```")
                self.stream = io.StringIO()
                sys.stdout = self.stream
                sys.stderr = self.stream


def setup(bot):
    debug_cog = Debugger(bot)
    bot.loop.create_task(debug_cog.redirection_clock())
    bot.add_cog(debug_cog)
