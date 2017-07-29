import discord
import json
from discord.ext import commands
from cogs.utils.dataIO import dataIO

'''Manage replacements within messages.'''


class Replacements:

    def __init__(self, bot):
        self.bot = bot
        self.replacement_dict = dataIO.load_json("settings/replacements.json")

    @commands.command(pass_context=True)
    async def replacements(self, ctx):
        await ctx.message.delete()
        menu_msg = await ctx.send("```\nWhat would you like to do? Pick a number.\n\n1. Create a new replacement\n2. Remove an existing replacement\n3. List all current replacements```")
        reply = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.message.channel and m.author == self.bot.user and m.content.isdigit())
        await reply.delete()
        if int(reply.content) == 1:
            await menu_msg.edit(content="```\nEnter a replacement trigger.\n```")
            reply = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.message.channel and m.author == self.bot.user)
            await reply.delete()
            trigger = reply.content
            await menu_msg.edit(content="```\nEnter a string to replace the trigger with.\n```")
            reply = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.message.channel and m.author == self.bot.user)
            await reply.delete()
            replacement = reply.content
            self.replacement_dict[trigger] = replacement
            with open("settings/replacements.json", "w+") as f:
                json.dump(self.replacement_dict, f, sort_keys=True, indent=4)
            await menu_msg.edit(content="```\nSuccessfully added a {}/{} replacement!\n```".format(trigger, replacement))
        elif int(reply.content) == 2:
            if self.replacement_dict:
                wizard_msg = "```\nPick a replacement to remove.\n\n"
                indexes = {}
                for idx, replacement in enumerate(self.replacement_dict):
                    wizard_msg += "{}. {}/{}\n".format(idx+1, replacement, self.replacement_dict[replacement])
                    indexes[idx] = replacement
                wizard_msg += "```"
                await menu_msg.edit(content=wizard_msg)
                reply = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.message.channel and m.author == self.bot.user and m.content.isdigit())
                await reply.delete()
                try:
                    removed_replacement = self.replacement_dict.pop(indexes[int(reply.content)-1])
                    with open("settings/replacements.json", "w+") as f:
                        json.dump(self.replacement_dict, f, sort_keys=True, indent=4)
                    await menu_msg.edit(content="```\nSuccessfully removed the {}/{} replacement!\n```".format(indexes[int(reply.content)-1], removed_replacement))
                except (IndexError, KeyError):
                    await menu_msg.edit(content="```\nInvalid number!\n```")
            else:
                await menu_msg.edit(content="```You have no replacements to remove!```")
        elif int(reply.content) == 3:
            reply_msg = "```All replacements:\n"
            for replacement in self.replacement_dict:
                reply_msg += replacement + ": " + self.replacement_dict[replacement] + "\n"
            await menu_msg.edit(content=reply_msg + "```")

    async def on_message(self, message):
        if message.author == self.bot.user:
            replaced_message = message.content
            for replacement in self.replacement_dict:
                replaced_message = replaced_message.replace(replacement, self.replacement_dict[replacement])
            if message.content != replaced_message:
                await message.edit(content=replaced_message)

def setup(bot):
    bot.add_cog(Replacements(bot))
