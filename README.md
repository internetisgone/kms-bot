# KMS bot
discord bot that periodically deletes old messages in text channels using [purge](https://discordpy.readthedocs.io/en/stable/api.html?highlight=purge#discord.TextChannel.purge)<br>
- custom duration for each channel 
- pinned messages are kept
- purge tasks are kept in a local SQLite database and resumed on bot restart<br>

rest in peace [@AutoDelete#6949](https://github.com/riking/AutoDelete) which inspired this project

## usage
### start or reset purge task in a channel
`@kms_bot_user 2d`<br>
`@kms_bot_user 24h`<br>
`@kms_bot_user 5m`<br>
`@kms_bot_user 30s`<br>
or any custom duration 
### stop purge task in a channel
`@kms_bot_user stop`
### get available commands
`@kms_bot_user help`

## setup and run
python 3.8 or higher is required<br>
### clone this repo
```
git clone https://github.com/internetisgone/kms-bot.git
cd kms-bot
```
### create a bot user
- go to discord developer portal and create a new application<br><br>
- in the "bot" section, copy its token and paste it in `.env`. optionally, uncheck "public bot"<br><br>
- in the "OAuth2 - URL generator" section, set scope to `bot`, and select the `send messages`, `manage messages`, and `read message history` permissions. invite the bot to your server with the link 
- in the "bot" section, set Privileged Gateway Intents for Message Content Intent to on
### run the bot
create and activate a venv
```
# macos and linux
python3 -m venv .venv
source .venv/bin/activate

# windows
py -m venv .venv
.venv\Scripts\activate.bat
```
install requirements
```
pip install -r requirements.txt
```
run the bot
```
# macos and linux
python3 main.py

# windows
py main.py
```

## hosting
hosting platforms with free tier 
- [fly.io](https://fly.io/). it will build the bot from the `Dockerfile`. u need to configure a volume for the sqlite db to work
- [pythonanywhere](https://www.pythonanywhere.com/). afaik it has persistent storage but the machine gets restarted quite often
<br>
vps self-hosting<br>
im using `screen` rn but the proper way to do it would be adding it as a service in `systemd`
