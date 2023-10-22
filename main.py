import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import aiosqlite

load_dotenv()

# for dev #
# PROXY = "http://127.0.0.1:1087" 
# DISCORD_KEY = os.getenv("DISCORD_KEY_TEST")

# for production #
PROXY = None
DISCORD_KEY = os.getenv("DISCORD_KEY")

COMMAND_PREFIX = "!"
DEFAULT_DURATION = "2h"
PURGE_INTERVAL = 33 # in seconds

active_tasks = {} # key: channel id, value: task

async def purge_channel(channel, dtime, self_msg_id):
    await channel.purge(
        limit = None, # todo might need to set a limit 
        check = lambda msg: not msg.pinned and not msg.id == self_msg_id, 
        before = datetime.now() - dtime,
        oldest_first = True
    )   

async def set_purge_task_loop(channel, dtime):
    stop_task(channel.id) # stop prev task if there's any
    interval = dtime.total_seconds() if dtime.total_seconds() < PURGE_INTERVAL else PURGE_INTERVAL

    new_task = tasks.loop(seconds = interval, reconnect = True)(purge_channel)
    self_msg = await channel.send(f"messages in this channel will be deleted after {str(dtime)}.")
    new_task.start(channel, dtime, self_msg.id)

    active_tasks[channel.id] = new_task

async def get_all_tasks_db():
    tasks = None
    try: 
        db = await aiosqlite.connect("kms.db") # creates kms.db if it doesn't exist
        cursor = await db.cursor()
        await cursor.execute("CREATE TABLE IF NOT EXISTS kms_tasks(channel_id INTEGER PRIMARY KEY, purge_duration_seconds INTEGER)") # channel id is unique across servers 
        await db.commit()

        await cursor.execute("SELECT * FROM kms_tasks")
        tasks = await cursor.fetchall()
        await db.close()
    except Exception as e:
        print(e)
    finally:
        return tasks

async def update_task_db(channel_id, dtime_seconds):
    try: 
        db = await aiosqlite.connect("kms.db")
        cursor = await db.cursor()

        # check if channel id is already in table
        await cursor.execute(f"SELECT channel_id FROM kms_tasks WHERE channel_id = {channel_id}")
        result = await cursor.fetchone()
        if result == None:
            await cursor.execute(f"INSERT INTO kms_tasks (channel_id, purge_duration_seconds) VALUES ({channel_id}, {dtime_seconds})")
        else:
            await cursor.execute(f"UPDATE kms_tasks SET purge_duration_seconds = {dtime_seconds} WHERE channel_id = {channel_id}")
        await db.commit()

        # show table
        # await cursor.execute("SELECT * FROM kms_tasks")
        # rows = await cursor.fetchall()
        # print("----------- updated kms_tasks -----------")
        # for row in rows:
        #     print(row)

        await db.close()

    except Exception as e:
        print(e)

async def delete_task_db(channel_id):
    try:
        db = await aiosqlite.connect("kms.db")
        cursor = await db.cursor()
        await cursor.execute(f"DELETE FROM kms_tasks WHERE channel_id = {channel_id}") 
        await db.commit()

        # show table
        # await cursor.execute("SELECT * FROM kms_tasks")
        # rows = await cursor.fetchall()
        # print("----------- updated kms_tasks -----------")
        # for row in rows:
        #     print(row)

        await db.close()
    except Exception as e:
        print(e)

def stop_task(channel_id):
    if channel_id in active_tasks:
        print(f"stopping task {active_tasks[channel_id]} in channel {channel_id}")
        active_tasks[channel_id].stop()

def run_bot():
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    bot = commands.Bot(intents = intents, command_prefix = COMMAND_PREFIX, proxy = PROXY)  

    @bot.event
    async def on_ready():
        print(f"{bot.user} is running")

        # check the db for existing tasks 
        tasks = await get_all_tasks_db()

        # start tasks
        for task in tasks:
            channel_id, dtime = task
            channel = bot.get_channel(channel_id)
            dtime = timedelta(seconds = dtime)
            print(f"found task in channel {channel_id} with dtime {dtime}")

            await set_purge_task_loop(channel, dtime)
                        
    @bot.command(name = "kms") 
    async def set_duration(ctx, usr_input):
        try:
            if "cancel" in usr_input:
                # cancel task
                if ctx.channel.id in active_tasks:
                    stop_task(ctx.channel.id)                 
                    await delete_task_db(ctx.channel.id) # remove from db
                    del active_tasks[ctx.channel.id] # remove from dict
                    await ctx.channel.send("kms cancelled")
                else: 
                    await ctx.channel.send("nothing to cancel in this channel")

            else: 
                # try parse duration 
                duration = re.search('\d+[smhd]', usr_input)
                dtime = None
                if not duration:
                    duration = DEFAULT_DURATION
                else: 
                    duration = duration.group(0)

                num = re.search('\d+', duration)
                if "s" in duration:
                    dtime = timedelta(seconds = int(num.group(0)))
                elif "m" in duration:
                    dtime = timedelta(minutes = int(num.group(0)))
                elif "d" in duration:
                    dtime = timedelta(days = int(num.group(0)))
                else: 
                    dtime = timedelta(hours = int(num.group(0)))

                # todo limit dtime max value

                # start / restart task in a channel
                await set_purge_task_loop(ctx.channel, dtime)
                # update db
                await update_task_db(ctx.channel.id, dtime.total_seconds())

        except Exception as e:
            print(e)
            await ctx.channel.send(f"failed to kms: {e}")

    bot.run(DISCORD_KEY)

if __name__ == '__main__':
    run_bot()