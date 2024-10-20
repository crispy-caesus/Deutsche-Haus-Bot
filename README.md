# Deutsche Haus Bot

This was just supposed to be a quick "script" of a bot, so the code is in no way any way close to readable.

## Functionality

- boosters can create a club (role with name and color, channel name adhering the dh channel naming scheme)
- club owners can add members to their club
- club members can join a join-to-create voice channel
    - they can select one of their clubs in a message interaction with the bot in the text channel of said voice channel
    - upon selecting one, a voice channel, only accessible to its club's members is created
    - they are moved to the new voice channel
    - once the created voice channel is empty, it is deleted

## Deployment
Create a bot applicationon on https://discord.com/developers/applications and give the bot read message intents.
Add the bot to your server and give it at least `Manage Channels`, `Manage Roles`, `Move Members`, `Send Messages` and `View Channels` permissions

Add your bot's token into a bot_token.py file in a format of `token = ""`

Install the necessary **dependencies** with `pip install -r requirements.txt`

Run the bot with `python bot.py`
