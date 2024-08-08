import discord
import bot_token
import aiosqlite

bot = discord.Bot()

@bot.on_guild_join()
def joined(guild)
    




@bot.slash_command()
async def hello(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")

bot.run(bot_token.token)
