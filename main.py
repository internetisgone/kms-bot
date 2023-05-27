import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import re
import asyncio
from dotenv import load_dotenv

PROXY = "http://127.0.0.1:1087" 
DEFAULT_DURATION = "2h"
# PROXY = None
# SERVER_WHITELIST = []

load_dotenv()

def run_bot():
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    bot = None
    if PROXY != None:
        bot = commands.Bot(intents = intents, command_prefix='!', proxy = PROXY)  
    else:
        bot = commands.Bot(intents = intents, command_prefix='!')
    
    @bot.event
    async def on_ready():
        print(f"{bot.user} is running")

    @bot.command(name="kms") 
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

            await ctx.channel.send(f"messages in this channel will be deleted after {duration}")
            print(dtime)

            @tasks.loop(seconds = dtime.total_seconds(), reconnect = True)
            async def delete_msg():
                async for msg in ctx.channel.history():
                    time_diff = (discord.utils.utcnow() - msg.created_at).total_seconds()
                    # ignore pinned msg and msg sent by the bot itself
                    if time_diff > dtime.total_seconds() and not msg.pinned and not msg.author == bot.user: 
                        await msg.delete()
                        # await ctx.channel.send(f"deleting msg {msg}")
                        await asyncio.sleep(0.5) # avoid rate limits
            
            # start the task
            delete_msg.start()

            # await ctx.channel.purge(
            #     limit = None, 
            #     check = lambda msg: not msg.pinned, 
            #     before = datetime.now() - dtime,
            #     oldest_first = True
            # ) 
            # await ctx.channel.send("earth server has been wiped :)")

        except Exception as e:
            print(e)
            await ctx.channel.send(f"kms failed, {e}")


    bot.run(os.getenv("DISCORD_KEY"))

if __name__ == '__main__':
    run_bot()