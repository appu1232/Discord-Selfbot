import json
import math
import re
from appuselfbot import isBot
from discord.ext import commands

class Customcmds:

    def __init__(self, bot):
        self.bot = bot

    # List all custom commands
    @commands.command(pass_context=True)
    async def customcmds(self, ctx):
        with open('commands.json', 'r') as commands:
            cmds = json.load(commands)
        msg = '```json\nList of Custom Commands: {\n'
        for cmd in cmds:
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
            await self.bot.send_message(ctx.message.channel, isBot + msg)
        else:
            msg = msg[7:-3]
            splitList = [msg[i:i + 1900] for i in range(0, len(msg), 1900)]
            allWords = []
            splitmsg = ''
            for i, blocks in enumerate(splitList):
                splitmsg += 'List of Custom Commands: %s of %s\n' % (i + 1, part)
                for b in blocks.split('\n'):
                    splitmsg += b + '\n'
                allWords.append(splitmsg)
                splitmsg = ''
            for i in allWords:
                await self.bot.send_message(ctx.message.channel, '```%s```' % i)

    # Add a custom command
    @commands.command(pass_context=True)
    async def add(self, ctx, *, msg: str):
        words = msg.strip()

        with open('commands.json', 'r') as commands:
            cmds = json.load(commands)

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
                    cmds[entry[0]] = entry[1]

            await self.bot.send_message(ctx.message.channel,
                                   isBot + 'Successfully added ``%s`` to ``%s``' % (entry[1], entry[0]))

        except Exception as e:
            await self.bot.send_message(ctx.message.channel, isBot + 'Error, seomthing went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)

    # Remove a custom command
    @commands.command(pass_context=True)
    async def remove(self, ctx, *, msg: str):
        words = msg.strip()

        with open('commands.json', 'r') as commands:
            cmds = json.load(commands)

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
                                                   isBot + 'Successfully removed ``%s`` from %``s``' % (
                                                   entry[1], entry[0]))

                # Item for key is string
                else:
                    entry = words.split(' ', 1)
                    if entry[0] in cmds:
                        oldValue = cmds[entry[0]]
                        del cmds[entry[0]]
                        success = True
                        await self.bot.send_message(ctx.message.channel,
                                               isBot + 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

            if success == False:
                await self.bot.send_message(ctx.message.channel, isBot + 'Could not find specified command.')

        except Exception as e:
            await self.bot.send_message(ctx.message.channel, isBot + 'Error, something went wrong. Exception: ``%s``' % e)

        # Update commands.json
        with open('commands.json', 'w') as commands:
            commands.truncate()
            json.dump(cmds, commands, indent=4)


def setup(bot):
    bot.add_cog(Customcmds(bot))
