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
                with stdoutIO() as s:
                    result = exec(code, env)
                    if inspect.isawaitable(result):
                        result = await result
                result = s.getvalue()
                if result == '':
                    code = 'print(' + code + ')'
                    with stdoutIO() as s:
                        result = exec(code, env)
                        if inspect.isawaitable(result):
                            result = await result
                    result = s.getvalue()
            except Exception as e:
                await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + python.format(type(e).__name__ + ': ' + str(e)))
                return

            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + python.format(result))

    # Create a script. Console output will be sent to channel as ```output```. If printm() used instead of print(), output is sent as a normal message.
    @py.command(pass_context=True)
    async def make(self, ctx, *, code: str):

        if code.startswith('stealth '):
            stealth = True
            code = code[8:]
        else:
            stealth = False
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Running...')
        if not os.path.isdir('%s/temp/' % os.getcwd()):
            os.makedirs('%s/temp/' % os.getcwd())
        code = code.strip()
        template = open('%s/cogs/subprocess.txt' % os.getcwd(), 'r').readlines()
        if stealth is True:
            template[45] = ''

        code = code.strip('` ')
        code_list = code.split('\n')

        self.bot.subprocesses += 1
        for b,i in enumerate(code_list):
            if i.strip() == '':
                template.insert(39 + b, ' ' * 12 + i + 'if \'[temp.subpro%s, %s]\' not in self.bot.running_procs:' % (self.bot.subprocesses, ctx.message.channel.id) + '\n' + ' ' * 16 + i + 'return\n')
            else:
                template.insert(39 + b, ' ' * 12 + i + '\n')

        try:
            self.bot.unload_extension('temp.subpro%s' % str(self.bot.subprocesses))
        except:
            pass

        if os.path.exists('%s/temp/subpro%s.py' % (os.getcwd(), str(self.bot.subprocesses))):
            os.remove('%s/temp/subpro%s.py' % (os.getcwd(), str(self.bot.subprocesses)))

        with open('%s/temp/subpro%s.py' % (os.getcwd(), str(self.bot.subprocesses)), 'w') as script:
            for b,i in enumerate(template):
                if 'printm(' in i or 'printm (' in i:
                    if 'printm(' in i:
                        spaces, statement = i.split('printm(')
                    else:
                        spaces, statement = i.split('printm (')
                    script.write('%sawait self.bot.send_message(ctx.message.channel, %s)\n' % (spaces, statement[:-2]))
                elif 'print(' in i or 'print (' in i:
                    if 'print(' in i:
                        spaces, statement = i.split('print(')
                    else:
                        spaces, statement = i.split('print (')
                    script.write('%sawait self.bot.send_message(ctx.message.channel, \'```\' + %s + \'```\')\n' % (spaces, statement[:-2]))
                elif 'time.sleep(' in i:
                    spaces, statement = i.split('time.sleep(')
                    script.write('%sawait asyncio.sleep(%s)\n' % (spaces, statement[:-2]))
                elif b == 37:
                    runcmd = ' ' * 4 + 'async def run%s(self, ctx):\n' % str(self.bot.subprocesses)
                    script.write(runcmd)
                else:
                    script.write(i)

        self.bot.running_procs.append('[temp.subpro%s, %s]' % (str(self.bot.subprocesses), ctx.message.channel.id))
        self.bot.load_extension('temp.subpro%s' % str(self.bot.subprocesses))
        with open('config.json') as f:
            config = json.load(f)
        run = await self.bot.send_message(ctx.message.channel, config['cmd_prefix'] + 'run%s' % str(self.bot.subprocesses))
        await self.bot.delete_message(run)

    # Load a saved script and run in current channel
    @py.group(pass_context=True)
    async def load(self, ctx, *, msg: str):
        save_file = msg.strip()
        save_file = save_file[:-3] if save_file.endswith('.py') else save_file
        if not os.path.exists('%s/cogs/save/%s.py' % (os.getcwd(), save_file)):
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Could not find file ``%s``' % save_file)
            return
        file_lines = open('%s/cogs/save/%s.py' % (os.getcwd(), save_file)).readlines()
        stealth = True
        for b, i in enumerate(file_lines):
            if '        await self.bot.send_message(ctx.message.channel, isBot + \'Finished\')' in i:
                stealth = False
            if ']\' not in self.bot.running_procs:' in i:
                proc, statement = i.split(']\' not in self.bot.running_procs:')
                start = proc.split(', ')[0]
                file_lines[b] = start + ', ' + ctx.message.channel.id + ']\' not in self.bot.running_procs:\n'
        with open('%s/cogs/save/%s.py' % (os.getcwd(), save_file), 'w') as new_file:
            for i in file_lines:
                new_file.write(i)
        if stealth:
            await self.bot.delete_message(ctx.message)
        else:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Running...')
        cmd = file_lines[37].split('(self, ctx)')[0][14:]

        self.bot.load_extension('cogs.save.%s' % save_file)
        self.bot.running_procs.append('[cogs.save.%s, %s]' % (save_file, ctx.message.channel.id))
        with open('config.json') as f:
            config = json.load(f)
        run = await self.bot.send_message(ctx.message.channel, config['cmd_prefix'] + '%s' % cmd)
        await self.bot.delete_message(run)

    # Save last made script
    @py.group(pass_context=True)
    async def save(self, ctx, *, msg: str):
        msg = msg.strip()[:-3] if msg.strip().endswith('.py') else msg.strip()
        os.chdir(os.getcwd())
        if not os.path.isdir('%s/cogs/save/' % os.getcwd()):
            os.makedirs('%s/cogs/save/' % os.getcwd())
        if os.path.exists('%s/cogs/save/%s.py' % (os.getcwd(), msg)):
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + '``%s.py`` already exists. Overwrite? ``y/n``.' % msg)
            reply = await self.bot.wait_for_message(author=ctx.message.author)
            if reply.content.lower().strip() != 'y':
                await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Cancelled.')
                return
            if os.path.exists('%s/cogs/save/%s.py' % (os.getcwd(), msg)):
                os.remove('%s/cogs/save/%s.py' % (os.getcwd(), msg.strip()))
                try:
                    self.bot.running_procs.remove('[cogs.save.%s, %s]' % (msg, ctx.message.channel.id))
                except:
                    pass
        try:
            shutil.move('%s/temp/subpro%s.py' % (os.getcwd(), str(self.bot.subprocesses)), '%s/cogs/save/%s.py' % (os.getcwd(), msg))
            file_lines = open('%s/cogs/save/%s.py' % (os.getcwd(), msg)).readlines()
            file_lines[37] = ' ' * 4 + 'async def run%s(self, ctx):\n' % msg
            for b, i in enumerate(file_lines):
                if ']\' not in self.bot.running_procs:' in i:
                    proc, statement = i.split(']\' not in self.bot.running_procs:')
                    start, chnl = proc.split(', ')
                    spaces = start.split('if \'[')[0]
                    folder = '\'[cogs.save.%s' % msg
                    file_lines[b] = spaces + 'if ' + folder + ', ' + chnl + ']\' not in self.bot.running_procs:\n'

            with open('%s/cogs/save/%s.py' % (os.getcwd(), msg), 'w') as new_file:
                for i in file_lines:
                    new_file.write(i)
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Saved script as ``%s.py``' % msg)
        except:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Error saving file as ``%s.py``' % msg)

    # List all saved scripts
    @py.group(pass_context=True)
    async def list(self, ctx):
        os.chdir('%s/cogs/save/' % os.getcwd())
        try:
            if ctx.message.content[8:]:
                numb = ctx.message.content[8:].strip()
                if numb.isdigit():
                    numb = int(numb)
                else:
                    await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Invalid syntax. Ex: ``>py list 1``')
            else:
                numb = 1
            filelist = glob.glob('*.py')
            if len(filelist) == 0:
                await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'No saved scripts.')
                return
            filelist.sort()
            msg = ''
            pages = math.ceil(len(filelist) / 10)
            if numb < 1:
                numb = 1
            elif numb > pages:
                numb = pages

            for i in range(10):
                try:
                    msg += filelist[i + (10 * (numb-1))] + '\n'
                except:
                    break

            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'List of saved scripts. Page ``%s of %s`` ```%s```' % (numb, pages, msg))
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Error, something went wrong: ``%s``' % e)
        finally:
            os.chdir('..')
            os.chdir('..')

    # View a saved scripts
    @py.group(pass_context=True)
    async def view(self, ctx, *, msg: str):
        msg = msg.strip()[:-3] if msg.strip().endswith('.py') else msg.strip()
        os.chdir('%s/cogs/save/' % os.getcwd())
        try:
            if os.path.exists('%s.py' % msg):
                f = open('%s.py' % msg, 'r').readlines()
                lines = 37
                while True:
                    if f[lines].strip() == 'var = traceback.format_exc()':
                        break
                    else:
                        lines += 1
                lines -= 3
                edit_lines = ''
                for i in range(39, lines):
                    if f[i].strip().startswith('await self.bot.send_message(ctx.message.channel, \'```\' +'):
                        spaces, toprint = f[i].split('await self.bot.send_message(ctx.message.channel, \'```\' + ')
                        edit_lines += spaces[12:] + 'print(' + toprint[:-10] + ')\n'
                    elif f[i].strip().startswith('await self.bot.send_message(ctx.message.channel, '):
                        spaces, toprint = f[i].split('await self.bot.send_message(ctx.message.channel, ')
                        edit_lines += spaces[12:] + 'printm(' + toprint[:-2] + ')\n'
                    elif f[i].strip().startswith('await asyncio.sleep('):
                        spaces, toprint = f[i].split('await asyncio.sleep(')
                        edit_lines += spaces[12:] + 'time.sleep(' + toprint[:-2] + ')\n'
                    else:
                        edit_lines += f[i][12:]
                await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Viewing ``%s.py``: ```%s```' % (msg, edit_lines))
            else:
                await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + '``%s.py`` does not exist.' % msg)
                return

        except Exception as e:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Error, something went wrong: ``%s``' % e)
        finally:
            os.chdir('..')
            os.chdir('..')

    # Delete a saved scripts
    @py.group(pass_context=True)
    async def delete(self, ctx, *, msg: str):
        msg = msg.strip()[:-3] if msg.strip().endswith('.py') else msg.strip()
        os.chdir('%s/cogs/save/' % os.getcwd())
        try:
            if os.path.exists('%s.py' % msg):
                os.remove('%s.py' % msg)
                await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Deleted ``%s.py`` from saves.' % msg)
            else:
                await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + '``%s.py`` does not exist.' % msg)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Error, something went wrong: ``%s``' % e)
        finally:
            os.chdir('..')
            os.chdir('..')

    # Clear unsaved scripts in temp
    @py.group(pass_context=True)
    async def clear(self, ctx):
        for i in self.bot.running_procs:
            try:
                ext = i.split(', ')[0]
                self.bot.unload_extension(ext[1:])
            except:
                pass
        try:
            os.chdir('%s/temp' % os.getcwd())
            filelist = glob.glob('*.py')
            for f in filelist:
                os.remove(f)
            self.bot.subprocesses = 0
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Cleared unsaved scripts cache.')
        except:
            pass
        finally:
            os.chdir('..')
            gc.collect()

    # Kill all scripts running in the current channel
    @commands.command(pass_context=True)
    async def kill(self, ctx):
        running = []
        for i in self.bot.running_procs:
            if ctx.message.channel.id in i:
                running.append(i)
                folder = i.split(', ')[0]
                try:
                    self.bot.unload_extension(folder[1:])
                except:
                    pass
        for i in running:
            self.bot.running_procs.remove(i)
        if ctx.message.content[5:].lower().strip() != 's':
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Killed scripts in current channel.')
        else:
            await self.bot.delete_message(ctx.message)

    # Kill all scripts
    @commands.command(pass_context=True)
    async def killall(self, ctx):
        for i in self.bot.running_procs:
            folder = i.split(', ')[0]
            try:
                self.bot.unload_extension(folder[1:])
            except:
                pass
        self.bot.running_procs = []
        if ctx.message.content[8:].lower().strip() != 's':
            await self.bot.send_message(ctx.message.channel, appuselfbot.isBot + 'Killed all running scripts.')
        else:
            await self.bot.delete_message(ctx.message)


def setup(bot):
    bot.add_cog(Debugger(bot))
