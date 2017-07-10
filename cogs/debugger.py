import pkg_resources
import contextlib
import sys
import inspect
import os
import shutil
import appuselfbot
import glob
import math
from PythonGists import PythonGists
from discord.ext import commands
from io import StringIO
from traceback import format_exc
from cogs.utils.checks import *

# Common imports that can be used by the debugger.
import requests
import json
import gc
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
import psutil

'''Module for the python interpreter as well as saving, loading, viewing, etc. the cmds/scripts ran with the interpreter.'''


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

    # Executes/evaluates code. Got the idea from RoboDanny bot by Rapptz. RoboDanny uses eval() but I use exec() to cover a wider scope of possible inputs.
    async def interpreter(self, env, code):
        if code.startswith('[m]'):
            code = code[3:].strip()
            code_block = False
        else:
            code_block = True
        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result
            if not result:
                try:
                    with stdoutIO() as s:
                        result = exec(code, env)
                        if inspect.isawaitable(result):
                            result = await result
                    result = s.getvalue()
                except Exception as g:
                    return self.bot.bot_prefix + '```{}```'.format(type(g).__name__ + ': ' + str(g))
        except SyntaxError:
            try:
                with stdoutIO() as s:
                    result = exec(code, env)
                    if inspect.isawaitable(result):
                        result = await result
                result = s.getvalue()
            except Exception as g:
                return self.bot.bot_prefix + '```{}```'.format(type(g).__name__ + ': ' + str(g))

        except Exception as e:
            return self.bot.bot_prefix + '```{}```'.format(type(e).__name__ + ': ' + str(e))

        if len(str(result)) > 1950:
            url = PythonGists.Gist(description='Py output', content=str(result), name='output.txt')
            return self.bot.bot_prefix + 'Large output. Posted to Gist: %s' % url
        else:
            if code_block:
                return self.bot.bot_prefix + '```py\n{}\n```'.format(result)
            else:
                return result

    @commands.command(pass_context=True)
    async def debug(self, ctx, option: str = None):
        """Shows useful informations to people that try to help you."""
        try:
            if embed_perms(ctx.message):
                em = discord.Embed(color=0xad2929, title='\ud83e\udd16 Appu\'s Discord Selfbot Debug Infos')
                # em.add_field(name='Selfbot Version', value='%s'%self.bot.version)
                system = ''
                if sys.platform == 'linux':
                    system = subprocess.run(['uname', '-a'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                    if 'ubuntu' in system.lower():
                        system += '\n'+subprocess.run(['lsb_release', '-a'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                elif sys.platform == 'win32':
                    try: platform
                    except: import platform
                    system = '%s %s (%s)'%(platform.system(),platform.version(),sys.platform)
                    # os = subprocess.run('systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\"', stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                else:
                    system = sys.platform
                em.add_field(name='Operating System', value='%s' % system)
                em.add_field(name='Discord.py Version', value='%s'%discord.__version__)
                em.add_field(name='Python Version', value='%s (%s)'%(sys.version,sys.api_version), inline=False)
                em.add_field(name='PIP Version', value='%s'%pkg_resources.get_distribution('pip').version, inline=False)
                dependencys = ['discord','prettytable','requests','spice_api','bs4','strawpy','lxml','discord_webhooks','psutil','PythonGists','PIL','pyfiglet','tokage','pytz','github']
                loaded_modules = 0
                unloaded_modules = 0
                for x in dependencys:
                    try:
                        __import__(x.strip())
                        loaded_modules += 1
                    except:
                        unloaded_modules += 1
                
                em.add_field(name='Dependencies', value='{0} modules imported successfully\n {1} modules imported unsuccessfully'.format(loaded_modules, unloaded_modules), inline=False)
                
                cogs = self.bot.cogs
                cogs_folder = os.listdir('cogs')
                cog_folder = []
                for x in cogs_folder:
                    if x.endswith('.py'):
                        cog_folder.append(x)
                    
                
                loaded_cogs = 0
                unloaded_cogs = 0
                for x in cogs:
                    x = self.bot.cogs[x].__module__[5:] + '.py'
                    if x in cog_folder:
                        loaded_cogs += 1
                    else:
                        unloaded_cogs += 1
                        
                em.add_field(name='Cogs', value='{0} cogs loaded\n {1} cogs unloaded'.format(loaded_cogs, len(cog_folder)-loaded_cogs), inline=False)

                user = subprocess.run(['whoami'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                if sys.platform == 'linux':
                    user += user+'@'+subprocess.run(['hostname'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
                em.set_footer(text='Generated at {:%Y-%m-%d %H:%M:%S} by {}'.format(datetime.datetime.now(), user))
                try: await self.bot.send_message(ctx.message.channel, content=None, embed=em)
                except discord.errors.HTTPException as e:
                    await self.bot.send_message(ctx.message.channel, content=None, embed=em)
            else:
                await self.bot.send_message(ctx.message.channel, 'No permissions to embed debug info.')
        except:
            await self.bot.send_message(ctx.message.channel, '``` %s ```'%format_exc())

    @commands.group(pass_context=True, invoke_without_command=True)
    async def py(self, ctx, *, msg):
        """Python interpreter. See the wiki for more info."""

        if ctx.invoked_subcommand is None:
            code = msg.strip().strip('` ')

            env = {
                'bot': self.bot,
                'ctx': ctx,
                'message': ctx.message,
                'server': ctx.message.server,
                'channel': ctx.message.channel,
                'author': ctx.message.author
            }
            env.update(globals())

            result = await self.interpreter(env, code)

            os.chdir(os.getcwd())
            with open('%s/cogs/utils/temp.txt' % os.getcwd(), 'w') as temp:
                temp.write(msg.strip())

            await self.bot.send_message(ctx.message.channel, result)

    # Save last >py cmd/script.
    @py.command(pass_context=True)
    async def save(self, ctx, *, msg):
        """Save the code you last ran. Ex: >py save stuff"""
        msg = msg.strip()[:-4] if msg.strip().endswith('.txt') else msg.strip()
        os.chdir(os.getcwd())
        if not os.path.exists('%s/cogs/utils/temp.txt' % os.getcwd()):
            return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Nothing to save. Run a ``>py`` cmd/script first.')
        if not os.path.isdir('%s/cogs/utils/save/' % os.getcwd()):
            os.makedirs('%s/cogs/utils/save/' % os.getcwd())
        if os.path.exists('%s/cogs/utils/save/%s.txt' % (os.getcwd(), msg)):
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + '``%s.txt`` already exists. Overwrite? ``y/n``.' % msg)
            reply = await self.bot.wait_for_message(author=ctx.message.author)
            if reply.content.lower().strip() != 'y':
                return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Cancelled.')
            if os.path.exists('%s/cogs/utils/save/%s.txt' % (os.getcwd(), msg)):
                os.remove('%s/cogs/utils/save/%s.txt' % (os.getcwd(), msg))

        try:
            shutil.move('%s/cogs/utils/temp.txt' % os.getcwd(), '%s/cogs/utils/save/%s.txt' % (os.getcwd(), msg))
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Saved last run cmd/script as ``%s.txt``' % msg)
        except:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Error saving file as ``%s.txt``' % msg)

    # Load a cmd/script saved with the >save cmd
    @py.command(aliases=['start'], pass_context=True)
    async def run(self, ctx, *, msg):
        """Run code that you saved with the save commmand. Ex: >py run stuff parameter1 parameter2"""
        # Like in unix, the first parameter is the script name
        parameters = msg.split()
        save_file = parameters[0] # Force scope
        if save_file.endswith('.txt'): 
            save_file = save_file[:-(len('.txt'))] # Temptation to put '.txt' in a constant increases
        else:
            parameters[0] += '.txt' # The script name is always full
        
        if not os.path.exists('%s/cogs/utils/save/%s.txt' % (os.getcwd(), save_file)):
            return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Could not find file ``%s.txt``' % save_file)

        script = open('%s/cogs/utils/save/%s.txt' % (os.getcwd(), save_file)).read()

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'server': ctx.message.server,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'argv': parameters
        }
        env.update(globals())

        result = await self.interpreter(env, script.strip('` '))

        await self.bot.send_message(ctx.message.channel, result)

    # List saved cmd/scripts
    @py.command(aliases=['ls'], pass_context=True)
    async def list(self, ctx, txt: str = None):
        """List all saved scripts. Ex: >py list or >py ls"""
        os.chdir('%s/cogs/utils/save/' % os.getcwd())
        try:
            if txt:
                numb = txt.strip()
                if numb.isdigit():
                    numb = int(numb)
                else:
                    await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Invalid syntax. Ex: ``>py list 1``')
            else:
                numb = 1
            filelist = glob.glob('*.txt')
            if len(filelist) == 0:
                return await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'No saved cmd/scripts.')
            filelist.sort()
            msg = ''
            pages = int(math.ceil(len(filelist) / 10))
            if numb < 1:
                numb = 1
            elif numb > pages:
                numb = pages

            for i in range(10):
                try:
                    msg += filelist[i + (10 * (numb-1))] + '\n'
                except:
                    break

            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'List of saved cmd/scripts. Page ``%s of %s`` ```%s```' % (numb, pages, msg))
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Error, something went wrong: ``%s``' % e)
        finally:
            os.chdir('..')
            os.chdir('..')
            os.chdir('..')

    # View a saved cmd/script
    @py.group(aliases=['vi', 'vim'], pass_context=True)
    async def view(self, ctx, *, msg: str):
        """View a saved script's contents. Ex: >py view stuff"""
        msg = msg.strip()[:-4] if msg.strip().endswith('.txt') else msg.strip()
        os.chdir('%s/cogs/utils/save/' % os.getcwd())
        try:
            if os.path.exists('%s.txt' % msg):
                f = open('%s.txt' % msg, 'r').read()
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Viewing ``%s.txt``: ```%s```' % (msg, f.strip('` ')))
            else:
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + '``%s.txt`` does not exist.' % msg)

        except Exception as e:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Error, something went wrong: ``%s``' % e)
        finally:
            os.chdir('..')
            os.chdir('..')
            os.chdir('..')

    # Delete a saved cmd/script
    @py.group(aliases=['rm'], pass_context=True)
    async def delete(self, ctx, *, msg: str):
        """Delete a saved script. Ex: >py delete stuff"""
        msg = msg.strip()[:-4] if msg.strip().endswith('.txt') else msg.strip()
        os.chdir('%s/cogs/utils/save/' % os.getcwd())
        try:
            if os.path.exists('%s.txt' % msg):
                os.remove('%s.txt' % msg)
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Deleted ``%s.txt`` from saves.' % msg)
            else:
                await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + '``%s.txt`` does not exist.' % msg)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Error, something went wrong: ``%s``' % e)
        finally:
            os.chdir('..')
            os.chdir('..')
            os.chdir('..')


    @commands.command(pass_context=True)
    async def load(self, ctx, *, msg):
        """Load a module"""
        await self.bot.delete_message(ctx.message)
        try:
            self.bot.load_extension(msg)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Failed to load module: `{}`'.format(msg))
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + '{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Loaded module: `{}`'.format(msg))

    @commands.command(pass_context=True)
    async def unload(self, ctx, *, msg):
        """Unload a module"""
        await self.bot.delete_message(ctx.message)
        try:
            self.bot.unload_extension(msg)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Failed to unload module: `{}`'.format(msg))
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + '{}: {}'.format(type(e).__name__, e))
        else:
            await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Unloaded module: `{}`'.format(msg))
        
    @commands.command(pass_context=True, aliases=['cc', 'clear', 'cleartrace'])
    async def clearconsole(self, ctx):
        """Clear the console of any errors or other messages."""
        await self.bot.delete_message(ctx.message)
        for _ in range(100):
            print("")
        print('Logged in as')
        try:
            print(self.bot.user.name)
        except:
            pass
        print('User id:' + str(self.bot.user.id))
        print('------')
        await self.bot.send_message(ctx.message.channel, self.bot.bot_prefix + 'Console Cleared')


def setup(bot):
    bot.add_cog(Debugger(bot))
