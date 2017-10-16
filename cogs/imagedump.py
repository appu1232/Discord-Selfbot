import datetime
import asyncio
import re
import sys
import subprocess
import json
import time
import os
from datetime import datetime
from discord.ext import commands
from cogs.utils.checks import cmd_prefix_len

'''Module for miscellaneous commands'''


class Imagedump:

    def __init__(self, bot):
        self.bot = bot

    def check_images(self, message, images, type_of_items):
        if message.attachments:
            yield from (item.url for item in message.attachments if item.url != '' and item.url not in images
                        for i in type_of_items if item.url.lower().endswith(i.strip()))

        if message.embeds:
            for embed in message.embeds:
                data = embed.to_dict()
                try:
                    url = data['image']['url']
                except KeyError:
                    try:
                        url = data['thumbnail']['url']
                    except KeyError:
                        continue

                if (url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webm'))
                        or data['type'] in {'jpg', 'jpeg', 'png', 'gif', 'gifv', 'webm', 'image'}) and url not in images:
                    for i in type_of_items:
                        if url.lower().endswith(i.strip()):
                            yield url

        urls = []
        try:
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
        except:
            pass

        if urls is not []:
            yield from (url for url in urls
                        if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.gifv', '.webm')) and url not in images
                        for i in type_of_items if url.lower().endswith(i.strip()))

    @commands.group(pass_context=True)
    async def imagedump(self, ctx):
        """Mass downloads images from a channel. [p]help imagedump for info.
        ----Simple----
        [p]imagedump <n> - checks the last <n> messages in this chat and downloads all the images/gifs/webms found.
        
        ----More options----
        Example: I want a new wallpaper. I'll check the last 5000 messages in this channel and download 100 items with type .png that fit on my 16:9 monitor with dimensions 1920x1080. This is what I would do:

        [p]imagedump 5000 | items=100 | type=png | ratio=16:9 | dim=1920x1080

        ----

        General Syntax (only include the options you want):
        [p]imagedump <n> | items=<m> | before=YYYY-MM-DD | after=YYYY-MM-DD | dim=WidthxHeight | ratio=Width:Height | type=<type_of_item> | channel=<id> | user=<id> - add any one or more of these to the command to furthur specify your requirements to find items.
        
        - items=<m> - when checking the last <n> messages, only download <m> items max.
        
        - before=YYYY-MM-DD - check <n> messages before this date. Ex: before=2017-02-16
        
        - after=YYYY-MM-DD - check <n> messages after this date.
        
        - dim=WidthxHeight - only download items with these dimensions. Ex: dim=1920x1080 Optionally, do dim>=WidthxHeight for images greater than or equal and dim<=WidthxHeight for less than or equal to these dimensions.
        
        - ratio=Width:Height - only download items with these ratios. Ex: ratio=16:9
        
        - type=<type_of_item> - only download these types of files. Ex: type=png or type=gif, webm All options: jpg, png, gif (includes gifv), webm.
        
        - channel=<id> - download from a different channel (can be a from a different server). Enable developer mode, right click on the channel name, and hit copy id to get the id. Ex: channel=299293492645986307
        
        - user=<id> - download only items posted by this user. Enable developer mode, right click on user, copy id to get their id. Ex: user=124910128582361092
        
        """

        if ctx.invoked_subcommand is None:
            pre = cmd_prefix_len()
            error = 'Invalid syntax. ``>imagedump <n>`` where n is the number of messages to search in this channel. Ex: ``>imagedump 100``\n``>imagedump dir path/to/directory`` if you want to change where images are saved.'
            if ctx.message.content[9 + pre:].strip():
                finished_dls = os.listdir('cogs/utils/')
                finished = []
                for i in finished_dls:
                    if i.startswith('finished'):
                        finished.append(i)
                for i in finished:
                    os.remove('cogs/utils/{}'.format(i))
                if ctx.message.content[pre + 10] == 's':
                    silent = True
                    msg = ctx.message.content[11 + pre:].strip()
                else:
                    silent = False
                    msg = ctx.message.content[9 + pre:].strip()
                before = after = limit_images = user = None
                type_of_items = ['jpg', 'jpeg', 'png', 'gif', 'gifv', 'webm']
                x = y = dimx = dimy = 'None'
                fixed = 'no'

                before_msg = after_msg = limit_images_msg = type_of_items_msg = dimensions_msg = ratio_msg = channel_msg = user_msg = ''

                simple = True
                channel = ctx.message.channel
                if ' | ' not in msg:
                    if msg.isdigit():
                        limit = int(msg) + 1
                    else:
                        return await ctx.send(self.bot.bot_prefix + error)
                else:
                    simple = False
                    msg = msg.split(' | ')
                    if msg[0].strip().isdigit():
                        limit = int(msg[0].strip()) + 1
                    else:
                        return await ctx.send(self.bot.bot_prefix + error)
                    for i in msg:
                        if i.strip().lower().startswith('items='):
                            limit_images = i.strip()[6:].strip()
                            if limit_images.isdigit():
                                limit_images_msg = 'Up to {} items. '.format(limit_images)
                                limit_images = int(limit_images)
                            else:
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``items=`` should be the number of images. Ex: ``>imagedump 500 | items=10``')
                        if i.strip().lower().startswith('dim='):
                            dimensions = i.strip()[4:].strip()
                            if 'x' not in dimensions:
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``dim=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim=1920x1080``')
                            x, y = dimensions.split('x')
                            if not x.strip().isdigit() or not y.strip().isdigit():
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``dim=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim=1920x1080``')
                            else:
                                x, y = x.strip(), y.strip()
                                fixed = 'yes'
                                dimensions_msg = 'Dimensions: {}. '.format(dimensions)

                        if i.strip().lower().startswith('dim>='):
                            dimensions = i.strip()[5:].strip()
                            if 'x' not in dimensions:
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``dim>=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim>=1920x1080``')
                            x, y = dimensions.split('x')
                            if not x.strip().isdigit() or not y.strip().isdigit():
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``dim>=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim>=1920x1080``')
                            else:
                                x, y = x.strip(), y.strip()
                                fixed = 'more'
                                dimensions_msg = 'Dimensions: {} or larger. '.format(dimensions)

                        if i.strip().lower().startswith('dim<='):
                            dimensions = i.strip()[5:].strip()
                            if 'x' not in dimensions:
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``dim<=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim<=1920x1080``')
                            x, y = dimensions.split('x')
                            if not x.strip().isdigit() or not y.strip().isdigit():
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``dim<=`` should be the dimensions of the image in the form WidthxHeight. Ex: ``>imagedump 500 | dim<=1920x1080``')
                            else:
                                x, y = x.strip(), y.strip()
                                fixed = 'less'
                                dimensions_msg = 'Dimensions: {} or smaller. '.format(dimensions)

                        if i.strip().lower().startswith('ratio='):
                            ratio = i.strip()[6:].strip()
                            if ':' not in ratio:
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``ratio=`` should be the ratio of the image in the form w:h. Ex: ``>imagedump 500 | ratio=16:9``')
                            dimx, dimy = ratio.split(':')
                            if not dimx.strip().isdigit() or not dimy.strip().isdigit():
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``ratio=`` should be the ratio of the image in the form w:h. Ex: ``>imagedump 500 | ratio=16:9``')
                            else:
                                dimx, dimy = dimx.strip(), dimy.strip()
                                ratio_msg = 'Ratio: {}.'.format(ratio)

                        if i.strip().lower().startswith('before='):
                            try:
                                date = i.strip()[7:].strip()
                                before = datetime.strptime(date, '%Y-%m-%d')
                                before_msg = 'Before: {} '.format(date)
                            except:
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``before=`` should be a date in the format YYYY-MM-DD. Ex: ``>imagedump 500 | before=2017-02-15``')

                        if i.strip().lower().startswith('after='):
                            try:
                                date = i.strip()[6:].strip()
                                after = datetime.strptime(date, '%Y-%m-%d')
                                after_msg = 'After: {} '.format(date)
                            except:
                                return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``after=`` should be a date in the format YYYY-MM-DD. Ex: ``>imagedump 500 | after=2017-02-15``')

                        if i.strip().lower().startswith('type='):
                            type = i.strip()[5:].strip()
                            if ',' in type:
                                type_of_items = type.split(',')
                            else:
                                type_of_items = [type]
                            for i in type_of_items:
                                if 'png' in i or 'jpg' in i or 'gif' in i or 'webm' in i:
                                    pass
                                else:
                                    return await ctx.send(self.bot.bot_prefix + 'Invalid Syntax. ``type=`` should be tye type(s) of items to download. Ex: ``>imagedump 500 | type=png`` or ``>imagedump 500 | type=png, gif``')
                            if 'jpg' in type_of_items or '.jpg' in type_of_items:
                                type_of_items.append('.jpeg')
                            type_of_items_msg = 'Types: {} '.format(type)

                        if i.strip().lower().startswith('channel='):
                            channel = i.strip()[8:].strip()
                            channel = self.bot.get_channel(int(channel))
                            if not channel:
                                return await ctx.send(self.bot.bot_prefix + 'Channel not found. Are you using the right syntax? ``channel=`` should be the channel id. '
                                                                                                     'Ex: ``>imagedump 500 | channel=299431230984683520``')
                            channel_msg = 'Channel: {} '.format(channel.name)

                        if i.strip().lower().startswith('user='):
                            user_id = i.strip()[5:].strip()
                            for j in self.bot.guilds:
                                user = j.get_member(int(user_id))
                                if user:
                                    break
                            if not user:
                                return await ctx.send(self.bot.bot_prefix + 'User not found. Are you using the right syntax? ``user=`` should be the user\'s id. '
                                                                                                     'Ex: ``>imagedump 500 | user=124910128582361092``')
                            user_msg = 'User: {}'.format(user.name)

                await ctx.message.delete()
                with open('settings/optional_config.json', 'r+') as fp:
                    opt = json.load(fp)
                    if 'image_dump_delay' not in opt:
                        opt['image_dump_delay'] = "0"
                    fp.seek(0)
                    fp.truncate()
                    json.dump(opt, fp, indent=4)
                if 'image_dump_location' not in opt:
                    path = ''
                else:
                    path = opt['image_dump_location']
                if not os.path.exists('{}image_dump'.format(path)):
                    os.makedirs('{}image_dump'.format(path))
                try:
                    new_dump = time.strftime("%Y-%m-%dT%H_%M_%S_") + channel.name + '_' + channel.guild.name
                except:
                    new_dump = time.strftime("%Y-%m-%dT%H_%M_%S_")
                new_dump = "".join([x if x.isalnum() else "_" for x in new_dump])
                new_dump.replace('/', '_')
                os.makedirs('{}image_dump/{}'.format(path, new_dump))
                if not silent:
                    which_channel = 'in this channel...'
                    if ctx.message.channel != channel:
                        which_channel = 'in channel ``{}``'.format(channel.name)
                    if not simple:
                        params = 'Parameters: ``{}{}{}{}{}{}{}{}``'.format(limit_images_msg, before_msg, after_msg, dimensions_msg, ratio_msg, type_of_items_msg, channel_msg, user_msg)
                    else:
                        params = ''
                    await ctx.send(self.bot.bot_prefix + 'Downloading all images/gifs/webms from the last {} messages {}\nSaving to ``image_dump/{}`` Check console for progress.\n{}'.format(str(limit-1), which_channel, new_dump, params))
                start = time.time()
                images = []
                if limit > 100000:
                    print('Fetching last %s messages (this may take a few minutes)...' % str(limit - 1))
                else:
                    print('Fetching last %s messages...' % str(limit-1))
                async for message in channel.history(limit=limit, before=before, after=after):
                    if message.author == user or not user:
                        for url in self.check_images(message, images, type_of_items):
                            if url:
                                images.append(url)

                            if len(images) == limit_images:
                                break

                with open('cogs/utils/urls{}.txt'.format(new_dump), 'w') as fp:
                    for url in images:
                        fp.write(url + '\n')

                args = [sys.executable, 'cogs/utils/image_dump.py', path, new_dump, opt['image_dump_delay'], x, y, dimx, dimy, fixed]
                p = subprocess.Popen(args)
                self.bot.imagedumps.append(p)

                while p.poll() is None:
                    await asyncio.sleep(1)

                if os.path.exists('cogs/utils/paused{}.txt'.format(new_dump)):
                    return

                try:
                    with open('cogs/utils/finished{}.txt'.format(new_dump), 'r') as fp:
                        stop = float(fp.readline())
                        total = fp.readline()
                        failures = fp.readline()
                        size = fp.readline()
                except:
                    return print('Something went wrong when saving items and the download was stopped. Error posted above.')
                try:
                    os.remove('cogs/utils/finished{}.txt'.format(new_dump))
                except:
                    pass
                if int(failures) != 0:
                    if not silent:
                        await ctx.send(self.bot.bot_prefix + 'Done! ``{}`` items downloaded. ``{}`` However, ``{}`` items failed to download. Check your console for more info on which ones were missed. '
                                                                                      'Finished in: ``{} seconds.``'.format(str(total), size, str(failures), str(round(stop - start, 2))))
                    else:
                        print('{} items failed to download. See above for missed links. '
                              'Finished in: {} seconds.'.format(str(failures), str(round(stop - start, 2))))
                else:
                    if not silent:
                        await ctx.send(self.bot.bot_prefix + 'Done! ``{}`` items downloaded. ``{}`` Finished in: ``{} seconds.``'.format(str(total), size, str(round(stop-start, 2))))
                    else:
                        print('Finished in: {} seconds'.format(str(round(stop-start, 2))))
            else:
                await ctx.send(self.bot.bot_prefix + 'Invalid syntax. ``>imagedump <n>`` where n is the number of messages to search in this channel. '
                                                                              'Ex: ``>imagedump 100``\n``>imagedump dir path/to/directory`` if you want to change where images are saved.')

    @imagedump.command(pass_context=True)
    async def dir(self, ctx, *, msg: str = None):
        """Set directory to save to. Ex: [p]imagedump dir C:/Users/Bill/Desktop"""
        if msg:
            msg = msg.strip() if msg.strip().endswith('/') else msg.strip() + '/'
            if os.path.exists(msg):
                if not os.path.exists('{}image_dump'.format(msg)):
                    os.makedirs('{}image_dump'.format(msg))
                with open('settings/optional_config.json', 'r+') as fp:
                    opt = json.load(fp)
                    opt['image_dump_location'] = msg
                    fp.seek(0)
                    fp.truncate()
                    json.dump(opt, fp, indent=4)
                await ctx.send(self.bot.bot_prefix + 'Successfully set path. Images will be saved to: ``{}image_dump/``'.format(msg))
            else:
                await ctx.send(self.bot.bot_prefix + 'Invalid path. Try again. Example: ``>imagedump dir C:/Users/Bill/Desktop``')
        else:
            with open('settings/optional_config.json', 'r') as fp:
                opt = json.load(fp)
                if 'image_dump_location' not in opt:
                    path = os.path.abspath("settings")[:-8] + 'image_dump'
                else:
                    path = opt['image_dump_location'] + 'image_dump'
            await ctx.send(self.bot.bot_prefix + 'Current imagedump download location: ``{}``'.format(path.replace('\\', '/')))

    @imagedump.command(pass_context=True, aliases=['stop'])
    async def cancel(self, ctx):
        """Cancel ongoing imagedump downloads."""
        for i in self.bot.imagedumps:
            i.kill()
        self.bot.imagedumps = []
        if os.path.exists('pause.txt'):
            os.remove('pause.txt')
            paused_dls = os.listdir('cogs/utils/')
            for i in paused_dls:
                if i.startswith('paused') or i.startswith('urls'):
                    os.remove('cogs/utils/{}'.format(i))
        await ctx.send(self.bot.bot_prefix + 'Cancelled all imagedump processes currently running.')
        print('\nImagedump forcibily cancelled.')

    @imagedump.command(pass_context=True)
    async def pause(self, ctx):
        """Pause ongoing imagedump downloads."""
        for i in self.bot.imagedumps:
            if i.poll() is not None:
                pass
            else:
                open('pause.txt', 'a').close()
                self.bot.imagedumps = []
                return await ctx.send(self.bot.bot_prefix + 'Paused download. ``>imagedump resume`` to resume. Imagedumps can be resumed even after a restart.')
        return await ctx.send(self.bot.bot_prefix + 'No imagedumps processes are running currently.')

    @imagedump.command(pass_context=True, aliases=['unpause'])
    async def resume(self, ctx):
        """Resume paused imagedump downloads. (you can resume even after restart)"""
        if os.path.exists('pause.txt'):
            os.remove('pause.txt')
            paused_dls = os.listdir('cogs/utils/')
            proc = []
            for i in paused_dls:
                if i.startswith('paused'):
                    proc.append(i)
            for i in proc:
                with open('cogs/utils/{}'.format(i), 'r') as fp:
                    fp.readline()
                    path = fp.readline().strip()
                    new_dump = fp.readline().strip()
                    delay = fp.readline().strip()
                    x = fp.readline().strip()
                    y = fp.readline().strip()
                    dimx = fp.readline().strip()
                    dimy = fp.readline().strip()
                    fixed = fp.readline().strip()
                os.remove('cogs/utils/{}'.format(i))

                args = [sys.executable, 'cogs/utils/image_dump.py', path, new_dump, delay, x, y, dimx, dimy, fixed]
                print('\nResuming...')
                p = subprocess.Popen(args)
                self.bot.imagedumps.append(p)

            await ctx.send(self.bot.bot_prefix + 'Resumed imagedump. Check console for progress.')

        else:
            await ctx.send(self.bot.bot_prefix + 'No imagedump processes are paused.')


def setup(bot):
    bot.add_cog(Imagedump(bot))
