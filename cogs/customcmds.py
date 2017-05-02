import math
import re
from PythonGists import PythonGists
from appuselfbot import bot_prefix
from discord.ext import commands
from cogs.utils.checks import *

'''Module for custom commands adding, removing, and viewing.'''


class Customcmds:

    def __init__(self, bot):
        self.bot = bot

    # List all custom commands
    @commands.group(pass_context=True)
    async def customcmds(self, ctx):
        """Lists all customcmds. >help customcmds for more info
        
        >customcmds - normal output with all the customcmds and subcommands (response names).
        >customcmds <command_name> - output only this specific command.
        >customcmds gist - normal output but posted to Gist to avoid cluttering the chat."""
        if ctx.invoked_subcommand is None:
            with open('settings/commands.json', 'r') as c:
                cmds = json.load(c)
            sortedcmds = sorted(cmds.keys(), key=lambda x: x.lower())
            msgs = []
            part = ''
            if ctx.message.content[12:] and ctx.message.content[12:] != 'gist':
                one_cmd = True
                list_cmd = ctx.message.content.strip().split(' ')[1]
                for cmd in sortedcmds:
                    if one_cmd and list_cmd == cmd:
                        if type(cmds[cmd]) is list:
                            part = cmd + ': '
                            for i in cmds[cmd]:
                                part += str(i[0]) + ' | '
                            part = part.rstrip(' | ')
                            break
                        else:
                            part = cmd

            else:
                for cmd in sortedcmds:
                    if type(cmds[cmd]) is list:
                        check = cmd + ': '
                        for i in cmds[cmd]:
                            check += str(i[0]) + ' | '
                        check = check.rstrip(' | ') + '\n\n'
                    else:
                        check = cmd + '\n\n'
                    if len(part + check) > 1900:
                        msgs.append(part)
                        part = check
                    else:
                        part += check
            msgs.append(part)
            if 'gist' in ctx.message.content or 'Gist' in ctx.message.content:
                msgs = '\n'.join(msgs)
                url = PythonGists.Gist(description='Custom Commands', content=str(msgs), name='commands.txt')
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'List of Custom Commands: %s' % url)
            else:
                if len(msgs) == 1:
                    await self.bot.send_message(ctx.message.channel, '```css\n[List of Custom Commands]\n%s ```' % msgs[0].rstrip())
                else:
                    for b, i in enumerate(msgs):
                        await self.bot.send_message(ctx.message.channel, '```css\n[List of Custom Commands %s/%s]\n%s ```' % (b + 1, len(msgs), i.rstrip()))
        await self.bot.delete_message(ctx.message)

    @customcmds.command(pass_context=True)
    async def long(self, ctx):
        """Lists detailed version of customcmds. Ex: >customcmd long"""
        with open('settings/commands.json') as commands:
            if 'gist' in ctx.message.content or 'Gist' in ctx.message.content:
                cmds = commands.read()
                link = PythonGists.Gist(description='Full commands.json', content=cmds, name='commands.json')
                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Full commands.json: %s' % link)
            else:
                cmds = json.load(commands)
        msg = ''
        sortedcmds = sorted(cmds.keys(), key=lambda x: x.lower())
        if ctx.message.content[17:] and ctx.message.content[17:] != 'gist':
            one_cmd = True
            list_cmd = ctx.message.content.strip().split('long')[1].strip()
            for cmd in sortedcmds:
                if one_cmd and list_cmd == cmd:
                    msg += '"' + cmd + '" : "'
                    if type(cmds[cmd]) == list:
                        for i in cmds[cmd]:
                            msg += str(i) + ', '
                        msg = msg[:-2] + '",\n\n'
                    else:
                        msg += str(cmds[cmd]) + '",\n\n'

        else:
            for cmd in sortedcmds:
                msg += '"' + cmd + '" : "'
                if type(cmds[cmd]) == list:
                    for i in cmds[cmd]:
                        msg += str(i) + ', '
                    msg = msg[:-2] + '",\n\n'
                else:
                    msg += str(cmds[cmd]) + '",\n\n'
        msg = msg[:-3]
        msg += '}```'
        part = int(math.ceil(len(msg) / 1900))
        if part == 1:
            await self.bot.send_message(ctx.message.channel, bot_prefix + '```json\nList of Custom Commands: {\n' + msg)
        else:
            msg = msg[7:-3]
            splitList = [msg[i:i + 1900] for i in range(0, len(msg), 1900)]
            allWords = []
            splitmsg = ''
            for i, blocks in enumerate(splitList):
                splitmsg += 'List of Custom Commands: %s of %s\n\n' % (i + 1, part)
                for b in blocks.split('\n'):
                    splitmsg += b + '\n'
                allWords.append(splitmsg)
                splitmsg = ''
            for i in allWords:
                await self.bot.send_message(ctx.message.channel, '```%s```' % i)

    # Change customcmd embed color
    @customcmds.command(pass_context=True, aliases=['colour'])
    async def color(self, ctx, *, msg: str = None):
        '''Set color (hex) of a custom command image. Ex: >customcmd color 000000'''
        if msg:
            try:
                msg = msg.lstrip('#')
                int(msg, 16)
            except:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid color.')
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Successfully set color for customcmd embeds.')
        else:
            msg = ''
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Removed embed color for customcmd embeds.')
        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            opt['customcmd_color'] = msg
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)

    # Toggle auto-embed for images/gifs
    @customcmds.command(pass_context=True)
    async def embed(self, ctx):
        """Toggle auto embeding of images for custom commands."""
        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            if opt['rich_embed'] == 'on':
                opt['rich_embed'] = 'off'
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Turned off auto-embeding images/gifs for customcmds.')
            else:
                opt['rich_embed'] = 'on'
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Turned on auto-embeding images/gifs for customcmds.')
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)

    # Add a custom command
    @commands.command(pass_context=True)
    async def add(self, ctx, *, msg: str):
        """Add a new customcmd. >help add for more info
        
        There are two ways to add custom commands. The first way:
        ----Simple----
        >add <command> <response> Now, if you do .<command> you will receive <response>.
        Example: >add nervous http://i.imgur.com/K9gMjWo.gifv
        Then, doing .nervous will output this imgur link (images and gifs will auto embed) Assuming that your customcmd_prefix is set to "." 

        ---Multiple responses to the same command----
        >add <command> <response_name> <response>. This way, you can add multiple responses to the same command.
        Example:
        >add cry k-on http://i.imgur.com/tWtXttk.gif 
        
        Then you can add another to the .cry command:
        >add cry nichijou https://media.giphy.com/media/3fmRTfVIKMRiM/giphy.gif
        
        Note: If anything you are adding/removing is more than one word, you MUST put each part in quotes.
        Example: >add "cry" "mugi why" "http://i.imgur.com/tWtXttk.gif" or >add "copypasta" "I identify as an attack helicopter."
        
        Then invoke a specific response with .<command> <response_name> or get a random response for that command with .<command>
        So: .cry k-on would give you that specific link but .cry would give you one of the two you added to the cry command."""
        words = msg.strip()

        with open('settings/commands.json', 'r') as commands:
            cmds = json.load(commands)
            save = cmds

        try:

            # If there are quotes in the message (meaning multiple words for each param)
            if '"' in words:
                entry = re.findall('"([^"]+)"', words)

                # Item for key is list
                if len(entry) == 3:

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            entries.append(tuple((i[0], i[1])))
                        entries.append(tuple([entry[1], entry[2]]))
                        cmds[entry[0]] = entries
                    else:
                        cmds[entry[0]] = [(entry[1], entry[2])]

                # Item for key is string
                else:
                    if entry[0] in cmds:
                        if type(cmds[entry[0]]) is list:
                            return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Error, this is a list command. To append to this command, you need a <response name>. Ex: ``>add cmd response_name response``')
                    cmds[entry[0]] = entry[1]

            # No quotes so spaces seperate params
            else:

                # Item for key is list
                if len(words.split(' ')) == 3:
                    entry = words.split(' ', 2)

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            entries.append(tuple((i[0], i[1])))
                        entries.append(tuple([entry[1], entry[2]]))
                        cmds[entry[0]] = entries
                    else:
                        cmds[entry[0]] = [(entry[1], entry[2])]

                # Item for key is string
                else:
                    entry = words.split(' ', 1)
                    if entry[0] in cmds:
                        if type(cmds[entry[0]]) is list:
                            return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Error, this is a list command. To append to this command, you need a <response name>. Ex: ``>add cmd response_name response``')
                    cmds[entry[0]] = entry[1]

            await self.bot.send_message(ctx.message.channel,
                                   bot_prefix + 'Successfully added ``%s`` to ``%s``' % (entry[1], entry[0]))

        except Exception as e:
            with open('settings/commands.json', 'w') as commands:
                commands.truncate()
                json.dump(save, commands, indent=4)
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('settings/commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)

    # Remove a custom command
    @commands.command(pass_context=True)
    async def remove(self, ctx, *, msg: str):
        """Remove a customcmd. >help remove for more info.
        
        >remove <command> or >remove <command> <response_name> if you want to remove a specific response for a command.
        
        Just like with the add cmd, note that if anything you are adding/removing is more than one word, you must put each part in quotes.
        Example: If "cry" is the command and "mugi why" is the name for one of the links, removing that link would be: >remove "cry" "mugi why" """
        words = msg.strip()

        with open('settings/commands.json', 'r') as commands:
            cmds = json.load(commands)
            save = cmds

        try:

            # If there are quotes in the message (meaning multiple words for each param)
            success = False

            def check(msg):
                if msg:
                    return msg.content.lower().strip() == 'y' or msg.content.lower().strip() == 'n'
                else:
                    return False
            if '"' in words:
                entry = re.findall('"([^"]+)"', words)

                # Item for key is list
                if len(entry) == 2:

                    # Key exists
                    if entry[0] in cmds:
                        entries = []
                        for i in cmds[entry[0]]:
                            if entry[1] == i[0]:
                                cmds[entry[0]].remove(i)
                                await self.bot.send_message(ctx.message.channel,
                                                       bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (
                                                       entry[1], entry[0]))
                                success = True
                    else:
                        if entry[0] in cmds:
                            del cmds[entry[0]]
                            success = True
                            await self.bot.send_message(ctx.message.channel,
                                                   bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (
                                                   entry[1], entry[0]))


                # Item for key is string
                else:
                    if entry[0] in cmds:
                        if type(cmds[entry[0]]) is list:
                            await self.bot.send_message(ctx.message.channel, bot_prefix + 'This will delete all responses for this list command. Are you sure you want to do this? (y/n).')
                            reply = await self.bot.wait_for_message(timeout=10, author=ctx.message.author, check=check)
                            if reply:
                                if reply.content.lower().strip() == 'n':
                                    return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Cancelled.')
                            else:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Cancelled.')
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        await self.bot.send_message(ctx.message.channel,
                                               bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

            # No quotes so spaces seperate params
            else:

                # Item for key is list
                if len(words.split(' ')) == 2:
                    entry = words.split(' ')

                    # Key exists
                    if entry[0] in cmds:
                        for i in cmds[entry[0]]:
                            if entry[1] == i[0]:
                                cmds[entry[0]].remove(i)
                                await self.bot.send_message(ctx.message.channel,
                                                       bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (
                                                       entry[1], entry[0]))
                                success = True
                    else:
                        if entry[0] in cmds:
                            del cmds[entry[0]]
                            success = True
                            await self.bot.send_message(ctx.message.channel,
                                                   bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))

                # Item for key is string
                else:
                    entry = words.split(' ', 1)
                    if entry[0] in cmds:
                        if type(cmds[entry[0]]) is list:
                            await self.bot.send_message(ctx.message.channel, bot_prefix + 'This will delete all responses for this list command. Are you sure you want to do this? (y/n).')
                            reply = await self.bot.wait_for_message(timeout=10, author=ctx.message.author, check=check)
                            if reply:
                                if reply.content.lower().strip() == 'n':
                                    return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Cancelled.')
                            else:
                                return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Cancelled.')
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        await self.bot.send_message(ctx.message.channel,
                                               bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

            if success == False:
                await self.bot.send_message(ctx.message.channel, bot_prefix + 'Could not find specified command.')

        except Exception as e:
            with open('settings/commands.json', 'w') as commands:
                commands.truncate()
                json.dump(save, commands, indent=4)
            await self.bot.send_message(ctx.message.channel, bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('settings/commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)


def setup(bot):
    bot.add_cog(Customcmds(bot))
