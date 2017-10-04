import asyncio

class Menu:
    """An interactive menu class for Discord."""
    
    
    class Submenu:
        """A metaclass of the Menu class."""
        def __init__(self, name, content):
            self.content = content
            self.leads_to = []
            self.name = name
            
        def get_text(self):
            text = ""
            for idx, menu in enumerate(self.leads_to):
                text += "[{}] {}\n".format(idx+1, menu.name)
            return text
                
        def get_child(self, child_idx):
            try:
                return self.leads_to[child_idx]
            except IndexError:
                raise IndexError("child index out of range")
                
        def add_child(self, child):
            self.leads_to.append(child)
            
    class InputSubmenu:
        """A metaclass of the Menu class for submenu options that take input, instead of prompting the user to pick an option."""
        def __init__(self, name, content, input_function, leads_to):
            self.content = content
            self.name = name
            self.input_function = input_function
            self.leads_to = leads_to
            
        def next_child(self):
            return self.leads_to
            
    class ChoiceSubmenu:
        """A metaclass of the Menu class for submenu options for choosing an option from a list."""
        def __init__(self, name, content, options, input_function, leads_to):
            self.content = content
            self.name = name
            self.options = options
            self.input_function = input_function
            self.leads_to = leads_to
            
        def next_child(self):
            return self.leads_to
            
    
    def __init__(self, main_page):
        self.children = []
        self.main = self.Submenu("main", main_page)
        
    def add_child(self, child):
        self.main.add_child(child)
        
    async def start(self, ctx):
        current = self.main
        menu_msg = None
        while True:
            output = ""       
        
            if type(current) == self.Submenu:
                if type(current.content) == str:
                    output += current.content + "\n"
                elif callable(current.content):
                    current.content()
                else:
                    raise TypeError("submenu body is not a str or function")
                    
                if not current.leads_to:
                    if not menu_msg:
                        menu_msg = await ctx.send("```" + output + "```")
                    else:
                        await menu_msg.edit(content="```" + output + "```")
                    break
                    
                output += "\n" + current.get_text() + "\n"
                output += "Enter a number."
                
                if not menu_msg:
                    menu_msg = await ctx.send("```" + output + "```")
                else:
                    await menu_msg.edit(content="```" + output + "```")
                    
                reply = await ctx.bot.wait_for("message", check=lambda m: m.author == ctx.bot.user and m.content.isdigit() and m.channel == ctx.message.channel)
                await reply.delete()
                
                try:
                    current = current.get_child(int(reply.content) - 1)
                except IndexError:
                    print("Invalid number.")
                    break
                    
            elif type(current) == self.InputSubmenu:
                if type(current.content) == list:
                    answers = []
                    for question in current.content:
                        await menu_msg.edit(content="```" + question + "\n\nEnter a value." + "```")
                        reply = await ctx.bot.wait_for("message", check=lambda m: m.author == ctx.bot.user and m.channel == ctx.message.channel)
                        await reply.delete()
                        answers.append(reply)
                    current.input_function(*answers)
                else:
                    await menu_msg.edit(content="```" + current.content + "\n\nEnter a value." + "```")
                    reply = await ctx.bot.wait_for("message", check=lambda m: m.author == ctx.bot.user and m.channel == ctx.message.channel)
                    await reply.delete()
                    current.input_function(reply)
                
                if not current.leads_to:
                    break
                    
                current = current.leads_to
            
            elif type(current) == self.ChoiceSubmenu:
                result = "```" + current.content + "\n\n"
                if type(current.options) == dict:
                    indexes = {}
                    for idx, option in enumerate(current.options):
                        result += "[{}] {}: {}\n".format(idx+1, option, current.options[option])
                        indexes[idx] = option
                else:
                    for idx, option in current.options:
                        result += "[{}] {}\n".format(idx+1, option)
                await menu_msg.edit(content=result + "\nPick an option.```")
                reply = await ctx.bot.wait_for("message", check=lambda m: m.author == ctx.bot.user and m.content.isdigit() and m.channel == ctx.message.channel)
                await reply.delete()
                if type(current.options) == dict:
                    current.input_function(reply, indexes[int(reply.content)-1])
                else:
                    current.input_function(reply, current.options[reply-1]) 
                    
                if not current.leads_to:
                    break
                    
                current = current.leads_to
                    