# KMS bot
discord bot that periodically deletes old messages in text channels using [purge](https://discordpy.readthedocs.io/en/stable/api.html?highlight=purge#discord.TextChannel.purge)<br>
- minimal permissions (no message content access)
- purge durations are kept in a local SQLite database and resumed on bot restart
- pinned messages are left untouched<br>

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
### get channel status
`@kms_bot_user status`
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
go to discord developer portal and create a new application<br><br>
in the "bot" section, copy its token and paste it in `.env.example`, and rename the file to `.env`. optionally, uncheck "public bot"<br><br>
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

## hosting recommendations

### hosting platforms with free tier 
- [fly.io](https://fly.io/). it will build the bot from the `Dockerfile`. u need to configure a volume for the sqlite db to work
- [pythonanywhere](https://www.pythonanywhere.com/). afaik it has persistent storage but the machine gets restarted quite often

### vps self-hosting
(optional) add the bot as a systemd service so it starts automatically on system startup

create a `kms.service` config file at `/etc/systemd/system/` 
```
nano /etc/systemd/system/kms.service
```

the config should look something like this
```
[Unit]
Description=kms discord bot
After=network-online.target

[Service]
Type=simple
User=[your username here]
Restart=on-failure
Environment="PATH=/path/to/your/bot/.venv/bin"
WorkingDirectory=/path/to/your/bot
ExecStart=python3 main.py

[Install]
WantedBy=multi-user.target
```

start the service 
```
systemctl daemon-reload
systemctl start kms
```
check service status 
```
systemctl status kms
```