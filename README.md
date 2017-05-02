Come join the dedicated server for this bot: https://discord.gg/TBQE72k Feel free to ask questions, give suggestions, report bugs, or just hang out here. If you need help setting up the bot, I or someone on the server can help too.

# Discord Selfbot

Takes less than 5 minutes to set up. Has various commands and utilities, keyword logger/notifier, and adding custom commands. A few examples:

![](http://i.imgur.com/3H9zpop.gif)

1. [Features](#features)
2. [Setup](#setup)
3. [Optional Setup](#optional-setup)
4. [Running the selfbot](#running-the-selfbot)
5. [All Commands](#all-commands)
6. [Custom Commands](#custom-commands)
7. [Keyword Notifier](#keyword-notifier)
8. [User Following](#follow-users)
9. [Save Chat Messages](#save-chat-messages)
10. [Google API](#google-api)
11. [Other Things to Note](#other-things-to-note)

## Features

- Google web and image search.
- Keyword/user logger and notifier. Get notified when keywords you specified are said in any of your server or follow users and get notified when they send a message (with a cooldown). Useful to track someone or see if someone mentioned your name or your favorite show/book/whatever else keywords and you want to stalk— I mean, talk to them about it.
- Set your game to anything or set up multiple and cycle through them.
- Cycle through avatars automatically (minimum 5 minute interval).
- Add custom commands/reactions. The commands get saved to ``commands.json`` which has some sample commands added to start with. Can be used as macros for other commands as well.
- Custom embeds.
- Save image/gif/webm dumps (urls or attachments) in channels quickly to your computer (checks for duplicates as well).
- Smart MyAnimeList search of anime and manga/LNs using google custom search (and if that fails, using myanimelist's api for search)
- Python interpreter. Modeled off of RoboDanny's ?debug command. Does both exec() and eval(). Ability to save and load scripts.
- Save/output the last n number of messages from a chat, including any messages that were deleted.
- Get detailed information about a server and all of its members.
- Purge the last n messages you sent in a channel.
- Simple calculator.
- Quick commands so you can post pointless stuff as fast as possible like ``lenny``, ``shrug``, ``flip``, ``unflip``, and ``comeatmebro`` Also, meme commands like spacing text or converting it to regional indicator emojis.
- Various other misc commands like spoiler tagging text (encrypts the text), creating strawpolls, embeding text, server/user info commands, and more.

## Setup

Download the zip and extract it. Inside this folder, go into the ``settings`` folder and edit the file ``config.json``. If you can't edit it, you may need to download something like [Notepad++.](https://notepad-plus-plus.org/download/v7.3.3.html)

```json
{
    "token" : "your_token_here",
    "cmd_prefix": ">",
    "customcmd_prefix": ".",
    "bot_identifier": ":robot:"
}
```

- ``token`` - token obtained from ``localStorage.token`` On Discord do ``Ctrl + Shift + i`` for Windows or ``Cmd + Option + i`` on Mac and then [go here to get your token.](https://i.imgur.com/h3g9uf6.png) [For Mac.](https://i.imgur.com/otvxoYL.png) Don't give this out to anyone!
- ``cmd_prefix`` and ``customcmd_prefix`` - the prefix for in-built commands and custom commands respectively. Prefixes longer than one character are not supported. You may set the same prefix for both but be careful not to make a custom cmd with the same name as an in-built.
- ``bot_identifier`` - a word/message/emote the bot will add to the beginning of every message it sends (except embeds and replies to quick cmds). Make it empty if you don't want one.

**Note:** On Mac, you may need to [disable smartquotes.](http://www.iclarified.com/38772/how-to-disable-curly-quotes-in-mac-os-x-mavericks) Quotes in the json should look like this: ``"`` or else the bot may throw errors when logging in.

## Optional Setup

This is the ``optional_config.json`` file in the ``settings`` folder. These are additional parts that are not required to get the bot running but do provide some nice features.

```json
{
    "google_api_key" : "",
    "custom_search_engine" : "",
    "mal_username" : "",
    "mal_password" : ""
}
```

- ``google_api_key`` and ``custom_search_engine`` need to be obtained from Google. See the [Google API](#google-api) section below for instructions. This allows for image search with the ``>i`` command as well as smarter ``>mal`` search.
- ``mal_username`` and ``mal_password`` - MyAnimeList username and password which is required in order to do a MAL search. This is required in order to use the MAL API to grab anime/manga information and is not used for anything else. A normal MAL account will suffice.

## Running the selfbot

Note: You must have [Python 3.5.2 or above](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) installed. Make sure [this is selected](https://i.imgur.com/ZXEpGtH.png) when installing Git on Windows. **When installing Python, check ["Add Python to PATH"](https://i.imgur.com/KXgMcOK.png) in the install window.** Some Mac users have reported problems with Python 3.6 so if you are a Mac user, try to go for Python 3.5.

**Windows:**

Double click ``run.bat`` to start the bot. An anti-virus may warn you when you try to run it but let it pass. There is no malicious code here. If everything in the config is setup properly you should login fine. If you have a weak internet connection, the bot could take several minutes to log in.

Optionally, create a shortcut to the .bat file and [add it to startup](http://www.computerhope.com/issues/ch000322.htm) so you don't have to remember to run it every time.

**Mac/Linux:**

Navigate to the bot's folder in terminal/shell and run: ``bash run_linuxmac.sh``

Alternatively if the bash script isn't working for you, try ``sudo -H pip install -r requirements.txt`` (only need to do it the first time) and then try running the bash script again.

**Updating the bot:**

The respective script (``run.bat`` for Windows and ``run_linuxmac.sh`` for Mac/Linux) will prompt you when there's a new update on startup and will apply the update for you (it will save your settings). [You will need Git in order to do this.](https://git-scm.com/downloads)

Manual update: Unless otherwise stated, all you need to do is save your ``settings`` folder and its contents somewhere, delete everything else, download the newest version, and then replace the ``settings`` folder with your ``settings`` folder. If you know how to use git properly, that option exists as well.

## All Commands:
- ``>about`` - link to this github project and some more info.
- ``>help`` - list of all commands and what they do (not as detailed as this secion)
- ``>restart`` - restart the bot. If there is an update available it will prompt you if you want to update as well.
- ``>quit`` - quits the bot.
- ``>update`` - updates the bot to the latest version.
- ``>game <text>`` or ``>game <text1> | <text2> | <text3> | ...`` - Set your game. If multiple are given, it will cycle through them. **The game won't show for yourself but other people can see it.** The bot sets the game status on startup as well if you set it up once. Do ``>game`` with nothing else to turn off your game.
- ``>avatar`` - sets your avatar by cycling through the images you have under the ``avatars`` folder (.jpg, .jpeg, and .png only). It will prompt you with your desired interval and whether to change randomly or in order.
  + On first use, this command will require your discord password. This is just a limitation of the API. In no way is your password being distributed. It is just stored locally and called on internally to change your avatar. Just make sure you input the password in a private channel so no one sees it.
- ``>stats`` - Bot stats and some user info. Includes information such as uptime, messages sent and received across servers (since the bot started) and some other info. What it looks like:

![img](http://i.imgur.com/x7aEacJ.png)

**Custom Commands**

- ``>customcmds`` or ``>customcmds long`` - List all custom commands. The long version is more detailed (shows all the replies for each cmd as well). A sample custom command that outputs a picture:

![img](http://i.imgur.com/gBoKnjQ.png)
- ``>add <command> <response>`` or ``>add <command> <response_name> <response>`` - Add a custom command.
- ``>remove <command>`` or ``>remove <command> <response_name>`` - Remove a custom command.

See the [Custom Commands](#custom-commands) section for more info on how to invoke commands and set up multiple responses to the same command.

**Google web and image search commands**

- ``>g <tags>`` - Google search. Depending on the type of result, certain google cards can be parsed. Some results:

![img](http://i.imgur.com/xaqzej9.png?2)
![img](http://i.imgur.com/6isT5T0.png)
![img](http://i.imgur.com/0AzT1Ah.png)
- ``>i <tags>`` - Google image search. ``>i <n> <tags>`` gives the nth result. An image search result:

![img](http://i.imgur.com/neisYXe.png)

**Imagedump saver**

This command goes through ``n`` messages in a channel and downloads all the images/gifs/webms it finds (attachments and urls). It detects and ignores duplicate images. Also has many flags that can be specified which gives more options as to what images to download and where to look.

Simple:

- ``>imagedump <n>`` - checks the last ``<n>`` messages in this chat and downloads all the images/gifs/webms found.

More options:

- ``>imagedump <n> | items=<m> | before=YYYY-MM-DD | after=YYYY-MM-DD | dim=WidthxHeight | ratio=Width:Height | type=<type_of_item> | channel=<id> | user=<id>`` - add any one or more of these to the command to furthur specify your requirements to find items.
  + ``items=<m>`` - when checking the last ``<n>`` messages, only download ``<m>`` items max.
  + ``before=YYYY-MM-DD`` - check ``<n>`` messages before this date. Ex: ``before=2017-02-16``
  + ``after=YYYY-MM-DD`` - check ``<n>`` messages after this date.
  + ``dim=WidthxHeight`` - only download items with these dimensions. Ex: ``dim=1920x1080`` Optionally, do ``dim>=WidthxHeight`` for images greater than or equal and ``dim<=WidthxHeight`` for less than or equal to these dimensions.
  + ``ratio=Width:Height`` - only download items with these ratios. Ex: ``ratio=16:9``
  + ``type=<type_of_item>`` - only download these types of files. Ex: ``type=png`` or ``type=gif, webm`` All options: jpg, png, gif (includes gifv), webm.
  + ``channel=<id>`` - download from a different channel (can be from a different server). Useful if you can't send messages in that channel. [Enable developer mode,](https://i.imgur.com/AmOZHzL.png) right click on the channel name, and hit ``copy id`` to get the id. Ex: ``channel=299293492645986307``
  + ``user=<id>`` - download only items posted by this user. Right click on the user to get their id. Ex: user=124910128582361092
  
Example: I want a new wallpaper. I download 100 items with type .png that fit on my 16:9 monitor with at least 720p quality:

- ``>imagedump 5000 | items=100 | type=png | ratio=16:9 | dim>=1280x720``
  + Note that the number of messages to check is still needed here. You don't need any exact number, just specify a vague number of messages that you think will cover the amount.

Other imagedump options:

- ``>imagedump dir path/to/directory/`` - if you want to change where the images/gifs are automatically saved to.
  + ``>imagedump dir`` - see the current path set to save images to.
- ``>imagedump s <n>`` - downloads silently without sending a "Downloading..." message or a "Done" message at the end. Useful if you don't want to clog up the channel.
- ``>imagedump stop`` - stop any imagedump downloads occurring right now.

Note: Large number of messages specified for ``<n>`` (> 100,000) will take a decent amount of time to just fetch, let alone download. The console may be stuck at fetching for a while and may say "Unclosed client session" but it's fine, it will just take some time.

**MyAnimeList commands**

- ``>mal anime <tags>`` or ``>mal manga <tags>`` - Searches MyAnimeList for specified entry. Use ``manga`` for light novels as well.
- ``>mal anime [link] <tags>`` or ``>mal manga [link] <tags>`` - Just gets the link to the MAL page instead of the full info.

A MAL search result:

![img](http://i.imgur.com/NmqmzdM.png)

**Server commands**

- ``>server`` or ``>server <name of server>`` - Get various information about the server. What it looks like:

![img](http://i.imgur.com/gPF7K73.png)
- ``>server role <name of role>`` - Get info about said role.
- ``>server members`` - Uploads a txt file containing detailed information about every member on the server including join date, account created, color, top role, and more.
- ``>server avi`` or ``>server avi <name of server>`` - Gets the server image.
- ``>server emojis`` - Lists all the custom emojis for the current server.

**Misc**

- ``>ping`` - Responds with ``pong`` and also gives the response time.
- ``>poll <title> = <Option 1> | <Option 2> | ...`` - Create a strawpoll.
- ``>spoiler <word> <some spoilers>`` or ``>spoiler <words> | <some spoiler>`` - Encrypt the spoiler and provides a link to decode it using ROT13. Basically spoiler tagging a message. Ex: ``>spoiler Book He lives`` or ``>spoiler Some movie | He was his brother all along``
- ``>calc`` - calculator. Ex: ``>calc 44 * (45-15)``
- ``>choose <Option 1> | <Option 2> | ...`` - Randomly chooses one of the given options.
- ``>d`` or ``>d <n>`` - Remove the last message or last n messages you sent (along with this one). ``>d !<n>`` will wait ``<n>`` seconds before deleting the message. It will also repeatedly edit the message and count down the seconds and show a little animation. Very stupid, very unnecessary, and it abuses the rate-limit...but it's pretty funny to see people's reactions. :P
- ``>info`` or ``>info <user>`` - See various discord info about yourself or a specified user. Also, ``>info avi`` or ``>info avi <user>`` to see a bigger verion of the users profile picture.

![img](http://i.imgur.com/n4mSRyD.png)
- ``>embed`` - Make an embed out of the message. You can customize all attributes of the embed. Do ``>embed`` to see more specific instructions and the syntax.
	+ Pro tip: save custom embeds by adding the entire command as a custom command. Ex: ``>add "customembed" ">embed title=hello world | description=this is a test | color=3AB35E"``

![img](https://i.imgur.com/0VBktGI.png)

- ``>emoji <emoji>`` - Gets the image url for the specified emoji.
- ``>quote`` or ``>quote <words>`` - Quotes the last message in the channel if no words are given or finds the message (if it wasn't too long ago) with the given words and quotes that. Deleted messages can be quoted.
![quote](https://cloud.githubusercontent.com/assets/14967932/24776240/f509e02a-1aed-11e7-95f5-6ecf30eb367a.gif)  

- ``>l2g <tags>`` - Gives a https://googleitfor.me link with the specified tags for when you want to be a smartass.
- ``>gist <text>`` - posts the given text to Gist. Also can do ``>gist file /path/to/file`` to post the file if the file is in the bot folder.
- ``>regional <text>`` - send each letter in this message as regional indicator emojis.
- ``>space <text>`` or ``>space <n> <text>`` - put a space between each letter in the message. Optionally, specify how many spaces to put between each letter with ``<n>``
- ``>react <text>`` or ``>react <text> <id>`` - react to the above message with the given text. If the message id is given, it will react to that message instead.

**Logging commands**

- ``>log`` - See what, where, and how you are logging/tracking. See the [Keyword Notifier](#keyword-notifier) section below for more commands used for keyword logging. A logged message:

![img](http://i.imgur.com/4I8B2IW.png)
- ``>log history <n>`` or ``>log history save <n>`` - Output/save the last ``<n>`` number of messages from the chat you just used the command in, including deleted messages. See [Save Chat Messages](#save-chat-messages) section for more details.

**Python Interpreter**

- ``>py <code>`` - python interpreter. Similiar to RoboDanny's ?debug command. Works with exec and eval statements. Also has the ``>load <module>`` ``>unload <module>`` and ``>reload`` cmds to load, unload, and reload modules.

Example usage of the python interpreter:

![img](http://i.imgur.com/MpAtJ7W.png)

- ``>py save <filename>`` ``>py run <filename>`` ``>py list`` ``>py view <filename>`` ``>py delete <filename>`` - Save/run/delete/view the contents of scripts. ``>py save <filename>`` saves the last ``>py <code>`` you did into a file. ``>py list`` or ``>py list <page_number>`` lets you see the list of scripts you have saved.
![pyscripts](https://cloud.githubusercontent.com/assets/14967932/24776287/1b93ec36-1aee-11e7-8418-14d91105e5f5.gif)

Alternatively, there is also the ``>repl`` command which uses an embed shell like so:
![img](https://i.imgur.com/jg2dmAq.png)

- Input by putting the code in \` like this: \`print('test')\`
- Make the shell jump to the most recent message with ``>repl jump`` and clear the current shell with ``>repl clear``
- Quit the shell with \`quit\`
- Based entirely off of eye-sigil's repl shell. Kind of unnecessarily huge and fancy but hey, it looks nice.

## Custom Commands:
![custom](https://cloud.githubusercontent.com/assets/14967932/24776178/bb6bb5f0-1aed-11e7-94e4-567b993b4ba6.gif)

**There are two ways to add custom commands.** The first way:

- ``>add <command> <response>`` Now, if you do ``.<command>`` you will receive ``<response>``.

Example: ``>add nervous http://i.imgur.com/K9gMjWo.gifv`` Then, doing ``.nervous`` will output this imgur link (images and gifs will auto embed)

However, **you may want to add multiple responses to the same command.** So the second way:

- ``>add <command> <response_name> <response>``. This way, you can add multiple responses to the same command.

Example: ``>add kaguya present http://i.imgur.com/7Px7EZx.png`` then you can add another to the ``.kaguya`` command: ``>add kaguya yes http://i.imgur.com/y0yAp1j.png``.

Invoke a specific response with ``.<command> <response_name>`` or get a random response for that command with ``.<command>``

Ex: ``.kaguya present`` would give you that specific link but ``.kaguya`` would give you one of the two you added to the kaguya command.

Change the customcmd default embed color with ``>customcmds color <hex_value>`` or set it to have no color with just ``>customcmds color``
If for some reason, Discord isn't embedding images/gifs correctly (might just be Discord server issues sometimes), you can toggle auto-embedding with ``>customcmds embed``

**Ways to view your customcmds:**

- ``>customcmds`` - small view, just shows the command and response names.
  + ``>customcmds <command>`` - view just this command and its response names.
  + ``>customcmds gist`` - posts to Gist and gets the link to it rather than posting it in the chat (useful if your list is really long)
- ``>customcmds long`` - large view, shows you everything including the responses.
  + ``>customcmds long <command>`` - view just this command and it's response names and responses.
  + ``>customcmds long gist`` - posts it to Gist and retrieves the link like with customcmds gist.
  


**Removing commands:**
- ``>remove <command>`` or ``>remove <command> <response_name>`` if you want to remove a specific response for a command.

**Adding/removing commands/responses with multiple words:** 

If anything you are adding/removing is more than one word, **you must put each part in quotes**. Example: ``>add "kaguya" "how cute" "http://i.imgur.com/LtdE1zW.jpg"`` or ``>add "copypasta" "I identify as an attack helicopter."``

## Keyword Notifier

The Keyword notifier can be used to log and get notified when someone says a keyword or words in one of your servers (works for mentions as well). Here is another example of what it looks like when the bot finds a message with the specified keyword:

![img](https://i.imgur.com/5dMJo27.png)

As you can see, it shows the context, the keyword it matched, time message was sent, server, channel, and the names of the users in the context.

So, here's how you get started with setting up the notifier:

1. Go to the server where you want to receive notifications. You probably want a private server just for yourself or one where you are admin and can create private channels.
2. Set up the notifications settings for this server/channel so that you get notified on every new message, not just mentions.
3. Go to your **Server Settings** ([it's here](https://i.imgur.com/PofYpiZ.png)) and go to **WebHooks** near the bottom. Create a webhook.
4. Give it whatever name and avatar you like and change the channel to the channel where you want to receive notifications. Copy the url and **make sure you hit save.** [It should look something like this.](https://i.imgur.com/AmaaMaA.png)
5. Do ``>webhook <url>`` where ``<url>`` is the webhook url.
6. In the channel you want to receive notifications, do ``>log location``
7. Do ``>notify msg`` to enable notifications through this webhook. ``>notify ping`` will send the notification and also ping you. To disable the webhook and all notifications, do ``>notify none``
8. Personalize your keyword notifier for specific servers/words and more:

----

- **View settings and turn on and off the keyword logging:**
  + ``>log`` - All settings related to keyword logging. Will be mostly empty if nothing is setup yet.
  + ``>log on`` - Turn on keyword logging. (should be on by default)
  + ``>log off`` - Turn off keyword logging.
  + ``>log context <number>`` - set how many messages before the logged message to show when logging a keyword. Default is four.
  + ``>log location`` - sets the channel you typed this in as the log and notification location for the logger (unless you have it set to direct messages)

- **Set up words to log for:**
  + ``>log addkey <word>`` - adds this word (or words) as a keyword. Ex: ``>log addkey appu`` or ``>log addkey kaguya wants to be confessed to``
  + ``>log removekey <word>`` - removes this keyword.

- **Set up which servers you want to get notified for or set it up for all servers:**
  + ``>log add`` - adds the server you are in to be checked for keywords.
  + ``>log remove`` - removes the server from keyword check.
  + ``>log toggle`` - toggle between just the servers you added or all servers. Default is set to all servers so you do not need to add every server.

- **Blacklist users, servers, and words that you don't want to recieve notifications for:**
  + ``>log addblacklist [user] <user>`` - blacklists the user from the keyword notifier. ``<user>`` can be their name + discriminator, a mention, or their user id.
  + ``>log addblacklist [word] <word>`` - blacklists this word from the keyword notifier.
  + ``>log addblacklist [server]`` - blacklists the current server from the keyword notifier.
  + ``>log addblacklist [channel]`` - blacklists the current channel from the keyword notifier.
  + ``>log addblacklist [word] [server] <word>`` - blacklists the current word for only this server (the one you are typing in).
    - Ex: ``overwatch`` is a keyword but you don't want notifs from the Overwatch server. Go to the server and in any channel, type ``>log addblacklist [word] [server] overwatch``.
  + ``>log addblacklist [word] [channel] <word>`` - blacklists the current word for only this channel (the one you are typing in).
  + ``>log removeblacklist [user] <user>`` or ``>log removeblacklist [word] <word>`` etc. - self-explanatory.  

- **Set how you want to receive notifications:**
  + ``>notify msg`` - posts in the keyword notifier channel using the webhook. (default)
  + ``>notify ping`` - posts in the keyword notifier channel but also get pinged when it does so (helpful if you want to see your logs in the recent mentions tab).
  + ``>notify dm`` - recieve via direct message. **This requires the proxy bot to be set up. See below**
  + ``>notify off`` - don't recieve any notifications (keywords will still be logged if keyword logging is on but no notifications will be sent)
 
**Things to note:**

1. Only other people can trigger the log message. You yourself saying a keyword won't log the message.
2. The channel the keyword notifier is logging in (your ``>log location``) is exempt from the keyword search.
3. Bots do not trigger the keyword notifier. Only user accounts can.
4. If the logged message + context is too long, the log message will be split up into multiple messages. These mutiple messages don't use embeds so it won't look as neat, sadly. This shouldn't happen often though.

**Why would I need to blacklist words/servers?**

It's just for convenience. If you have 50+ servers and only a handful that you don't want to log, it would be a hastle to add every one to the ``servers`` list so instead you can just enable all servers and add the few to the blacklist. For words being blacklisted, this is just to allow you to specify more in-depth what kind of messages you are trying to look for with the keyword notifier.

**What if I want to recieve notifications via direct message instead?**

This is possible, but you'll need a **proxy bot** for this. Here's how you can set that up:

1. First, go to the channel where you are getting notifications in and do ``>log location``. This lets the proxy bot know that this is where it should take the logs from to send to you via direct message.
2. Create a Discord bot account and get the bot's token. Then add the bot to the server where you are logging. [Follow these quick steps.](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)
3. Make sure to give the bot read, send, edit messages, and embed permissions in the channel you are keyword logging in.
4. Do ``>notify token <token>`` where ``<token>`` is the token you grabbed in step 1. Make sure you grabbed the **token** not the client secret!
5. Enable the proxy bot and set it to send via direct messages with ``>notify dm``. ``>notify off`` will turn off the proxy bot.

To switch back to the webhook method of posting notifications in channels, just do ``>notify msg`` or ``>notify ping`` again.

## Follow Users:

**Note:** You must set up the [Keyword Notifier](#keyword-notifier) (steps 1-8 at the start of the section) in order to use this feature.

**Set up people to follow and get notified when they post a message:**

- [Enable developer mode](https://i.imgur.com/AmOZHzL.png) in your user settings to copy [user](https://i.imgur.com/7694JCl.png) and [server](https://i.imgur.com/sc74gxG.png) ids.
- ``>log adduser <user_id> | <n>`` - get notified when this user sends a message across any of your servers. The ``<n>`` is the cooldown in minutes before that user posting will notify you again. See below for a more thorough explanation.
    + Ex: ``>log adduser 124910128582361092 | 10`` - I will get notified when user with id ``124910128582361092`` posts a message anywhere with a cooldown of 10 minutes.
- ``>log adduser <user_id> | <server_id> | <n>`` - get notified when this user sends a message in the given server. ``<n>`` is the same as above.
- ``>log removeuser <user_id>`` and ``>log removeuser <user_id> | <server_id>`` - remove the user from all servers or that one server respectively.
- ``>log refresh`` or ``>log refresh <user_id>`` - refresh the notifier for all users or this specific user if ``<user_id>`` is given. Basically allows you to get notified on the very next message from your users. Aka "I need to know where they are posting right now".
- ``>log`` - will show who you are ~~stalking~~ following (keyword settings are at the top and user settings are at the bottom)

**More important information about user following:**

- The cooldown is in minutes but you can go lower than 1, although I wouldn't advise it unless you want to get spam pinged.
- The cooldown is basically a timer that counts down but resets if the user posts again within the count down. Basically, a user must go ``<n>`` time without posting and then the next post will trigger the notification.
- ``adduser`` and ``removeuser`` are directly linked so you can't do something like add a user for all servers and then try to remove them from one server. If you add a user for all, you must remove for all. If you added for one server, you must remove for that server.
- If you are using a channel to recieve notifications (no proxy bot) and want to recieve notifications in a different channel for user follows rather than the same one as the keyword logger, you can do this by setting a second log location ``>log location2`` in this second channel. You will also need a second webhook so create a second webhook for this new channel using the same instructions as in the Keyword Notifier section and then do ``>webhook2 <webhook_url>`` and you should be all set.

## Save Chat Messages

You can only save chat messages in the servers you are logging (see [Keyword Notifier](#keyword-notifier) section above). Use ``>log`` to see what servers are being logged. Every channel in the enabled servers (or every server if all servers is enabled) will have their messages added to logging. The logger holds the latest 25 messages per channel.

- ``>log history <n>`` outputs the last ``<n>`` number of messages from the chat you just used the command in. ``<n>`` can be as large as the ``log_size``. Increase ``log_size`` in ``log_json`` if you want more messages. A screencap of what it looks like:

![img](http://i.imgur.com/snAWT7C.png)
- ``>log history save <n>`` saves the messages to a file and uploads the file instead. This is useful when saving large number of messages.

## Google API

In order to use the ``>i`` command to image search and in order to get more accurate MyAnimeList search results, you will need a Google API key and a Custom Search Engine ID.

Follow these steps to obtain them:

1. Visit the [Google API Console](https://console.developers.google.com/). Once you are in the Console, create a new project.
2. Go to ``Library`` and search ``Custom Search API``. Click it and enable it.
3. Go to ``Credentials`` and click ``create credentials`` and choose ``API Key`` (no need to restrict the key). The value under "Key" is your api key. Paste this into the optional_config.json under ``google_api_key``.
4. Go [here](https://cse.google.com/cse/all) and click ``Add`` and then ``Create`` (if asked to specify a site, just do www.google.com)
5. On the home page of the Custom Search webpage, click on the newly created search engine and change the ``Sites to Search`` option to ``Search the entire web but emphasize included sites``.
6. Make sure the ``Image search`` option is enabled and make sure to click the ``Update`` button at the bottom when you are done with the changes!
6. Go to ``Details`` section and click ``Search Engine ID`` to grab the ID. Copy this and add it for ``custom_search_engine`` in the optional_config.json.

**Note:** Google may take a little while to properly register your key so the search feature may not work right away. If it's still not working after a few hours, then you may have messed up somewhere.

## Other Things to Note
- Free custom search has a limit of 100 searches per day. The commands ``>i`` and ``>mal`` use this search. Still, this should be more than enough but feel free to pay for more if you would like, although I don't think it's needed.
- Custom commands have a lot of other quirks and flexablility. Check the [Custom Commands](#custom-commands) section to see how you can do stuff like add more than one response for a command, get a random response for a command, add commands that have multiple words, etc.

## Acknowledgements

- Thanks to [adjnouobsref](https://github.com/adjnouobsref) for the spoiler tags and various other contributions.
- Used a lot of [Danny's](https://github.com/Rapptz) code for certain parts, especially parsing Google cards and the debugger.
- Used [eye-sigil's](https://github.com/eye-sigil) code for the >repl command.
- Thanks to [IgneelDxD](https://github.com/IgneelDxD) for a lot of suggestions and fixes.