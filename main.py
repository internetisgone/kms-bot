import os
import discord
from discord.ext import commands, tasks
# import asyncio
from dotenv import load_dotenv

PROXY = "http://127.0.0.1:1087" 
# PROXY = None
# SERVER_WHITELIST = []

load_dotenv()

def run_bot():
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    if PROXY != None:
        bot = commands.Bot(intents = intents, command_prefix='!', proxy = PROXY)  
    else:
        bot = commands.Bot(intents = intents, command_prefix='!')
    
    @bot.event
    async def on_ready():
         print(f"{bot.user} is running")
        #  test.start()

    # @tasks.loop(seconds=1.0)
    # async def test():
    #     print("retard")

    @bot.command(name="kms") 
    async def delete_msg(ctx, duration):
        await ctx.channel.purge(limit = None, check = lambda msg: not msg.pinned)
        # await ctx.channel.send("earth server has been wiped :)")

    bot.run(os.getenv("DISCORD_KEY"))

if __name__ == '__main__':
    run_bot()