from discord.ext import commands
from appuselfbot import isBot
import enchant


class Spellcheck:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def s(self, ctx):
        dict = enchant.Dict('en_US')
        if ctx.message.content[2:].strip():
            if dict.check(ctx.message.content[2:].strip()) is False:
                await self.bot.send_message(ctx.message.channel, isBot + ':x: Correct spelling: %s' % (dict.suggest(ctx.message.content[2:].strip())[0]))
            else:
                await self.bot.send_message(ctx.message.channel, isBot + ':white_check_mark:')
        else:
            check_msg = self.bot.self_log[len(self.bot.self_log)-2]
            correct_msg = ''
            for i in check_msg.content.split(' '):
                if i.startswith(('.', ',', '>', '/', '"', ':', ';', '{', '}', '[', ']', '(', ')', '|', '-', '+', '_', '+', '?', '!', '<', '*', '@', '#', '$', '%', '^', '&', '`')):
                    check = i[1:]
                    start = i[0]
                else:
                    check = i
                    start = ''
                if i.endswith(('.', ',', '>', '/', '"', ':', ';', '{', '}', '[', ']', '(', ')', '|', '-', '+', '_', '+', '?', '!', '<', '*', '@', '#', '$', '%', '^', '&', '`')):
                    print(check)
                    check = check[:-1]
                    print(check)
                    end = i[len(i)-1]
                else:
                    end = ''
                if dict.check(check) is False:
                    check = dict.suggest(check)[0]
                correct_msg += start + check + end + ' '
            await self.bot.edit_message(check_msg, correct_msg.strip())
            await self.bot.delete_message(ctx.message)


def setup(bot):
    bot.add_cog(Spellcheck(bot))