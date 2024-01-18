import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# for dev #
# PROXY = "http://127.0.0.1:1087" 
# DISCORD_KEY = os.getenv("DISCORD_KEY_TEST")

# for production #
PROXY = None
DISCORD_KEY = os.getenv("DISCORD_KEY")

COMMAND_PREFIX = "!"
COGS = [
    "cogs.purge"
]

class KMS(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        
        super().__init__(
            intents = intents,
            command_prefix = COMMAND_PREFIX, 
            case_insensitive = True,
            proxy = PROXY
        )
        
    async def setup_hook(self):
        for cog in COGS:
            await self.load_extension(cog)

        # command to reload cogs 
        @commands.command()
        @commands.is_owner()
        async def reload(ctx, msg):
            try: 
                if msg in COGS:
                    await self.reload_extension(cog)
                    await ctx.channel.send(f"reloaded {cog}")
                else:
                    await ctx.channel.send("no such cog")
                    return
            except Exception as e:
                print(e)
                await ctx.channel.send(f"error reloading cog: {e}")
                return

        self.add_command(reload)

if __name__ == '__main__':
    bot = KMS()
    bot.run(DISCORD_KEY)