# A Discord selfbot with various commands

A selfbot that has various in-built commands as well as the ability to dynamically add commands using the ``>add`` command on discord.

1. [Features](#features)
2. [Setup](#setup)
3. [Running the Selfbot](#running-the-selfbot)
5. [Custom Commands](#custom-commands)
6. [Keyword Logger](#keyword-logger)
7. [Save Chat Messages](#save-chat-messages)
8. [Google API](#google-api)
9. [Other Things to Note](#other-things-to-note)

## Features

- Google search (web or image).
- Keyword/mention logger. Log messages from any or all servers that have one of the keywords you specify. Useful for seeing if someone mentioned your name or your favorite show/book/whatever else keyword.
- Set your game to anything quickly and easily.
- Add custom commands/reactions. The commands get stored in ``commands.json`` which has some sample commands added to start with.
- Smart MyAnimeList search of anime and manga/LNs using google custom search (and if that fails, using myanimelist's api for search)
- Python debugger. Modeled off of RoboDanny's ?debug command. Does both exec() and eval().
- Save/output the last n number of messages from a chat, including any messages that were deleted.
- Get detailed information about a server and all of its members.
- Quote a message from a user, even if it was deleted.
- Set yourself as afk and reply to a user telling them you are away if they message/mention you. (technically frowned upon by Discord so use it as a joke occasionally, not practical use)
- Quick commands so you can post pointless stuff as fast as possible like ``lenny``, ``shrug``, ``flip``, ``unflip``, and ``comeatmebro``
- Self-destruct your previous message with animated text and a countdown. Yes, it's very pointless and abuses the rate-limit...but it looks cool.
- Simple calculator.
- Various other misc commands.

## Setup

Start off by setting up the ``config.json`` file in the ``settings`` folder:

```json
{
	"my_id" : "",
	"token" : "",
	"google_api_key" : "",
    "custom_search_engine" : "",
	"mal_username" : "",
    "mal_password" : "",
	"set_afk" : "off",
	"afk_message" : "",
	"cmd_prefix": ">",
	"customcmd_prefix": ".",
	"bot_identifier": ":robot:"
}
```

- ``my_id`` - your discord ID. On Discord go to settings > Appearance and Enable Developer Mode. Right-click yourself on the sidebar or chat and click copy ID to get your ID.
- ``token`` - token obtained from ``localStorage.token`` On Discord do ``Ctrl + Shift + i`` for Windows or ``Cmd + Shift + i`` on Mac and then [go here to get your token.](https://i.imgur.com/h3g9uf6.png) Don't give this out to anyone!
- ``google_api_key`` and ``custom_search_engine`` need to be obtained from Google. See the **Google API** section below for instructions.
- ``mal_username`` and ``mal_password`` - MyAnimeList username and password which is required in order to do a MAL search. This is required in order to use the MAL API to grab anime/manga information and is not used for anything else. A normal MAL account will suffice.
- ``set_afk`` - does not need to be changed. It defaults to ``off`` and can be changed through Discord by doing ``>setafk on`` or ``>setafk off``. Warning: As mentioned, this is not something Discord wants selfbots to do. More of a joke than anything.
- ``afk_message`` - the message that is sent when ``set_afk`` is enabled and someone pings you in a channel. This can be edited through Discord with the ``>setafkmsg`` cmd.
- ``cmd_prefix`` and ``customcmd_prefix`` - the prefix for in-built commands and custom commands respectively. Prefixes longer than one character are not supported. You may set the same prefix for both but be careful not to make a custom cmd with the same name as in in-built.
- ``bot_identifier`` - a word/message/emote the bot will add to the beginning of every message it sends (except embeds and replies to quick cmds). Make it empty if you don't want one.

The Google and MAL info is not needed in order to get the bot running. However, they provide some very nice features so do fill them in if you want to use the bot to its full potential.

## Running the selfbot

Note: You must have Python 3.5.2 or above installed. **When installing python, make sure you check "Add Python to PATH" in the install window.**

**Windows:** Double click ``run.bat`` to start the bot. If everything in the config is setup properly you should login fine. If you have a weak internet connection, the bot could take several minutes to log in.

**Mac/Linux:** Navigate to the bot's folder in terminal/shell and run: ``pip install -r requirements.txt`` Once it's finished, run: ``python loopself.py`` to start the bot.

## All Commands:
- ``>restart`` - restart the bot.
- ``>game`` - Set your game. This won't show for yourself but other people can see it.
- ``>calc`` - calculator. Ex: ``>calc 44 * (45-15)`` (note: exponents are done with **)
- ``>stats`` - Bot stats and some user info. Includes information such as uptime, messages sent and received across servers (since the bot started) and some other info. What it looks like:

![img](http://i.imgur.com/x7aEacJ.png)
- ``>ping`` - Responds with ``pong`` and also gives the response time. How the ping response looks:

![img](http://i.imgur.com/XhzTYaW.png)
- ``>g <tags>`` - Google search. Depending on the type of result, certain google cards can be parsed. Some result:

![img](http://i.imgur.com/xaqzej9.png?2)
![img](http://i.imgur.com/6isT5T0.png)
![img](http://i.imgur.com/0AzT1Ah.png)
- ``>i <tags>`` - Google image search. ``>i <n> <tags>`` gives the nth result. An image search result:

![img](http://i.imgur.com/neisYXe.png)
- ``>log`` - See what where and how you are logging. See the **Keyword Logger** section below for more commands used for keyword logging. A logged message:

![img](http://i.imgur.com/4I8B2IW.png)
- ``>log history <n>`` or ``>log history save <n>`` - Output/save the last ``<n>`` number of messages from the chat you just used the command in, including deleted messages. See **Save Chat Messages** section for more details.
- ``>mal anime <tags>`` or ``>mal manga <tags>`` - Searches MyAnimeList for specified entry. Use ``manga`` for light novels as well. To just get the link instead of the full info, put ``[link]`` before the tags. a MAL search result:

![img](http://i.imgur.com/NmqmzdM.png)
- ``>server`` or ``>server <name of server>`` - Get various information about the server. What it looks like:

![img](http://i.imgur.com/gPF7K73.png)
- ``>server members`` - Uploads a txt file containing detailed information about every member on the server including join date, account created, color, top role, and more.
- ``>server avi`` or ``>server avi <name of server>`` - Gets the server image.
- ``>server emojis`` - Lists all the custom emojis for the current server.
- ``>emoji <emoji>`` - Gets the image url for the specified emoji.
- ``>quote`` or ``>quote <words>`` - Quotes the last message in the channel if no words are given or finds the message (if it wasn't too long ago) with the given words and quotes that.
- ``>embed <words>`` - Make an embed out of the message.
- ``>poll <title> = <Option 1> | <Option 2> | ...`` - Create a strawpoll.
- ``>info`` or ``>info <user>`` - See various discord info about yourself or a specified user. Also, ``>info avi`` or ``>info avi <user>`` to see a bigger verion of the users profile picture.

![img](http://i.imgur.com/n4mSRyD.png)
- ``>l2g <tags>`` - Gives a https://googleitfor.me link with the specified tags for when you want to be a smartass.
- ``>setafk on`` or ``>setafk off`` - Turn the afk message trigger on or off.
- ``>setafkmsg <msg>`` - Set the afk message.
- ``>customcmds`` or ``>customcmds long`` - List all custom commands. The long version is more detailed (shows all the replies for each cmd as well). A sample custom command that outputs a picture:

![img](http://i.imgur.com/gBoKnjQ.png)
- ``>add <command> <response>`` or ``>add <command> <response_name> <response>`` - Add a custom command. See the **Custom Commands** section for more info.
- ``>remove <command>`` or ``>remove <command> <response_name>`` - Remove a custom command. See the **Custom Commands** section for more info.
- ``>d`` or ``>d <n>`` - Remove the last message or last n messages you sent (along with this one). ``>d !<n>`` will wait ``<n>`` seconds before deleting the message. It will also repeatedly edit the message and count down the seconds and show a little animation. Very stupid, very unnecessary, but it's pretty funny to see people's reactions. :P
- ``>about`` - link to this github project
- ``>py`` - python debugging. Similiar to RoboDanny's ?debug command. Works with exec and eval statements. Also has the ``>load`` and ``>unload`` cmds to load/unload modules. Example usage:

![img](http://i.imgur.com/MpAtJ7W.png)

![img](http://i.imgur.com/PF0inrv.png)

![img](http://i.imgur.com/P7J4wVb.png)

## Custom Commands:
There are two types of commands: ``string`` commands which only have one response and ``list`` commands which can have multiple responses.

**String commands**:
- 90% of the time you will probably be using the ``string`` command type with something like ``.<command>`` to get the response. Ex: ``.hakomari`` leads to the response ``https://myanimelist.net/manga/55215/Utsuro_no_Hako_to_Zero_no_Maria``
- To add a command, you would do ``>add <command> <response>`` and to remove a command, you would do ``>remove <command>``

In order to have multiple responses to one command, you need to use the ``list`` command type:

**List commands**:
- Add a second parameter between the command and the response like so: ``>add <command> <response_name> <response>`` Ex: ``>add kaguya cute http://i.imgur.com/LtdE1zW.jpg``.
- Adding different ``<response_name>`` and ``<response>`` to the same ``<command>`` will append it to the list of responses for that command.
- Invoke a specific response with: ``.<command> <response_name>`` or ``.<command> <index>``
- Random responses: If more than one response name and response are in a command, get a random response with ``.<command>``
- ``>remove <command> <response_name>`` to remove a specific response from the command or ``>remove <command>`` to remove the entire command.
- **Important Note:** You cannot make a command that was initially a string command into a list command by adding a second response to it. You must remove the string command and add it as a list command.

**Adding commands with more than one word for the command/response_name/response:**

If *any* one of these are multiple words, you must put *all three* in quotes. Ex:
``>add "kaguya" "how cute" "http://i.imgur.com/LtdE1zW.jpg"``
or:
``>add "get good" "https://cdn.discordapp.com/attachments/240823952459431936/266807454506024961/lpLiH3n.png"`` etc.

## Keyword Logger

The Keyword logger can be used for mentions (just like the recent mentions tab on discord) and also for any keywords you want. Here is another example of what it looks like when the bot finds a message with the specified keyword:

![img](http://i.imgur.com/TIqzsf0.png)

As you can see, it shows the context, the keyword it matched, time message was sent, server, channel, and the names of the users in the context.

So, here's how you get started with setting up the logger:

1. Make a channel where you want to receive these log messages. You can set it to be anwhere you want really, but if you don't want anyone else to read/send messages where it logs, create a server for just yourself and use a channel there.
2. In this channel, do ``>log location`` to set the log location to this channel. Now do ``>log`` and you should see that ``Log location:`` is set to this current channel in this server.
3. Add the keywords you want to log. ``>log addkey <word>`` Each key can be more than one word and case does not matter. Removing is just ``>log removekey <word>``. If you want to add mentions to the keywords, just tag yourself or the specified user as if you were mentioning them. When you view the keywords with ``>log``, the mentions will look like \<@1287683643986> or something but that's fine.
4. Add the servers you want to log or set it to log all servers. Go to a server and in any channel, do ``>log add`` to let the logger check that server for keywords. Do ``>log remove`` to remove the server you are in from the logger. If you want to set to all servers, do ``>log toggle``. Do it again to toggle back to only the specified servers.
5. Set the context length. This is the number of messages to show in the log message. The default is set to 4 (this is 4 messages before keyword message + the keyword message). Set it with ``>log context <number>``. You can go up to 20 messages.
6. Add users, words, or servers to the blacklist. These won't trigger the keyword logger even if a match is made. The syntax is: ``>log addblacklist [user] <user>`` or ``>log addblacklist [word] <word>`` or ``>log addblacklist [server]`` When blacklisting users, ``<user>`` can be their name + discriminator, a mention, or their user id. Removing is more or less the same but with ``>log removeblacklist`` instead.

**Why would I need to blacklist words/servers?**

It's just for convenience. If you have 50+ servers and only a handful that you don't want to log, it would be a hastle to add every one to the ``servers`` list so instead you can just enable all servers and add the few to the blacklist. For words being blacklisted, this is just to allow you to specify more in-depth what kind of messages you are trying to look for with the keyword logger.

**Note:**

1. Only other people can trigger the log message. You yourself saying a keyword won't log the message. Also, the channel the keyword logger is logging in is exempt from the keyword search.
2. If the logged message + context is too long, the log message will be split up into multiple messages. These mutiple messages don't use embeds so it won't look as neat, sadly. This shouldn't happen often though.

That should be it. Check your settings any time with ``>log``.

## Save Chat Messages

You can only save chat messages in the servers you are logging (see **Keyword Logger** section above). Use ``>log`` to see what servers are being logged. Every channel in the enabled servers (or every server if all servers is enabled) will have their messages added to logging. By default, the logger holds the latest 500 messages per channel. This value is determined by ``log_size`` in ``log.json`` under the ``settings`` folder. You can increase this value if you want; the upper limit is well over 500.
When you want to save some kind of memorable discussion/funny moment/important reminder or want to shame someone for a message they deleted or something, use the ``>log history`` command:

- ``>log history <n>`` outputs the last ``<n>`` number of messages from the chat you just used the command in. ``<n>`` can be as large as the ``log_size``. Increase ``log_size`` in ``log_json`` if you want more messages. A screencap of what it looks like:

![img](http://i.imgur.com/snAWT7C.png)
- ``>log history save <n>`` saves the messages to a file and uploads the file instead. This is useful when saving large number of messages. A screencap of what it looks like:

![img](http://i.imgur.com/MUwOhgp.png)

**Warning:** You probably want to stick with using ``save`` when grabbing large amounts of messages. Outputting walls of text by doing ``>log history 200`` might get you banned from most public servers.

## Google API

In order to use the ``>i`` command to image search and in order to get more accurate MyAnimeList search results, you will need a Google API key and a Custom Search Engine ID.

Follow these steps to obtain them:

1. Visit the [Google API Console](https://console.developers.google.com/). Once you are in the Console, create a new project.
2. Go to ``Library`` and search ``Custom Search API``. Click it and enable it.
3. Go to ``Credentials`` and click ``create credentials`` and choose ``API Key`` (no need to restrict the key). The value under "Key" is your api key. Paste this into the config.json under ``google_api_key``.
4. Go [here](https://cse.google.com/cse/all) and click ``Add`` and then ``Create`` (if asked to specify a site, just do www.google.com)
5. On the home page of the Custom Search webpage, click on the newly created search engine and change the ``Sites to Search`` option to ``Search the entire web but emphasize included sites``.
6. Make sure the ``Image search`` option is enabled and make sure to click the ``Update`` button at the bottom when you are done with the changes!
6. Go to ``Details`` section and click ``Search Engine ID`` to grab the ID. Copy this and add it for ``custom_search_engine`` in the config.json.

**Note:** Google may take a little while to properly register your key so the search feature may not work right away. If it's still not working after a few hours, then you may have messed up somewhere.

## Other Things to Note
- Free custom search has a limit of 100 searches per day. The commands ``>i`` and ``>mal`` use this search. Still, this should be more than enough but feel free to pay for more if you would like, although I don't think it's needed.
- Try not to keep ``setafk`` on for too long or use it too frequently. Technically, responding to someone else's ping with an automated response is not something Discord likes selfbots doing. I highly suggest this be used as a fun gimmick rather than for actual use all the time.
- Custom commands have a lot of other quirks and flexablility. Check the **Custom commands** section below to see how you can do stuff like add more than one response for a command, get a random response for a command, add commands that have multiple words, etc.


## Acknowledgements

Used a lot of [Danny's](https://github.com/Rapptz) code for certain parts, especially parsing Google cards and the debugger. Also thanks to [IgneelDxD](https://github.com/IgneelDxD) for a lot of suggestions and fixes.