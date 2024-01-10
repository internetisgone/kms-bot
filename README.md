# KMS bot
periodically deletes old messages in a discord text channel using [purge](https://discordpy.readthedocs.io/en/stable/api.html?highlight=purge#discord.TextChannel.purge)<br>
- works across channels and servers
- pinned messages are kept
- purge tasks are kept in a local SQLite database and resumed on bot restart<br>

rest in peace [@AutoDelete#6949](https://github.com/riking/AutoDelete) which inspired this project

## usage
### start or reset purge task in a channel
`!kms 2d`<br>
`!kms 24h`<br>
`!kms 5m`<br>
`!kms 30s`<br>
### stop purge task in a channel
`!kms stop`
### get available commands
`!kms help`

## setup and run
python 3.8 or higher is required<br>
- clone this repo
    ```
    git clone https://github.com/internetisgone/kms-bot.git
    cd kms-bot
    ```
- go to discord developer portal and create a new application 
- in the "bot" section, copy the bot's token and paste it in `.env`. enable the `message content intent` in `privileged gateway intents`
- in the "OAuth2 - URL generator" section, set scope to `bot`, and select the `send messages`, `manage messages`, and `read message history` permissions. invite the bot to your server with the link 
- run the bot<br>
    macos and linux:
    ```
    sh run.sh
    ```
    windows:
    ```
    run.cmd
    ```
## hosting
todo