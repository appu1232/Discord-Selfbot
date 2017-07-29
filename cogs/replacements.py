import discord
import json
from discord.ext import commands
from cogs.utils.dataIO import dataIO
import shutil
import os.path

'''Manage replacements within messages.'''


class Replacements:

    def __init__(self, bot):
        self.bot = bot
        if not os.path.isfile("settings/replacements.json"):
            shutil.copy2("settings/replacements.json.sample", "settings/replacements.json")
        self.replacement_dict = dataIO.load_json("settings/replacements.json")

    @commands.command(pass_context=True)
    async def replacements(self, ctx):
        await self.bot.delete_message(ctx.message)
        menu_msg = await self.bot.send_message(ctx.message.channel, "```\nWhat would you like to do? Pick a number.\n\n1. Create a new replacement\n2. Remove an existing replacement\n3. List all current replacements```")
        def check(message):
            if message.content.isdigit():
                return True
            return False
        reply = await self.bot.wait_for_message(author=self.bot.user, check=check, channel=ctx.message.channel)
        await self.bot.delete_message(reply)
        if int(reply.content) == 1:
            await self.bot.edit_message(menu_msg, "```\nEnter a replacement trigger.\n```")
            reply = await self.bot.wait_for_message(author=self.bot.user, channel=ctx.message.channel)
            await self.bot.delete_message(reply)
            trigger = reply.content
            await self.bot.edit_message(menu_msg, "```\nEnter a string to replace the trigger with.\n```")
            reply = await self.bot.wait_for_message(author=self.bot.user, channel=ctx.message.channel)
            await self.bot.delete_message(reply)
            replacement = reply.content
            self.replacement_dict[trigger] = replacement
            with open("settings/replacements.json", "w+") as f:
                json.dump(self.replacement_dict, f, sort_keys=True, indent=4)
            await self.bot.edit_message(menu_msg, "```\nSuccessfully added a {}/{} replacement!\n```".format(trigger, replacement))
        elif int(reply.content) == 2:
            if self.replacement_dict:
                wizard_msg = "```\nPick a replacement to remove.\n\n"
                indexes = {}
                for idx, replacement in enumerate(self.replacement_dict):
                    wizard_msg += "{}. {}/{}\n".format(idx+1, replacement, self.replacement_dict[replacement])
                    indexes[idx] = replacement
                wizard_msg += "```"
                await self.bot.edit_message(menu_msg, wizard_msg)
                reply = await self.bot.wait_for_message(author=self.bot.user, check=check, channel=ctx.message.channel)
                await self.bot.delete_message(reply)
                try:
                    removed_replacement = self.replacement_dict.pop(indexes[int(reply.content)-1])
                    with open("settings/replacements.json", "w+") as f:
                        json.dump(self.replacement_dict, f, sort_keys=True, indent=4)
                    await self.bot.edit_message(menu_msg, "```\nSuccessfully removed the {}/{} replacement!\n```".format(indexes[int(reply.content)-1], removed_replacement))
                except (IndexError, KeyError):
                    await self.bot.edit_message(menu_msg, "```\nInvalid number!\n```")
            else:
                await self.bot.edit_message(menu_msg, "```You have no replacements to remove!```")
        elif int(reply.content) == 3:
            reply_msg = "```All replacements:\n"
            for replacement in self.replacement_dict:
                reply_msg += replacement + ": " + self.replacement_dict[replacement] + "\n"
            await self.bot.edit_message(menu_msg, reply_msg + "```")

    async def on_message(self, message):
        if message.author == self.bot.user:
            replaced_message = message.content
            for replacement in self.replacement_dict:
                replaced_message = replaced_message.replace(replacement, self.replacement_dict[replacement])
            if message.content != replaced_message:
                await self.bot.edit_message(message, replaced_message)

def setup(bot):
    bot.add_cog(Replacements(bot))
