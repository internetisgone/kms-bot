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
### clone this repo
```
git clone https://github.com/internetisgone/kms-bot.git
cd kms-bot
```
### create a bot user
go to discord developer portal and create a new application<br><br>
in the "bot" section, copy the bot's token and paste it in `.env`. enable the `message content intent` in `privileged gateway intents`<br><br>
in the "OAuth2 - URL generator" section, set scope to `bot`, and select the `send messages`, `manage messages`, and `read message history` permissions. invite the bot to your server with the link 
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
<br>
if u are too lazy to type all of the above, simply start the bot by running a script:

```
# macos and linux
sh run.sh

# windows
run.cmd
```

## hosting
todo