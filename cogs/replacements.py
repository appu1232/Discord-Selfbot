import discord
import json
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from cogs.utils.menu import Menu

'''Manage replacements within messages.'''


class Replacements:

    def __init__(self, bot):
        self.bot = bot
        self.replacement_dict = dataIO.load_json("settings/replacements.json")

    @commands.command(aliases=['replace'], pass_context=True)
    async def replacements(self, ctx):
        """Replace A with B"""
        await ctx.message.delete()
        menu = Menu("What would you like to do?")
        
        
        # handle new replacements
        def new_replacement(trigger, val):
            self.replacement_dict[trigger.content] = val.content
            with open("settings/replacements.json", "w+") as f:
                json.dump(self.replacement_dict, f, sort_keys=True, indent=4)
        
        end = menu.Submenu("end", "Successfully added a new replacement!")
        
        menu.add_child(menu.InputSubmenu("Add a new replacement", ["Enter a replacement trigger.", "Enter a string to replace the trigger with."], new_replacement, end))

        # handle removing replacements
        def remove_replacement(idx, val):
            self.replacement_dict.pop(val)
            with open("settings/replacements.json", "w+") as f:
                json.dump(self.replacement_dict, f, sort_keys=True, indent=4)
            
        end = menu.Submenu("end", "Successfully removed a replacement!")
        menu.add_child(menu.ChoiceSubmenu("Remove a replacement", "Pick a replacement to remove.", self.replacement_dict, remove_replacement, end))
        
        # handle listing replacements
        menu.add_child(menu.Submenu("List all your replacements", "\n".join([replacement + ": " + self.replacement_dict[replacement] for replacement in self.replacement_dict])))
        
        # go
        await menu.start(ctx)

    async def on_message(self, message):
        if message.author == self.bot.user:
            replaced_message = message.content
            for replacement in self.replacement_dict:
                replaced_message = replaced_message.replace(replacement, self.replacement_dict[replacement])
            if message.content != replaced_message:
                await message.edit(content=replaced_message)

def setup(bot):
    bot.add_cog(Replacements(bot))
