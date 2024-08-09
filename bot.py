import discord
import discord.ext.commands
import bot_token
import db as database
import aiosqlite

bot = discord.Bot()


@bot.slash_command(description="Erstellt einen Booster Club")
@discord.ext.commands.has_role(1170646611332956208)
async def club_hinzuftügen(ctx, kanalname, emoji, rollenname):
    user = ctx.author.id
    db = database.Database(f"{ctx.guild.id}.db")
    await db.create_tables()
    check = await db.check_if_club_creatable(kanalname, user)
    if check != None:
        await ctx.respond(check)
        return

    await ctx.guild.create_role(name=rollenname, color=0x5460D9, mentionable=False)

    role_converter = discord.ext.commands.RoleConverter()
    rolle = await role_converter.convert(ctx, rollenname)
    channel_name = f"[{emoji}]{kanalname}"
    response = await db.create_club(channel_name, user, rolle.id)
    if response == None:
        await ctx.respond(f"{channel_name} created!")
    else:
        await ctx.respond(response)

@bot.slash_command(description="Fügt Member zu eigenem Club hinzu")
async def mitglied_hinzufuegen(ctx, member):
    db = database.Database(f"{ctx.guild.id}.db")
    response = await db.add_member(member[2:-1], ctx.author.id)
    if response != None:
        await ctx.respond(response)
        return

    member_converter = discord.ext.commands.MemberConverter()
    member = await member_converter.convert(ctx, member)

    response = await db.select_club_by_owner(ctx.author.id)
    if response == None:
        await ctx.respond("Du hast keinen Club")
        return
    role_converter = discord.ext.commands.RoleConverter()
    role = await role_converter.convert(ctx, str(response))


    await member.add_roles(role)

    await ctx.respond(":white_check_mark:")

@bot.user_command(name="Say Hello")
async def hi(ctx, user):
    await ctx.respond(f"{ctx.author.mention} says hello to {user.name}!")

@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

bot.run(bot_token.token)
