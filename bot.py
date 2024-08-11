import discord
import discord.ext.commands
import bot_token
import db as database
import logic

bot = discord.Bot()
role_converter = discord.ext.commands.RoleConverter()
member_converter = discord.ext.commands.MemberConverter()

# ======================= INITIALIZATION ========================== #

@bot.listen()
async def on_guild_join(guild):
    await logic.on_guild_join(guild.id)


# ======================= SETUP ========================= #

@bot.slash_command(description="Gibt alle Commands zurück, die für die Initialisation des Bots nötig sind") 
async def setup(ctx):
    if not ctx.author.guild_permissions.administrator:
        ctx.respond("Du musst Administrator sein, um diesen Command auszuführen")
        return
    await ctx.respond(await logic.setup(ctx.guild.id))

@bot.slash_command(description="Setzt die Booster Rolle intern im Bot")
async def setze_booster_rolle(ctx, booster_rolle):
    if not ctx.author.guild_permissions.administrator:
        ctx.respond("Du musst Administrator sein, um diesen Command auszuführen")
        return
    await ctx.respond(await logic.add_booster_role(ctx.guild.id, int(booster_rolle[3:-1])))

@bot.slash_command(description="Setzt den Verteiler Channel intern im Bot")
async def setze_verteiler_channel(ctx, verteiler_channel_id):
    if not ctx.author.guild_permissions.administrator:
        ctx.respond("Du musst Administrator sein, um diesen Command auszuführen")
        return
    await ctx.respond(await logic.add_distributor_channel(ctx.guild.id, int(verteiler_channel_id)))

@bot.slash_command(description="Setzt die Kategorie, in der die Clubs erstellt werden sollen")
async def setze_club_kategorie(ctx, kategorie_id):
    if not ctx.author.guild_permissions.administrator:
        ctx.respond("Du musst Administrator sein, um diesen Command auszuführen")
        return
    await ctx.respond(await logic.add_club_category(ctx.guild.id, int(kategorie_id)))



"""
@bot.slash_command(description="Füge neue Rollen zu der Datenbank hinzu")
@discord.ext.commands.has_role()
async def
"""

async def get_existing_roles(ctx):
    results = ctx.guild.roles
    return results


# ======================== add club ================================ #

@bot.slash_command(description="Erstellt einen Booster Club")
@discord.ext.commands.has_role(1170646611332956208)
async def club_hinzuftügen(ctx, kanalname, emoji, rollenname, rollenfarbe):
    user = ctx.author.id

    await logic.add_club(kanalname, emoji, rollenname, rollenfarbe, user)

    db = database.Database(f"{ctx.guild.id}.db")
    await db.create_tables()
    check = await db.check_if_club_creatable(kanalname, user)
    if check != None:
        await ctx.respond(check)
        return

    await ctx.guild.create_role(name=rollenname, color=0x5460D9, mentionable=False)

    role = await role_converter.convert(ctx, rollenname)
    channel_name = f"[{emoji}]{kanalname}"
    response = await db.create_club(channel_name, user, role.id)
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

    member = await member_converter.convert(ctx, member)

    response = await db.select_club_by_owner(ctx.author.id)
    if response == None:
        await ctx.respond("Du hast keinen Club")
        return
    role = await role_converter.convert(ctx, str(response))


    await member.add_roles(role)
    await ctx.respond(":white_check_mark:")


@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

# ==================== distributor vc ======================= #

@bot.slash_command(description="Setzt join to create VC")
@discord.ext.commands.has_role(1170646611332956208)
async def verteiler_setzen(kanal_id):
    pass

#@bot.listen()
async def on_voice_state_update(user, before, after):
    if after.channel.id == 1:
        print(f"{user.name} Joined The {after.channel.name} VC")
        print(after.channel.members)



bot.run(bot_token.token)
