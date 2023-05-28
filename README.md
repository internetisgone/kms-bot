# autodelete-discord-bot

deletes messages in a discord channel after a certain amount of time. supports different settings for multiple channels. pinned messages are kept. uses [purge](https://discordpy.readthedocs.io/en/stable/api.html?highlight=purge#discord.TextChannel.purge).<br>

rest in peace [@AutoDelete#6949](https://github.com/riking/AutoDelete)

## usage
`!kms 24h`<br>
`!kms 30m`<br>
`!kms 1s`<br>

## running your own instance
- install the requirements with `pip3 install -r requirements.txt`
- create a `.env` file using the template below
- go to discord developer portal and create a new application 
- in the "bot" section, copy the bot's token and paste it in `.env`. also enable the `message content intent` in `privileged gateway intents`. optional: uncheck `public bot`
- in the "OAuth2 - URL generator" section, set scope to `bot`, and select the `send messages`, `manage messages`, and `read message history` permissions. generate an invite link 
- invite the bot to your server with the link and run main.py

## .env
```
DISCORD_KEY = "123456"
```
