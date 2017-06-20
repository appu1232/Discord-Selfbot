import random
import re
from appuselfbot import bot_prefix
from discord.ext import commands
from cogs.utils.checks import *
from pyfiglet import figlet_format

'''Module for fun/meme commands commands'''


class Fun:
    def __init__(self, bot):
        self.bot = bot
        self.regionals = {'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
                          'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
                          'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}', 'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
                          'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
                          'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
                          'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
                          'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}', 'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
                          'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
                          'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
                          'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
                          'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}', 'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
                          'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
                          's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
                          'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
                          'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}', 'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}',
                          'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
                          'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}',
                          '0': '0⃣', '1': '1⃣', '2': '2⃣', '3': '3⃣',
                          '4': '4⃣', '5': '5⃣', '6': '6⃣', '7': '7⃣', '8': '8⃣', '9': '9⃣', '!': '\u2757',
                          '?': '\u2753'}
        self.emoji_reg = re.compile(r'<:.+?:([0-9]{15,21})>')
        self.ball = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                     'Reply hazy try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']

    emoji_dict = {
    # these arrays are in order of "most desirable". Put emojis that most convincingly correspond to their letter near the front of each array.
        'a': ['🇦', '🅰', '🍙', '🔼', '4⃣'],
        'b': ['🇧', '🅱', '8⃣'],
        'c': ['🇨', '©', '🗜'],
        'd': ['🇩', '↩'],
        'e': ['🇪', '3⃣', '📧', '💶'],
        'f': ['🇫', '🎏'],
        'g': ['🇬', '🗜', '6⃣', '9⃣', '⛽'],
        'h': ['🇭', '♓'],
        'i': ['🇮', 'ℹ', '🚹', '1⃣'],
        'j': ['🇯', '🗾'],
        'k': ['🇰', '🎋'],
        'l': ['🇱', '1⃣', '🇮', '👢', '💷'],
        'm': ['🇲', 'Ⓜ', '📉'],
        'n': ['🇳', '♑', '🎵'],
        'o': ['🇴', '🅾', '0⃣', '⭕', '🔘', '⏺', '⚪', '⚫', '🔵', '🔴', '💫'],
        'p': ['🇵', '🅿'],
        'q': ['🇶', '♌'],
        'r': ['🇷', '®'],
        's': ['🇸', '💲', '5⃣', '⚡', '💰', '💵'],
        't': ['🇹', '✝', '➕', '🎚', '🌴', '7⃣'],
        'u': ['🇺', '⛎', '🐉'],
        'v': ['🇻', '♈', '☑'],
        'w': ['🇼', '〰', '📈'],
        'x': ['🇽', '❎', '✖', '❌', '⚒'],
        'y': ['🇾', '✌', '💴'],
        'z': ['🇿', '2⃣'],
        '0': ['0⃣', '🅾', '0⃣', '⭕', '🔘', '⏺', '⚪', '⚫', '🔵', '🔴', '💫'],
        '1': ['1⃣', '🇮'],
        '2': ['2⃣', '🇿'],
        '3': ['3⃣'],
        '4': ['4⃣'],
        '5': ['5⃣', '🇸', '💲', '⚡'],
        '6': ['6⃣'],
        '7': ['7⃣'],
        '8': ['8⃣', '🎱', '🇧', '🅱'],
        '9': ['9⃣'],
        '?': ['❓'],
        '!': ['❗', '❕', '⚠', '❣'],

        # emojis that contain more than one letter can also help us react
        # letters that we are trying to replace go in front, emoji to use second
        #
        # if there is any overlap between characters that could be replaced,
        # e.g. 💯 vs 🔟, both could replace "10",
        # the longest ones & most desirable ones should go at the top
        # else you'll have "100" -> "🔟0" instead of "100" -> "💯".
        'combination': [['cool', '🆒'],
                        ['back', '🔙'],
                        ['soon', '🔜'],
                        ['free', '🆓'],
                        ['end', '🔚'],
                        ['top', '🔝'],
                        ['abc', '🔤'],
                        ['atm', '🏧'],
                        ['new', '🆕'],
                        ['sos', '🆘'],
                        ['100', '💯'],
                        ['loo', '💯'],
                        ['zzz', '💤'],
                        ['...', '💬'],
                        ['ng', '🆖'],
                        ['id', '🆔'],
                        ['vs', '🆚'],
                        ['wc', '🚾'],
                        ['ab', '🆎'],
                        ['cl', '🆑'],
                        ['ok', '🆗'],
                        ['up', '🆙'],
                        ['10', '🔟'],
                        ['11', '⏸'],
                        ['ll', '⏸'],
                        ['ii', '⏸'],
                        ['tm', '™'],
                        ['on', '🔛'],
                        ['oo', '🈁'],
                        ['!?', '⁉'],
                        ['!!', '‼'],
                        ['21', '📅'],
                        ]
    }

    # used in textflip
    text_flip = {}
    char_list = "abcdefghijklmnpqrtuvwxyzABCDEFGHIJKLMNPQRTUVWYZ12345679!&*(),.'"
    alt_char_list = "ɐqɔpǝɟƃɥᴉɾʞlɯudbɹʇnʌʍxʎz∀qƆpƎℲפHIſʞ˥WNԀQɹ┴∩ΛM⅄ZƖᄅƐㄣϛ9ㄥ6¡⅋*)('˙,"
    for idx, char in enumerate(char_list):
        text_flip[char] = alt_char_list[idx]


    # used in >react, checks if it's possible to react with the duper string or not
    def has_dupe(duper):
        collect_my_duper = list(filter(lambda x: x != '<' and x != '⃣',
                                       duper))  # remove < because those are used to denote a written out emoji, and there might be more than one of those requested that are not necessarily the same one.  ⃣ appears twice in the number unicode thing, so that must be stripped too...
        return len(set(collect_my_duper)) != len(collect_my_duper)

    # used in >react, replaces e.g. 'ng' with '🆖'
    def replace_combos(react_me):
        for combo in Fun.emoji_dict['combination']:
            if combo[0] in react_me:
                react_me = react_me.replace(combo[0], combo[1], 1)
        return react_me

    # used in >react, replaces e.g. 'aaaa' with '🇦🅰🍙🔼'
    def replace_letters(react_me):
        for char in "abcdefghijklmnopqrstuvwxyz0123456789!?":
            char_count = react_me.count(char)
            if char_count > 1:  # there's a duplicate of this letter:
                if len(Fun.emoji_dict[
                           char]) >= char_count:  # if we have enough different ways to say the letter to complete the emoji chain
                    i = 0
                    while i < char_count:  # moving goal post necessitates while loop instead of for
                        if Fun.emoji_dict[char][i] not in react_me:
                            react_me = react_me.replace(char, Fun.emoji_dict[char][i], 1)
                        else:
                            char_count += 1  # skip this one because it's already been used by another replacement (e.g. circle emoji used to replace O already, then want to replace 0)
                        i += 1
            else:
                if char_count == 1:
                    react_me = react_me.replace(char, Fun.emoji_dict[char][0])
        return react_me

    @commands.command(pass_context=True, aliases=['8ball'])
    async def ball8(self, ctx, *, msg: str):
        """Let the 8ball decide your fate. Ex: >8ball Will I get good?"""
        answer = random.randint(0, 19)
        if embed_perms(ctx.message):
            if answer < 10:
                color = 0x008000
            elif 10 <= answer < 15:
                color = 0xFFD700
            else:
                color = 0xFF0000
            em = discord.Embed(color=color)
            em.add_field(name='\u2753 Question', value=msg)
            em.add_field(name='\ud83c\udfb1 8ball', value=self.ball[answer], inline=False)
            await self.bot.send_message(ctx.message.channel, content=None, embed=em)
            await self.bot.delete_message(ctx.message)
        else:
            await self.bot.send_message(ctx.message.channel, '\ud83c\udfb1 ``{}``'.format(random.choice(self.ball)))

    @commands.command(pass_context=True, aliases=['pick'])
    async def choose(self, ctx, *, choices: str):
        """Choose randomly from the options you give. >choose this | that"""
        await self.bot.send_message(ctx.message.channel,
                                    bot_prefix + 'I choose: ``{}``'.format(random.choice(choices.split("|"))))

    @commands.command(pass_context=True)
    async def l2g(self, ctx, *, msg: str):
        """Creates a lmgtfy link. Ex: >l2g how do i become cool."""
        lmgtfy = 'http://lmgtfy.com/?q='
        await self.bot.send_message(ctx.message.channel, bot_prefix + lmgtfy + msg.lower().strip().replace(' ', '+'))
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True)
    async def vowelreplace(self, ctx, *, msg: str):
        """Replaces all vowels in a word with a letter"""
        word = msg.split(" ")[0]
        letter = msg.split(" ")[1]
        for ch in ['a', 'e', 'i', 'o', 'u']:
            if ch in word:
                word = word.replace(ch, letter)
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(ctx.message.channel, word)

    @commands.group(pass_context=True)
    async def ascii(self, ctx):
        """Convert text to ascii art. Ex: >ascii stuff >help ascii for more info."""
        if ctx.invoked_subcommand is None:
            pre = cmd_prefix_len()
            if ctx.message.content[pre + 5:]:
                with open('settings/optional_config.json', 'r+') as fp:
                    opt = json.load(fp)
                msg = str(figlet_format(ctx.message.content[pre + 5:].strip(), font=opt['ascii_font']))
                if len(msg) > 2000:
                    await self.bot.send_message(ctx.message.channel, bot_prefix + 'Message too long, rip.')
                else:
                    await self.bot.delete_message(ctx.message)
                    await self.bot.send_message(ctx.message.channel, bot_prefix + '```{}```'.format(msg))
            else:
                await self.bot.send_message(ctx.message.channel,
                                            bot_prefix + 'Please input text to convert to ascii art. Ex: ``>ascii stuff``')

    @ascii.command(pass_context=True)
    async def font(self, ctx, *, txt: str):
        """Change font for ascii. All fonts: http://www.figlet.org/examples.html for all fonts."""
        try:
            str(figlet_format('test', font=txt))
        except:
            return await self.bot.send_message(ctx.message.channel, bot_prefix + 'Invalid font type.')
        with open('settings/optional_config.json', 'r+') as fp:
            opt = json.load(fp)
            opt['ascii_font'] = txt
            fp.seek(0)
            fp.truncate()
            json.dump(opt, fp, indent=4)
        await self.bot.send_message(ctx.message.channel, bot_prefix + 'Successfully set ascii font.')

    @commands.command(pass_context=True)
    async def dice(self, ctx, *, txt: str = None):
        """Roll dice. Optionally input # of dice and # of sides. Ex: >dice 5 12"""
        await self.bot.delete_message(ctx.message)
        dice = 1
        sides = 6
        invalid = 'Invalid syntax. Ex: `>dice 4` - roll four normal dice. `>dice 4 12` - roll four 12 sided dice.'
        if txt:
            if ' ' in txt:
                dice, sides = txt.split(' ')
                try:
                    dice = int(dice)
                    sides = int(sides)
                except:
                    return await self.bot.send_message(ctx.message.channel, bot_prefix + invalid)
            else:
                try:
                    dice = int(txt)
                except:
                    return await self.bot.send_message(ctx.message.channel, bot_prefix + invalid)
        dice_rolls = []
        dice_roll_ints = []
        for roll in range(dice):
            result = random.randint(1, sides)
            dice_rolls.append(str(result))
            dice_roll_ints.append(result)
        embed = discord.Embed(title="Dice rolls:", description=' '.join(dice_rolls))
        embed.add_field(name="Total:", value=sum(dice_roll_ints))
        await self.bot.send_message(ctx.message.channel, "", embed=embed)

    @commands.command(pass_context=True)
    async def textflip(self, ctx, *, msg):
        """Flip given text."""
        result = ""
        for char in msg:
            if char in self.text_flip:
                result += self.text_flip[char]
            else:
                result += char
        await self.bot.edit_message(ctx.message, result[::-1])  # slice reverses the string

    @commands.command(pass_context=True)
    async def regional(self, ctx, *, msg):
        """Replace letters with regional indicator emojis"""
        await self.bot.delete_message(ctx.message)
        msg = list(msg)
        regional_list = [self.regionals[x.lower()] if x.isalnum() or x == '!' or x == '?' else x for x in msg]
        regional_output = '  '.join(regional_list)
        await self.bot.send_message(ctx.message.channel, regional_output)

    @commands.command(pass_context=True)
    async def space(self, ctx, *, msg):
        """Add n spaces between each letter. Ex: >space 2 thicc"""
        await self.bot.delete_message(ctx.message)
        if msg.split(' ', 1)[0].isdigit():
            spaces = int(msg.split(' ', 1)[0]) * ' '
            msg = msg.split(' ', 1)[1].strip()
        else:
            spaces = ' '
        spaced_message = '{}'.format(spaces).join(list(msg))
        await self.bot.send_message(ctx.message.channel, spaced_message)

    # given String react_me, return a list of emojis that can construct the string with no duplicates (for the purpose of reacting)
    # TODO make it consider reactions already applied to the message
    @commands.command(pass_context=True, aliases=['r'])
    async def react(self, ctx, msg: str, channel="current", msg_id="last", prefer_combine: bool = False):
        """Add letter(s) as reaction to previous message. Ex: >react hot"""
        await self.bot.delete_message(ctx.message)
        msg = msg.lower()

        msg_id = None if msg_id == "last" or msg_id == "0" or msg_id == "1" else int(msg_id)

        limit = 25 if msg_id else 1

        reactions = []
        non_unicode_emoji_list = []
        react_me = ""  # this is the string that will hold all our unicode converted characters from msg

        # replace all custom server emoji <:emoji:123456789> with "<" and add emoji ids to non_unicode_emoji_list
        char_index = 0
        while char_index < len(msg):
            react_me += msg[char_index]
            if msg[char_index] == '<':
                if (char_index != len(msg) - 1) and msg[char_index + 1] == ":":
                    name_end_colon = msg[char_index + 2:].index(':') + char_index
                    id_end = msg[name_end_colon + 2:].index('>') + name_end_colon
                    non_unicode_emoji_list.append(
                        msg[name_end_colon + 3:id_end + 2])  # we add the custom emoji to the list to replace '<' later
                    char_index = id_end + 2  # jump ahead in react_me parse
                else:
                    raise Exception("Can't react with '<'")
            char_index += 1
        if Fun.has_dupe(non_unicode_emoji_list):
            raise Exception(
                "You requested that I react with at least two of the exact same specific emoji. I'll try to find alternatives for alphanumeric text, but if you specify a specific emoji must be used, I can't help.")

        react_me_original = react_me  # we'll go back to this version of react_me if prefer_combine is false but we can't make the reaction happen unless we combine anyway.

        if Fun.has_dupe(react_me):  # there's a duplicate letter somewhere, so let's go ahead try to fix it.
            if prefer_combine:  # we want a smaller reaction string, so we'll try to combine anything we can right away
                react_me = Fun.replace_combos(react_me)
            react_me = Fun.replace_letters(react_me)

            if Fun.has_dupe(react_me):  # check if we were able to solve the dupe
                if not prefer_combine:  # we wanted the most legible reaction string possible, even if it was longer, but unfortunately that's not possible, so we're going to combine first anyway
                    react_me = react_me_original
                    react_me = Fun.replace_combos(react_me)
                    react_me = Fun.replace_letters(react_me)
                    if Fun.has_dupe(react_me):  # this failed too, so there's really nothing we can do anymore.
                        raise Exception("Tried a lot to get rid of the dupe, but couldn't. react_me: " + react_me)
                else:
                    raise Exception("Tried a lot to get rid of the dupe, but couldn't. react_me: " + react_me)

            lt_count = 0
            for char in react_me:
                if char != "<":
                    if char not in "0123456789":  # these unicode characters are weird and actually more than one character.
                        if char != '⃣':  # </3
                            reactions.append(char)
                    else:
                        reactions.append(self.emoji_dict[char][0])
                else:
                    reactions.append(discord.utils.get(self.bot.get_all_emojis(), id=non_unicode_emoji_list[lt_count]))
                    lt_count += 1
        else:  # probably doesn't matter, but by treating the case without dupes seperately, we can save some time
            lt_count = 0
            for char in react_me:
                if char != "<":
                    if char in "abcdefghijklmnopqrstuvwxyz0123456789!?":
                        reactions.append(self.emoji_dict[char][0])
                    else:
                        reactions.append(char)
                else:
                    reactions.append(discord.utils.get(self.bot.get_all_emojis(), id=non_unicode_emoji_list[lt_count]))
                    lt_count += 1

        if channel == "current":
            async for message in self.bot.logs_from(ctx.message.channel, limit=limit):
                if (not msg_id and message.id != ctx.message.id) or (str(msg_id) == message.id):
                    for i in reactions:
                        await self.bot.add_reaction(message, i)
        else:
            if channel.startswith("<#") and channel.endswith(">"):
                found_channel = discord.utils.get(ctx.message.server.channels, id=channel.replace("<", "").replace(">", "").replace("#", ""))
            else:
                found_channel = discord.utils.get(ctx.message.server.channels, name=channel)
            if found_channel:
                async for message in self.bot.logs_from(found_channel, limit=limit):
                    if (not msg_id and message.id != ctx.message.id) or (str(msg_id) == message.id):
                        for i in reactions:
                            await self.bot.add_reaction(message, i)
            else:
                async for message in self.bot.logs_from(ctx.message.channel, limit=limit):
                    if (not msg_id and message.id != ctx.message.id) or (str(msg_id) == message.id):
                        for i in reactions:
                            await self.bot.add_reaction(message, i)


def setup(bot):
    bot.add_cog(Fun(bot))