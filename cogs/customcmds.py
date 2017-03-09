import json
import math
import re
from appuselfbot import isBot
from discord.ext import commands

class Customcmds:

    def __init__(self, bot):
        self.bot = bot

    # List all custom commands
    @commands.group(pass_context=True)
    async def customcmds(self, ctx):
        if ctx.invoked_subcommand is None:
            with open('settings/commands.json', 'r') as commands:
                cmds = json.load(commands)
            sortedcmds = sorted(cmds.keys(), key=lambda x: x.lower())
            msgs = []
            part = ''
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
            if len(msgs) == 1:
                await self.bot.send_message(ctx.message.channel, '```css\n[List of Custom Commands]\n%s ```' % msgs[0].rstrip())
            else:
                for b, i in enumerate(msgs):
                    await self.bot.send_message(ctx.message.channel, '```css\n[List of Custom Commands %s/%s]\n%s ```' % (b + 1, len(msgs), i.rstrip()))
        await self.bot.delete_message(ctx.message)

    @customcmds.command(pass_context=True)
    async def long(self, ctx):
        with open('settings/commands.json', 'r') as commands:
            cmds = json.load(commands)
        msg = ''
        sortedcmds = sorted(cmds.keys(), key=lambda x: x.lower())
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
            await self.bot.send_message(ctx.message.channel, isBot + '```json\nList of Custom Commands: {\n' + msg)
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
        await self.bot.delete_message(ctx.message)

    # Add a custom command
    @commands.command(pass_context=True)
    async def add(self, ctx, *, msg: str):
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
                    if type(cmds[entry[0]]) is list:
                        return await self.bot.send_message(ctx.message.channel, isBot + 'Error, this is a list command. To append to this command, you need a <response name>. Ex: ``>add cmd response_name response``')
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
                    if type(cmds[entry[0]]) is list:
                        return await self.bot.send_message(ctx.message.channel, isBot + 'Error, this is a list command. To append to this command, you need a <response name>. Ex: ``>add cmd response_name response``')
                    cmds[entry[0]] = entry[1]

            await self.bot.send_message(ctx.message.channel,
                                   isBot + 'Successfully added ``%s`` to ``%s``' % (entry[1], entry[0]))

        except Exception as e:
            with open('settings/commands.json', 'w') as commands:
                commands.truncate()
                json.dump(save, commands, indent=4)
            await self.bot.send_message(ctx.message.channel, isBot + 'Error, something went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('settings/commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)

    # Remove a custom command
    @commands.command(pass_context=True)
    async def remove(self, ctx, *, msg: str):
        words = msg.strip()

        with open('settings/commands.json', 'r') as commands:
            cmds = json.load(commands)
            save = cmds

        try:

            # If there are quotes in the message (meaning multiple words for each param)
            success = False
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
                                                       isBot + 'Successfully removed ``%s`` from ``%s``' % (
                                                       entry[1], entry[0]))
                                success = True
                    else:
                        if entry[0] in cmds:
                            del cmds[entry[0]]
                            success = True
                            await self.bot.send_message(ctx.message.channel,
                                                   isBot + 'Successfully removed ``%s`` from ``%s``' % (
                                                   entry[1], entry[0]))


                # Item for key is string
                else:
                    if entry[0] in cmds:
                        if type(cmds[entry[0]]) is list:
                            await self.bot.send_message(ctx.message.channel, isBot + 'This will delete all responses for this list command. Enter ``y`` to proceed.')
                            reply = await self.bot.wait_for_message(author=ctx.message.author)
                            if reply.content.lower().strip() != 'y':
                                return await self.bot.send_message(ctx.message.channel, isBot + 'Cancelled.')
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        await self.bot.send_message(ctx.message.channel,
                                               isBot + 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

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
                                                       isBot + 'Successfully removed ``%s`` from ``%s``' % (
                                                       entry[1], entry[0]))
                                success = True
                    else:
                        if entry[0] in cmds:
                            del cmds[entry[0]]
                            success = True
                            await self.bot.send_message(ctx.message.channel,
                                                   isBot + 'Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))

                # Item for key is string
                else:
                    entry = words.split(' ', 1)
                    if entry[0] in cmds:
                        if type(cmds[entry[0]]) is list:
                            await self.bot.send_message(ctx.message.channel, isBot + 'This will delete all responses for this list command. Enter ``y`` to proceed.')
                            reply = await self.bot.wait_for_message(author=ctx.message.author)
                            if reply.content.lower().strip() != 'y':
                                return await self.bot.send_message(ctx.message.channel, isBot + 'Cancelled.')
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        await self.bot.send_message(ctx.message.channel,
                                               isBot + 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

            if success == False:
                await self.bot.send_message(ctx.message.channel, isBot + 'Could not find specified command.')

        except Exception as e:
            with open('settings/commands.json', 'w') as commands:
                commands.truncate()
                json.dump(save, commands, indent=4)
            await self.bot.send_message(ctx.message.channel, isBot + 'Error, something went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('settings/commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)


def setup(bot):
    bot.add_cog(Customcmds(bot))
