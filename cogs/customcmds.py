import math
import re
import json
from github import Github
from PythonGists import PythonGists
from discord.ext import commands
from cogs.utils.checks import cmd_prefix_len, load_config

'''Module for custom commands adding, removing, and viewing.'''


class Customcmds:
    def __init__(self, bot):
        self.bot = bot

    async def githubUpload(self, username, password, repo_name):
        g = Github(username, password)
        repo = g.get_user().get_repo(repo_name)
        with open('settings/commands.json', 'r') as fp:
            contents = fp.read()
        updateFile = '/settings/commands.json'
        sha = repo.get_contents(updateFile).sha
        repo.update_file('/settings/commands.json', 'Updating customcommands', contents, sha)

    async def check(self, ctx, val, pre):
        def is_numb(msg):
            if msg.author == ctx.message.author:
                if msg.content.isdigit() and val != 0:
                    return 0 < int(msg.content) < val
                elif val == 0:
                    return True
                else:
                    return False
            else:
                return False

        reply = await self.bot.wait_for("message", check=is_numb)
        return reply

    # view customcmds
    async def customcommands(self, ctx):
        with open('settings/commands.json', 'r') as c:
            cmds = json.load(c)
        sortedcmds = sorted(cmds.keys(), key=lambda x: x.lower())
        msgs = []
        part = ''
        pre = cmd_prefix_len()
        if ctx.message.content[10 + pre:].strip() and ctx.message.content[10 + pre:].strip() != 'gist':
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
            await ctx.send(self.bot.bot_prefix + 'List of Custom Commands: %s' % url)
        else:
            if len(msgs) == 1:
                await ctx.send(
                    '```css\n[List of Custom Commands]\n%s ```' % msgs[0].rstrip())
            else:
                for b, i in enumerate(msgs):
                    await ctx.send(
                        '```css\n[List of Custom Commands %s/%s]\n%s ```' % (
                            b + 1, len(msgs), i.rstrip()))

    # List all custom commands
    @commands.group(pass_context=True)
    async def customcmds(self, ctx):
        """Lists all customcmds. [p]help customcmds for more info

        [p]customcmds - normal output with all the customcmds and subcommands (response names).
        [p]customcmds <command_name> - output only this specific command.
        [p]customcmds gist - normal output but posted to Gist to avoid cluttering the chat."""
        if ctx.invoked_subcommand is None:
            await self.customcommands(ctx)
        await ctx.message.delete()

    @customcmds.command(pass_context=True)
    async def long(self, ctx):
        """Lists detailed version of customcmds. Ex: [p]customcmds long"""
        with open('settings/commands.json') as commands:
            if 'gist' in ctx.message.content or 'Gist' in ctx.message.content:
                cmds = commands.read()
                link = PythonGists.Gist(description='Full commands.json', content=cmds, name='commands.json')
                return await ctx.send(self.bot.bot_prefix + 'Full commands.json: %s' % link)
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
            await ctx.send(self.bot.bot_prefix + '```json\nList of Custom Commands: {\n' + msg)
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
                await ctx.send('```%s```' % i)

    # Change customcmd embed color
    @customcmds.command(pass_context=True, aliases=['colour'])
    async def color(self, ctx, *, msg: str = None):
        '''Set color (hex) of a custom command image. Ex: [p]customcmds color 000000'''
        if msg:
            try:
                msg = msg.lstrip('#')
                int(msg, 16)
            except:
                await ctx.send(self.bot.bot_prefix + 'Invalid color.')
            await ctx.send(self.bot.bot_prefix + 'Successfully set color for customcmd embeds.')
        else:
            msg = ''
            await ctx.send(self.bot.bot_prefix + 'Removed embed color for customcmd embeds.')
        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            opt['customcmd_color'] = msg
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)

    @customcmds.command(pass_context=True)
    async def update(self, ctx):
        """Needs GitHub repo set for an update"""
        with open('settings/github.json', 'r+') as fp:
            opt = json.load(fp)
            if opt['username'] != "":
                try:
                    await self.githubUpload(opt['username'], opt['password'], opt['reponame'])
                except:
                    await ctx.send("Incorrect GitHub credentials")
            else:
                await ctx.send("GitHub account and repo not specified in `github.json`")

    # Toggle auto-embed for images/gifs
    @customcmds.command(pass_context=True)
    async def embed(self, ctx):
        """Toggle auto embeding of images for custom commands."""
        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            if opt['rich_embed'] == 'on':
                opt['rich_embed'] = 'off'
                await ctx.send(self.bot.bot_prefix + 'Turned off auto-embeding images/gifs for customcmds.')
            else:
                opt['rich_embed'] = 'on'
                await ctx.send(self.bot.bot_prefix + 'Turned on auto-embeding images/gifs for customcmds.')
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)

    # Add a custom command
    @commands.command(pass_context=True)
    async def add(self, ctx, *, msg: str = None):
        """Add a new customcmd. [p]help add for more info

        Simply do: [p]add
        This will trigger the menu which you can navigate through and add your custom command that way.

        -----------------------------------------------------------

        Legacy method:

        There are two ways to add custom commands. The first way:
        ----Simple----
        [p]add <command> <response> Now, if you do .<command> you will receive <response>.
        Example: [p]add nervous http://i.imgur.com/K9gMjWo.gifv
        Then, doing .nervous will output this imgur link (images and gifs will auto embed) Assuming that your customcmd_prefix is set to "."

        ---Multiple responses to the same command----
        [p]add <command> <response_name> <response>. This way, you can add multiple responses to the same command.
        Example:
        [p]add cry k-on http://i.imgur.com/tWtXttk.gif

        Then you can add another to the .cry command:
        [p]add cry nichijou https://media.giphy.com/media/3fmRTfVIKMRiM/giphy.gif

        Note: If anything you are adding/removing is more than one word, you MUST put each part in quotes.
        Example: [p]add "cry" "mugi why" "http://i.imgur.com/tWtXttk.gif" or [p]add "copypasta" "I identify as an attack helicopter."

        Then invoke a specific response with .<command> <response_name> or get a random response for that command with .<command>
        So: .cry k-on would give you that specific link but .cry would give you one of the two you added to the cry command."""
        if not msg:

            await ctx.message.delete()
            pre = ctx.message.content.split('add')[0]
            customcmd_prefix = load_config()['customcmd_prefix']
            menu = await ctx.send(self.bot.bot_prefix + '```\n\u2795 Choose type of customcmd to add. Enter a number:\n\n1. Simple customcmd (1 cmd with 1 response).\n2. Customcmd with multiple responses.\n3. View current customcmds.```')

            reply = await self.check(ctx, 4, pre)
            if reply:
                await reply.delete()
                # Add simple customcmd
                if reply.content == "1":
                    await menu.edit(content=self.bot.bot_prefix + '```\n\u2795 Enter a cmd name. This is how you will invoke your response.```')
                    reply = await self.check(ctx, 0, pre)

                    # Grab the cmd name
                    if reply:
                        await reply.delete()
                        entry_cmd = reply.content
                        await menu.edit(content=
                                        self.bot.bot_prefix + '```\n\u2795 Enter the response for this cmd. This is what the bot will output when you send the cmd you specified.```')
                        reply = await self.check(ctx, 0, pre)

                        # Grab the response
                        if reply:
                            try:
                                await reply.delete()
                            except:
                                pass
                            entry_response = reply.content
                            with open('settings/commands.json', 'r+') as commands:
                                cmds = json.load(commands)
                                save = cmds
                                commands.seek(0)
                                commands.truncate()
                                try:
                                    cmds[entry_cmd] = entry_response
                                    json.dump(cmds, commands, indent=4)
                                    await menu.edit(content=
                                                    self.bot.bot_prefix + 'Successfully added ``{}`` to ``{}`` Invoke this response by doing: ``{}``'.format(
                                                        entry_response, entry_cmd,
                                                        customcmd_prefix + entry_cmd))
                                except Exception as e:

                                    json.dump(save, commands, indent=4)
                                    await menu.edit(content=
                                                    self.bot.bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)

                # Add complex customcmd
                elif reply.content == "2":
                    await menu.edit(content=
                                    self.bot.bot_prefix + '```\n\u2795 What to add? Pick a number.\n\n1. Add new command.\n2. Add response to existing command.```')
                    reply = await self.check(ctx, 3, pre)
                    if reply:
                        await reply.delete()

                        # Create new list cmd
                        if reply.content == '1':
                            await menu.edit(content=
                                            self.bot.bot_prefix + '```\n\u2795 Enter the cmd name.```')

                            reply = await self.check(ctx, 0, pre)

                            # Grab cmd name
                            if reply:
                                await reply.delete()
                                entry_cmd = reply.content
                                await menu.edit(content=
                                                self.bot.bot_prefix + '```\n\u2795 Since you selected to have this cmd have multiple responses, these multiple responses must have different names to map them. Enter a response name.```')
                                reply = await self.check(ctx, 0, pre)

                                # Grab response name
                                if reply:
                                    await reply.delete()
                                    entry_response = reply.content
                                    await menu.edit(content=
                                                    self.bot.bot_prefix + '```\n\u2795 Now enter the response.```')
                                    reply = await self.check(ctx, 0, pre)

                                    # Grab the response
                                    if reply:
                                        try:
                                            await reply.delete()
                                        except:
                                            pass
                                        response = reply.content
                                        with open('settings/commands.json', 'r+') as commands:
                                            cmds = json.load(commands)
                                            save = cmds
                                            commands.seek(0)
                                            commands.truncate()
                                            try:
                                                cmds[entry_cmd] = [[entry_response, response]]

                                                json.dump(cmds, commands, indent=4)
                                                await menu.edit(content=
                                                                self.bot.bot_prefix + 'Successfully added response with response name ``{}`` to command ``{}`` Invoke this specific response with ``{}`` or get a random response from the list of responses for this command with ``{}``'.format(
                                                                    entry_response, entry_cmd,
                                                                    customcmd_prefix + entry_cmd + ' ' + entry_response,
                                                                    customcmd_prefix + entry_cmd))
                                            except Exception as e:

                                                json.dump(save, commands, indent=4)
                                                await menu.edit(content=
                                                                self.bot.bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)

                        # Add to existing list cmd
                        elif reply.content == '2':
                            list_cmds = []
                            with open('settings/commands.json') as commands:
                                cmds = json.load(commands)
                            for i in cmds:
                                if type(cmds[i]) is list:
                                    list_cmds.append(i)
                            msg = '1. '
                            count = 0
                            for count, word in enumerate(list_cmds):
                                msg += '{}  {}.'.format(word, count + 2)

                            msg = msg[:-(len(str(count + 2)) + 2)]
                            if count == 0:
                                return await menu.edit(content=
                                                       self.bot.bot_prefix + 'There are no cmds you can add multiple responses to. Create a cmd that enables multiple responses and then add a response to it.')
                            await menu.edit(content=
                                            self.bot.bot_prefix + '```\n\u2795 Enter the number of the cmd name to add a response to.\n\n {}```'.format(msg))

                            reply = await self.check(ctx, count + 2, pre)

                            if reply:
                                await reply.delete()
                                entry_cmd = list_cmds[int(reply.content) - 1]

                                await menu.edit(content=
                                                self.bot.bot_prefix + '```\n\u2795 Enter a response name.```')
                                reply = await self.check(ctx, 0, pre)

                                # Grab response name
                                if reply:
                                    await reply.delete()
                                    entry_response = reply.content
                                    await menu.edit(content=
                                                    self.bot.bot_prefix + '```\n\u2795 Now enter the response.```')
                                    reply = await self.check(ctx, 0, pre)

                                    # Grab the response
                                    if reply:
                                        try:
                                            await reply.delete()
                                        except:
                                            pass
                                        response = reply.content
                                        with open('settings/commands.json', 'r+') as commands:
                                            save = cmds
                                            commands.seek(0)
                                            commands.truncate()
                                            try:
                                                cmds[entry_cmd].append([entry_response, response])

                                                json.dump(cmds, commands, indent=4)
                                                await menu.edit(content=
                                                                self.bot.bot_prefix + 'Successfully added response with response name ``{}`` to command ``{}`` Invoke this specific response with ``{}`` or get a random response from the list of responses for this command with ``{}``'.format(
                                                                    entry_response, entry_cmd,
                                                                    customcmd_prefix + entry_cmd + ' ' + entry_response,
                                                                    customcmd_prefix + entry_cmd))
                                            except Exception as e:

                                                json.dump(save, commands, indent=4)
                                                await menu.edit(content=
                                                                self.bot.bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)

                elif reply.content == '3':
                    await menu.delete()
                    await self.customcommands(ctx)

        else:
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
                                return await ctx.send(self.bot.bot_prefix + 'Error, this is a list command. To append to this command, you need a <response name>. Ex: ``>add cmd response_name response``')
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
                                return await ctx.send(self.bot.bot_prefix + 'Error, this is a list command. To append to this command, you need a <response name>. Ex: ``>add cmd response_name response``')
                        cmds[entry[0]] = entry[1]

                await ctx.send(
                    self.bot.bot_prefix + 'Successfully added ``%s`` to ``%s``' % (entry[1], entry[0]))

            except Exception as e:
                with open('settings/commands.json', 'w') as commands:
                    commands.truncate()
                    json.dump(save, commands, indent=4)
                await ctx.send(self.bot.bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)

            # Update commands.json
            with open('settings/commands.json', 'w') as commands:
                commands.truncate()
                json.dump(cmds, commands, indent=4)

    # Remove a custom command
    @commands.command(pass_context=True)
    async def remove(self, ctx, *, msg: str = None):
        """Remove a customcmd. [p]help remove for more info.

        Simply do: [p]remove
        This will trigger the menu which you can navigate through and remove your custom command that way.

        -----------------------------------------------------------

        Legacy method:

        [p]remove <command> or [p]remove <command> <response_name> if you want to remove a specific response for a command.

        Just like with the add cmd, note that if anything you are adding/removing is more than one word, you must put each part in quotes.
        Example: If "cry" is the command and "mugi why" is the name for one of the links, removing that link would be: [p]remove "cry" "mugi why" """
        if not msg:

            await ctx.message.delete()
            pre = ctx.message.content.split('remove')[0]
            menu = await ctx.send(
                self.bot.bot_prefix + '```\n\u2796 Choose what to remove. Enter a number:\n\n1. A command and all its responses.\n2. A single response from a command that has more than one.```')

            reply = await self.check(ctx, 3, pre)

            if reply:

                await reply.delete()
                # Remove a cmd
                if reply.content == '1':
                    with open('settings/commands.json') as commands:
                        cmds = json.load(commands)
                    msg = '1. '
                    count = 0
                    all_cmds = []
                    for count, word in enumerate(cmds):
                        all_cmds.append(word)
                        msg += '{}  {}.'.format(word, count + 2)

                    msg = msg[:-(len(str(count + 2)) + 2)]
                    if count == 0:
                        return await menu.edit(content=
                                               self.bot.bot_prefix + 'There are no cmds to remove.')
                    await menu.edit(content=
                                    self.bot.bot_prefix + '```\n\u2796 Enter the number of the cmd to remove.\n\n {}```'.format(
                                        msg))

                    reply = await self.check(ctx, count + 2, pre)

                    if reply:
                        await reply.delete()
                        with open('settings/commands.json', 'r+') as commands:
                            save = cmds
                            commands.seek(0)
                            commands.truncate()
                            try:
                                cmd_to_remove = all_cmds[int(reply.content) - 1]
                                del cmds[cmd_to_remove]

                                json.dump(cmds, commands, indent=4)
                                await menu.edit(content=
                                                self.bot.bot_prefix + 'Successfully removed command ``{}``'.format(cmd_to_remove))
                            except Exception as e:

                                json.dump(save, commands, indent=4)
                                await menu.edit(content=
                                                self.bot.bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)

                # Remove a specific response from a cmd
                elif reply.content == '2':
                    list_cmds = []
                    with open('settings/commands.json') as commands:
                        cmds = json.load(commands)
                    for i in cmds:
                        if type(cmds[i]) is list:
                            list_cmds.append(i)
                    msg = '1. '
                    count = 0
                    for count, word in enumerate(list_cmds):
                        msg += '{}  {}.'.format(word, count + 2)

                    msg = msg[:-(len(str(count + 2)) + 2)]
                    if count == 0:
                        return await menu.edit(content=
                                               self.bot.bot_prefix + 'There are no cmds with multiple responses. If you are looking to remove a cmd with just one response, select 1 in the main menu for this command.')
                    await menu.edit(content=
                                    self.bot.bot_prefix + '```\n\u2796 Enter the number of the cmd that you want to remove a response from.\n\n {}```'.format(
                                        msg))

                    reply = await self.check(ctx, count + 2, pre)

                    # List responses from this cmd
                    if reply:
                        await reply.delete()
                        cmd_to_remove_from = list_cmds[int(reply.content) - 1]
                        cmd_responses = []
                        msg = '1. '
                        count = 0
                        for count, word in enumerate(cmds[cmd_to_remove_from]):
                            cmd_responses.append(word[0])
                            msg += '{}  {}.'.format(word[0], count + 2)

                        msg = msg[:-(len(str(count + 2)) + 2)]

                        await menu.edit(content=
                                        self.bot.bot_prefix + '```\n\u2796 Enter the number of the response to remove.\n\n {}```'.format(
                                            msg))

                        reply = await self.check(ctx, count + 2, pre)

                        if reply:
                            await reply.delete()
                            with open('settings/commands.json', 'r+') as commands:
                                save = cmds
                                commands.seek(0)
                                commands.truncate()
                                try:
                                    response_to_remove = cmd_responses[int(reply.content) - 1]
                                    for i in cmds[cmd_to_remove_from]:
                                        if i[0] == response_to_remove:
                                            cmds[cmd_to_remove_from].remove(i)
                                            if cmds[cmd_to_remove_from] == []:
                                                del cmds[cmd_to_remove_from]

                                    json.dump(cmds, commands, indent=4)
                                    await menu.edit(content=
                                                    self.bot.bot_prefix + 'Successfully removed response with name ``{}`` from command ``{}``'.format(
                                                        response_to_remove, cmd_to_remove_from))
                                except Exception as e:

                                    json.dump(save, commands, indent=4)
                                    await menu.edit(content=
                                                    self.bot.bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)






        else:

            words = msg.strip()

            with open('settings/commands.json', 'r') as commands:
                cmds = json.load(commands)
                save = cmds

            try:

                # If there are quotes in the message (meaning multiple words for each param)
                success = False

                def check(msg):
                    if ctx.message.author == msg.author:
                        if msg:
                            return msg.content.lower().strip() == 'y' or msg.content.lower().strip() == 'n'
                        else:
                            return False
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
                                    await ctx.send(
                                        self.bot.bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (
                                            entry[1], entry[0]))
                                    success = True
                        else:
                            if entry[0] in cmds:
                                del cmds[entry[0]]
                                success = True
                                await ctx.send(
                                    self.bot.bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (
                                        entry[1], entry[0]))

                    # Item for key is string
                    else:
                        if entry[0] in cmds:
                            if type(cmds[entry[0]]) is list:
                                await ctx.send(self.bot.bot_prefix + 'This will delete all responses for this list command. Are you sure you want to do this? (y/n).')
                                reply = await self.bot.wait_for("message", timeout=10, check=check)
                                if reply:
                                    if reply.content.lower().strip() == 'n':
                                        return await ctx.send(self.bot.bot_prefix + 'Cancelled.')
                                else:
                                    return await ctx.send(self.bot.bot_prefix + 'Cancelled.')
                            oldValue = cmds[entry[0]]
                            del cmds[entry[0]]
                            success = True
                            await ctx.send(
                                self.bot.bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

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
                                    await ctx.send(
                                        self.bot.bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (
                                            entry[1], entry[0]))
                                    success = True
                        else:
                            if entry[0] in cmds:
                                del cmds[entry[0]]
                                success = True
                                await ctx.send(
                                    self.bot.bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (entry[1], entry[0]))

                    # Item for key is string
                    else:
                        entry = words.split(' ', 1)
                        if entry[0] in cmds:
                            if type(cmds[entry[0]]) is list:
                                await ctx.send(self.bot.bot_prefix + 'This will delete all responses for this list command. Are you sure you want to do this? (y/n).')
                                reply = await self.bot.wait_for("message", timeout=10, check=check)
                                if reply:
                                    if reply.content.lower().strip() == 'n':
                                        return await ctx.send(self.bot.bot_prefix + 'Cancelled.')
                                else:
                                    return await ctx.send(self.bot.bot_prefix + 'Cancelled.')
                            oldValue = cmds[entry[0]]
                            del cmds[entry[0]]
                            success = True
                            await ctx.send(
                                self.bot.bot_prefix + 'Successfully removed ``%s`` from ``%s``' % (oldValue, entry[0]))

                if success is False:
                    await ctx.send(self.bot.bot_prefix + 'Could not find specified command.')

            except Exception as e:
                with open('settings/commands.json', 'w') as commands:
                    commands.truncate()
                    json.dump(save, commands, indent=4)
                await ctx.send(self.bot.bot_prefix + 'Error, something went wrong. Exception: ``%s``' % e)

            # Update commands.json
            with open('settings/commands.json', 'w') as commands:
                commands.truncate()
                json.dump(cmds, commands, indent=4)


def setup(bot):
    bot.add_cog(Customcmds(bot))