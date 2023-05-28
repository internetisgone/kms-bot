import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import re
import asyncio
from dotenv import load_dotenv

load_dotenv()

COMMAND_PREFIX = "!"
DEFAULT_DURATION = "2h"
PURGE_INTERVAL = 33 # in seconds

# for dev #
PROXY = "http://127.0.0.1:1087" 
DISCORD_KEY = os.getenv("DISCORD_KEY_TEST")

# for production #
# PROXY = None
# DISCORD_KEY = os.getenv("DISCORD_KEY")

active_tasks = {} # key: channel id, value: task

def run_bot():
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    bot = commands.Bot(intents = intents, command_prefix = COMMAND_PREFIX, proxy = PROXY)  

    @bot.event
    async def on_ready():
        print(f"{bot.user} is running")

    # @tasks.loop(seconds = PURGE_INTERVAL, reconnect = True)
    async def purge_channel(channel, dtime, self_msg_id):
        print(f"kms every {dtime} in channel {channel}")
        await channel.purge(
            limit = None, 
            check = lambda msg: not msg.pinned and not msg.id == self_msg_id, 
            before = datetime.now() - dtime,
            oldest_first = True
        )   

    async def start_purge_task_loop(channel, dtime, self_msg_id):
        # restart task if already running in a certain channel
        if channel.id in active_tasks:
            print(f"restarting task {active_tasks[channel.id]} in channel {channel}")
            active_tasks[channel.id].stop()

        interval = dtime.total_seconds() if dtime.total_seconds() < PURGE_INTERVAL else PURGE_INTERVAL

        new_task = tasks.loop(seconds = interval, reconnect = True)(purge_channel)
        active_tasks[channel.id] = new_task
        new_task.start(channel, dtime, self_msg_id)

    @bot.command(name = "kms") 
    async def set_duration(ctx, duration):
        try:
            # parse duration 
            duration = re.search('\d+[smh]', duration)
            dtime = None
            if not duration:
                # await ctx.channel.send("duration should be a number followed by either `h`, `m`, or `s`")
                duration = DEFAULT_DURATION
            else: 
                duration = duration.group(0)

            num = re.search('\d+', duration)
            if "s" in duration:
                dtime = timedelta(seconds = int(num.group(0)))
            elif "m" in duration:
                dtime = timedelta(minutes = int(num.group(0)))
            else: 
                dtime = timedelta(hours = int(num.group(0)))

            self_msg = await ctx.channel.send(f"messages in this channel will be deleted after {duration}")
            print(dtime) 

            # start task in a certain channel
            await start_purge_task_loop(ctx.channel, dtime, self_msg.id)

        except Exception as e:
            print(e)
            await ctx.channel.send(f"kms failed, {e}")


    bot.run(DISCORD_KEY)

if __name__ == '__main__':
    run_bot()