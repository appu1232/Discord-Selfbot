# A Discord selfbot with various commands

A selfbot that has various in-built commands as well as the ability to dynamically add commands using the ``>add`` command on discord. **Note: The in-built command prefix is ``>`` but custom commands use the prefix ``.``**

## Features

- Simple calculator
- Google search (web or image).
- Smart MyAnimeList search of anime and manga/LNs using google custom search (and if that fails, using myanimelist's api for search)
- Ping command that shows the response time.
- Set yourself as afk and message a user telling them you are away if they message/mention you.
- Dynamically add custom commands. Stored in ``commands.json`` which has some sample commands added to start with.
- Quick commands so you can post pointless stuff as fast as possible like ``lenny``, ``shrug``, ``flip``, ``unflip``, and ``comeatmebro``
- Self-destruct your previous message with animated text and a countdown. Yes, it's very pointless and abuses the rate-limit...but it looks cool.

## Setup

Start off by setting up the config.json file:

```json
{
	"my_id" : "",
	"token" : "",
	"google_api_key" : "",
    "custom_search_engine" : "",
	"mal_username" : "",
    "mal_password" : "",
	"set_afk" : "off",
	"afk_message" : ""
}
```

- ``my_id`` - your discord ID
- ``token`` - our token obtained from ``localStorage.token``
- ``google_api_key`` and ``custom_search_engine`` need to be obtained from Google. See **Google API** section below for instructions.
- ``mal_username`` and ``mal_password`` - MyAnimeList username and password which is required in order to do an MAL search. This is required in order to use the MAL API to grab anime/manga information and is not used for anything else. A normal MAL account will suffice.
- ``set_afk`` - does not need to be changed. It defaults to ``off`` and can be changed through Discord by doing ``>setafk on`` or ``>setafk off``.
- ``af_message`` - the message that is sent when ``set_afk`` is enabled and someone pings you in a channel. This can be edited through Discord with the ``>setafkmsg`` cmd.

## All Commands:
- ``>restart`` - restart the bot.
- ``>calc`` - calculator. Ex: ``>calc 44 * (45-15)`` (note: exponents are done with **)
- ``>ping`` - Responds with ``pong`` and also gives the response time.
- ``>g <tags>`` - Google search. ``>g <n> <tags>`` gives the nth result.
- ``>g i <tags>`` - Google image search. ``>g i <n> <tags>`` gives the nth result.
- ``>mal anime <tags>`` or ``>mal manga <tags>`` - Searches MyAnimeList for specified entry. Use ``manga`` for light novels as well.
- ``>l2g <tags>`` - Gives a https://googleitfor.me link with the specified tags for when you want to be a smartass.
- ``>setafk on`` or ``>setafk off`` - Turn the afk message trigger on and off.
- ``>setafkmsg <msg>`` - Set the afk message.
- ``>customcmds`` - List all custom commands.
- ``>add <command> <response>`` or ``>add <command> <response_name> <response> - Add a custom command. See the **Custom Commands** section for more info.
- ``>remove <command>`` or ``>remove <command> <response_name>`` - Remove a custom command. See the **Custom Commands** section for more info.
- ``>d`` or ``>d <seconds>`` - Remove the last message you sent (along with this one). ``>d`` will immediately delete but ``>d <seconds>`` will wait out the number of seconds. It will also repeatedly edit the message and count down the seconds and show a little animation. Very stupid, very unnecessary, but it's pretty funny to see people's reactions. :P

## Things to note:
- Free custom search has a limit of 100 calls per day. This should be more than enough in my opinion but feel free to pay for more if you would like, although I don't think it's needed.
- Try not to keep setafk on for too long or use it too frequently. Technically, responding to someone else's ping with an automated response is not something Discord likes selfbots doing. I highly suggest this be used as a fun gimmick rather than for actual use all the time.
- All commands besides quick commands are invoked with the ``>`` prefix, **however, custom commands use the prefix** ``.``
- The bot sets you to idle when you are not on discord. If you open up discord again, you will be online and you can freely change your status but when you go offline the bot changes it back to idle.
- Custom commands have a lot of other quirks and flexablility. Check the **Custom commands** section below to see how you can do stuff like add more than one response for a command, get a random response for a command, add commands that have multiple words, etc.

## Custom Commands:
There are two types of commands: commands that have a ``string`` as a response and commands that have a ``list`` as a response (multiple possible responses).

**String commands**:
- 90% of the time you will probably be using the ``string`` command type with something like ``.<command>`` to get the response. Ex: ``.hakomari`` leads to the response ``https://myanimelist.net/manga/55215/Utsuro_no_Hako_to_Zero_no_Maria``
- To add a command, you would do ``>add <command> <response>`` and to remove a command, you would do ``>remove <command>``

In order to have multiple responses to one command, you need to use the ``list`` command type:

**List commands**:
- Add a second parameter between the command and the response like so: ``>add <command> <response_name> <response>`` Ex: ``>add kaguya cute http://i.imgur.com/LtdE1zW.jpg``.
- Adding different ``<response_name>`` and ``<response>`` to the same ``<command>`` will append it to the list of responses for that command.
- Invoke a specific response with: ``.<command> <response_name>`` or ``.<command> <index>``
- Random responses: If more than one response name and response are in a command, get a random response with ``.<command>``.
- Removing follows the logical syntax: ``>remove <command> <response_name>`` to remove a specific response from the command and ``>remove <command>`` to remove the entire command.
- **Important Note:** You cannot make a command that was initially a string command into a list command by adding a second response to it. You must remove the string command and add it as a list command.

**Adding commands with more than one word for the command/response_name/response:**

If *any* one of these are multiple words, you must put *all three* in quotes. Ex:
``>add "kaguya" "how cute" "http://i.imgur.com/LtdE1zW.jpg"``
or:
``>"get good" "https://cdn.discordapp.com/attachments/240823952459431936/266807454506024961/lpLiH3n.png"`` etc.


## Google API

In order to use the ``>g`` command to search the web/images and in order to get more accurate MyAnimeList search results, you will need a Google API key and a Custom Search Engine ID.

Follow these steps to obtain them:

1. Use the [Google API Console](https://console.developers.google.com/) to obtain an API key. [Follow these steps](https://developers.google.com/maps/documentation/android-api/signup) if you are not sure how to go about it. Once you have it, paste it into the empty quotes for ``google_api_key``.
2. Add the Custom Search API to the list of APIs.
3. Go [here](https://cse.google.com/cse/all) and click ``Add`` and then ``Create`` (don't change anything in the Add page)
4. On the home page of the Custom Search webpage, click on the newly created search engine and change the ``Sites to Search`` option to ``Search the entire web by emphasize included sites``. You should have no sites included so this will just do a normal google search like we want.
5. Go to ``Details`` section and click ``Search Engine ID`` to grab the ID. Copy this and add it for ``custom_search_engine`` in the config.json.