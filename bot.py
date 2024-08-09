import discord
import bot_token
import db as database
import aiosqlite

bot = discord.Bot()
#@bot.on_guild_join()
#def joined(guild)
    




@bot.slash_command()
async def hello(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

@bot.slash_command()
async def club_hinzuftügen(ctx, club_name, emoji, rolle):
    db = database.Database(f"{ctx.guild.id}.db")
    await db.create_tables()

    user = ctx.author.id
    channel_name = f"[{emoji}]{club_name}"
    response = await db.create_club(channel_name, user, rolle[3:-1])
    if response == None:
        await ctx.respond(f"{channel_name} created!")
    else:
        await ctx.respond(response)

@bot.slash_command()
async def mitglied_hinzufuegen(ctx, member):
    db = database.Database(f"{ctx.guild.id}.db")
    response = await db.add_member(member[2:-1], ctx.author.id)
    await ctx.respond(":white_check_mark:")

@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")

bot.run(bot_token.token)
