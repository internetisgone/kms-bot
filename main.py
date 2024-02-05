import os
import discord
from discord import app_commands
from discord.ext import tasks
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

PURGE_INTERVAL = 33 # in seconds
MAX_DURATION = timedelta(days = 3333)
MIN_DURATION = timedelta(seconds = 1)
HELP_TEXT = """
HOW TO KMS
                                       
purge old messages:           
`/kms 30s`
`/kms 5m`
`/kms 24h`
`/kms 2d`
or any custom duration

stop purge task: 
`/stop`
                                       
get help:
`/help`
"""

active_tasks = {} # key: channel id, value: task

async def purge_channel(channel, dtime, self_msg_id):
    try:
        await channel.purge(
            limit = 100,
            check = lambda msg: not msg.pinned and not msg.id == self_msg_id, 
            before = datetime.now() - dtime,
            oldest_first = True
        )  
    except discord.errors.Forbidden as e:
        print(f"403 error purging channel {channel.id}: {e}") 
        if e.text == "Missing Access":
            stop_task(channel.id)
            await delete_task_db(channel.id)
            print(f"deleted task in channel {channel.id}")
        elif e.text == "Missing Permissions":
            stop_task(channel.id)
            await delete_task_db(channel.id)
            await channel.send("Σ(°Д°) kms stopped: missing permissions.")
    except Exception as e:
        print(f"error purging channel {channel.id}: {e}") 

async def set_purge_task_loop(channel, dtime, interaction):
    stop_task(channel.id) # stop prev task if there's any

    if dtime < MIN_DURATION:
        dtime = MIN_DURATION
        formatted_duration = get_formatted_duration(MIN_DURATION)
        await channel.send(f"minimun duration to kms is {formatted_duration}.")
    if dtime > MAX_DURATION:
        dtime = MAX_DURATION
        formatted_duration = get_formatted_duration(MAX_DURATION)
        await channel.send(f"maximum duration to kms is {formatted_duration}.") 

    interval = dtime.total_seconds() if dtime.total_seconds() < PURGE_INTERVAL else PURGE_INTERVAL

    # start the task
    new_task = tasks.loop(seconds = interval, reconnect = True)(purge_channel)
    formatted_duration = get_formatted_duration(dtime)
    self_msg = None
    if interaction:
        await interaction.response.send_message(f"messages older than {formatted_duration} will be deleted on a rolling basis in this channel.")
        self_msg = await interaction.original_response()
    else:
        self_msg = await channel.send(f"messages older than {formatted_duration} will be deleted on a rolling basis in this channel.")
    new_task.start(channel, dtime, self_msg.id)

    # update dict and db
    active_tasks[channel.id] = new_task 
    await update_task_db(channel.id, dtime.total_seconds())

async def get_all_tasks_db():
    tasks = None
    try: 
        db = await aiosqlite.connect("kms.db") # create kms.db if it doesn't exist
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
        await db.close()

    except Exception as e:
        print(e)

async def delete_task_db(channel_id):
    try:
        db = await aiosqlite.connect("kms.db")
        cursor = await db.cursor()
        await cursor.execute(f"DELETE FROM kms_tasks WHERE channel_id = {channel_id}") 
        await db.commit()
        await db.close()
    except Exception as e:
        print(e)

def stop_task(channel_id):
    if channel_id in active_tasks:
        # print(f"stopping task {active_tasks[channel_id]} in channel {channel_id}")
        active_tasks[channel_id].stop()

def get_formatted_duration(dtime):
    seconds = int(dtime.total_seconds())
    if seconds % 86400 == 0:
        days = seconds//86400
        return str(days) + " days" if days > 1 else str(days) + " day"
    elif seconds % 3600 == 0:
        hours = seconds//3600
        return str(hours) + " hours" if hours > 1 else str(hours) + " hour"
    elif seconds % 60 == 0:
        minutes = seconds//60
        return str(minutes) + " minutes" if minutes > 1 else str(minutes) + " minute"
    else:
        return str(seconds) + " seconds" if seconds > 1 else str(seconds) + " second"

def run_bot():
    bot = discord.Client(
        intents = discord.Intents.default(), 
        proxy = PROXY
    ) 
    tree = app_commands.CommandTree(bot)

    @bot.event
    async def on_ready():
        try:
            synced = await tree.sync()
            print(f"synced {len(synced)} commands")
        except Exception as e:
            print(f"failed to sync command tree: {str(e)}")
        
        print(f"{datetime.utcnow()} {bot.user} is online")

        # check the db for existing tasks 
        tasks = await get_all_tasks_db()

        # start tasks
        for task in tasks:
            try:
                channel_id, dtime = task
                channel = bot.get_channel(channel_id)
                dtime = timedelta(seconds = dtime)
                if (not channel or channel.type != discord.ChannelType.text):
                    # delete invalid data 
                    print(f"channel {channel_id} is not a text channel or kms has no access to it")             
                    await delete_task_db(channel_id)
                else: 
                    print(f"starting purge task in guild {channel.guild} channel {channel_id} with dtime {dtime}")
                    await set_purge_task_loop(channel, dtime, None)
                # todo 
                # sleep
            except Exception as e:
                print(f"error starting task in channel {channel_id}: {e}")
                # delete data
                
        # set status
        game = discord.Game("/kms")
        await bot.change_presence(status = discord.Status.online, activity = game)

    # slash command to set duration
    @tree.command(name = "kms") 
    async def on_kms(
        interaction: discord.Interaction,
        duration: str,
    ):
        if interaction.channel.type != discord.ChannelType.text:
            await interaction.response.send_message("Σ(°Д°) kms only supports text channels for now.")
            return
        
        try:
            # parse duration 
            duration = duration.lower()
            duration = re.search('\d+[smhd]', duration)
            dtime = None
            if not duration:
                # invalid input
                await interaction.response.send_message(f"Σ(°Д°) invalid duration. type `/help` to see supported formats.")
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

                # start / restart task in a channel
                await set_purge_task_loop(interaction.channel, dtime, interaction)
                print(f"{datetime.utcnow()} updated purge task in guild {interaction.guild}")

        except Exception as e:
            print(e)
            await interaction.channel.send(f"failed to kms: {e}")

    # slash command to stop purge task
    @tree.command(name = "stop") 
    async def on_stop(
        interaction: discord.Interaction,
    ):
        if interaction.channel.id in active_tasks:
            stop_task(interaction.channel.id)                 
            await delete_task_db(interaction.channel.id) # remove from db
            del active_tasks[interaction.channel.id] # remove from dict
            await interaction.response.send_message("kms stopped.")
        else: 
            await interaction.response.send_message("nothing to stop in this channel.")


    # slash command for help
    @tree.command(name = "help") 
    async def on_help(
        interaction: discord.Interaction,
    ):
        await interaction.response.send_message(HELP_TEXT)

    bot.run(DISCORD_KEY)

if __name__ == '__main__':
    run_bot()