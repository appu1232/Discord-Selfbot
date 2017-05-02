import discord
from discord.ext import commands
import collections
import aiohttp
import inspect
import traceback
from contextlib import redirect_stdout
from PythonGists import PythonGists
import io

'''Module for an embeded python interpreter. More or less the same as the debugger module but with embeds.'''


class EmbedShell():
    def __init__(self, bot):
        self.bot = bot
        self.repl_sessions = {}
        self.repl_embeds = {}
        self.aioclient = aiohttp.ClientSession()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')

    def get_syntax_error(self, err):
        """Returns SyntaxError formatted for repl reply."""
        return '```py\n{0.text}{1:>{0.offset}}\n{2}: {0}```'.format(
            err,
            '^',
            type(err).__name__)

    @commands.group(name='shell',
                    aliases=['ipython', 'repl',
                             'longexec', 'core', 'overkill'],
                    pass_context=True,
                    invoke_without_command=True)
    async def repl(self, ctx, *, name: str = None):
        """Head on impact with an interactive python shell."""
        # TODO Minimize local variables
        # TODO Minimize branches

        session = ctx.message.channel.id

        embed = discord.Embed(
            description="_Enter code to execute or evaluate. "
                        "`exit()` or `quit` to exit._")

        embed.set_author(
            name="Interactive Python Shell",
            icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb"
                     "/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png")

        embed.set_footer(text="Based on RDanny's repl command by Danny. Embed shell by eye-sigil.")
        if name is not None:
            embed.title = name.strip(" ")

        history = collections.OrderedDict()

        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'server': ctx.message.server,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'discord': discord,
            '_': None
        }

        variables.update(globals())

        if session in self.repl_sessions:

            error_embed = discord.Embed(
                color=15746887,
                description="**Error**: "
                            "_Shell is already running in channel._")
            await self.bot.say(embed=error_embed)
            return

        shell = await self.bot.say(embed=embed)

        self.repl_sessions[session] = shell
        self.repl_embeds[shell] = embed

        while True:
            response = await self.bot.wait_for_message(
                author=ctx.message.author,
                channel=ctx.message.channel,
                check=lambda m: m.content.startswith('`'))

            cleaned = self.cleanup_code(response.content)
            shell = self.repl_sessions[session]

            shell_check = discord.utils.get(
                self.bot.messages,
                id=self.repl_sessions[session].id)

            # Self Bot Method
            if shell_check is None:
                new_shell = await self.bot.say(embed=self.repl_embeds[shell])

                self.repl_sessions[session] = new_shell

                embed = self.repl_embeds[shell]
                del self.repl_embeds[shell]
                self.repl_embeds[new_shell] = embed

                shell = self.repl_sessions[session]

            del shell_check

            try:
                await self.bot.delete_message(response)
            except discord.Forbidden:
                pass

            if len(self.repl_embeds[shell].fields) >= 7:
                self.repl_embeds[shell].remove_field(0)

            if cleaned in ('quit', 'exit', 'exit()'):
                self.repl_embeds[shell].color = 16426522

                if self.repl_embeds[shell].title is not discord.Embed.Empty:
                    history_string = "History for {}\n\n\n".format(
                        self.repl_embeds[shell].title)
                else:
                    history_string = "History for latest session\n\n\n"

                for item in history.keys():
                    history_string += ">>> {}\n{}\n\n".format(
                        item,
                        history[item])

                gist_url = PythonGists.Gist(description='Py output', content=str(history_string), name='output.txt')
                return_msg = "[`Leaving shell session. " \
                             "History hosted on Gist.`]({})".format(
                    gist_url)

                self.repl_embeds[shell].add_field(
                    name="`>>> {}`".format(cleaned),
                    value=return_msg,
                    inline=False)

                try:
                    await self.bot.edit_message(
                        self.repl_sessions[session],
                        embed=self.repl_embeds[shell])
                except:
                    pass

                del self.repl_embeds[shell]
                del self.repl_sessions[session]
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as err:
                    self.repl_embeds[shell].color = 15746887

                    return_msg = self.get_syntax_error(err)

                    history[cleaned] = return_msg

                    if len(cleaned) > 800:
                        cleaned = "<Too big to be printed>"
                    if len(return_msg) > 800:
                        gist_url = PythonGists.Gist(description='Py output', content=str(return_msg), name='output.txt')
                        return_msg = "[`SyntaxError too big to be printed. " \
                                     "Hosted on Gist.`]({})".format(
                            gist_url)

                    self.repl_embeds[shell].add_field(
                        name="`>>> {}`".format(cleaned),
                        value=return_msg,
                        inline=False)

                try:
                    await self.bot.edit_message(
                        self.repl_sessions[session],
                        embed=self.repl_embeds[shell])
                except:
                    pass
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as err:
                self.repl_embeds[shell].color = 15746887
                value = stdout.getvalue()
                fmt = '```py\n{}{}\n```'.format(
                    value,
                    traceback.format_exc())
            else:
                self.repl_embeds[shell].color = 4437377

                value = stdout.getvalue()

                if result is not None:
                    fmt = '```py\n{}{}\n```'.format(
                        value,
                        result)

                    variables['_'] = result
                elif value:
                    fmt = '```py\n{}\n```'.format(value)

            history[cleaned] = fmt

            if len(cleaned) > 800:
                cleaned = "<Too big to be printed>"

            try:
                if fmt is not None:
                    if len(fmt) >= 800:
                        gist_url = PythonGists.Gist(description='Py output', content=str(fmt), name='output.txt')
                        self.repl_embeds[shell].add_field(
                            name="`>>> {}`".format(cleaned),
                            value="[`Content too big to be printed. "
                                  "Hosted on Gist.`]({})".format(
                                gist_url),
                            inline=False)

                        await self.bot.edit_message(
                            self.repl_sessions[session],
                            embed=self.repl_embeds[shell])
                    else:
                        self.repl_embeds[shell].add_field(
                            name="`>>> {}`".format(cleaned),
                            value=fmt,
                            inline=False)

                        await self.bot.edit_message(
                            self.repl_sessions[session],
                            embed=self.repl_embeds[shell])
                else:
                    self.repl_embeds[shell].add_field(
                        name="`>>> {}`".format(cleaned),
                        value="`Empty response, assumed successful.`",
                        inline=False)

                    await self.bot.edit_message(
                        self.repl_sessions[session],
                        embed=self.repl_embeds[shell])

            except discord.Forbidden:
                pass

            except discord.HTTPException as err:
                try:
                    error_embed = discord.Embed(
                        color=15746887,
                        description='**Error**: _{}_'.format(err))
                    await self.bot.say(embed=error_embed)
                except:
                    pass

    @repl.command(name='jump',
                  aliases=['hop', 'pull', 'recenter', 'whereditgo'],
                  pass_context=True)
    async def _repljump(self, ctx):
        """Brings the shell back down so you can see it again."""

        session = ctx.message.channel.id

        if session not in self.repl_sessions:
            try:
                error_embed = discord.Embed(
                    color=15746887,
                    description="**Error**: _No shell running in channel._")
                await self.bot.say(embed=error_embed)
            except:
                pass
            return

        shell = self.repl_sessions[session]
        embed = self.repl_embeds[shell]

        await self.bot.delete_message(ctx.message)
        try:
            await self.bot.delete_message(shell)
        except discord.errors.NotFound:
            pass
        try:
            new_shell = await self.bot.say(embed=embed)
        except:
            pass

        self.repl_sessions[session] = new_shell

        del self.repl_embeds[shell]
        self.repl_embeds[new_shell] = embed

    @repl.command(name='clear',
                  aliases=['clean', 'purge', 'cleanup',
                           'ohfuckme', 'deletthis'],
                  pass_context=True)
    async def _replclear(self, ctx):
        """Clears the fields of the shell and resets the color."""

        session = ctx.message.channel.id

        if session not in self.repl_sessions:
            try:
                error_embed = discord.Embed(
                    color=15746887,
                    description="**Error**: _No shell running in channel._")
                await self.bot.say(embed=error_embed)
            except:
                pass
            return

        shell = self.repl_sessions[session]

        self.repl_embeds[shell].color = discord.Color.default()
        self.repl_embeds[shell].clear_fields()

        await self.bot.delete_message(ctx.message)
        try:
            await self.bot.edit_message(
                shell,
                embed=self.repl_embeds[shell])
        except:
            pass


def setup(bot):
    bot.add_cog(EmbedShell(bot))