import discord
import discord.ext.commands
import asyncio
from varname import nameof
import emoji

import bot_token
import db as database

# ======================== STARTUP =========================== #

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

role_converter = discord.ext.commands.RoleConverter()
member_converter = discord.ext.commands.MemberConverter()

# ======================= INITIALIZATION ========================== #

@bot.event
async def on_ready():
    print(f'LOG: bot has logged in as {bot.user}')

@bot.listen()
async def on_guild_join(guild):
    db = await init_db(guild)
    await db.create_tables()
    print(f"LOG: guild {guild} joined")


# ====================== DB INIT ========================= #
async def init_db(ctx, guild=None)-> database.Database:
    if guild:
        return database.Database(f"{guild.id}.db")
    return database.Database(f"{ctx.guild.id}.db")


# ======================== ERROR HANDLING ============================= #

async def dm(ctx, message: str, err):
    user = await bot.fetch_user(621759962280099840)
    if user:
        messageDraft = message
        if err != None:
            messageDraft += "\n```{err}```"
        try:
            await user.send(messageDraft)
            await ctx.send("Der Entwickler wurde kontaktiert und wird sich sobald wie möglich darum kümmern") 
        except discord.Forbidden:
            print(f"{ctx.guild.id} | ERROR: Can't DM user")
            await ctx.send("Bitte kontaktiere die Serverleitung")
    else:
        print(f"{ctx.guild.id} | ERROR: Can't find user to DM")
        await ctx.send("Bitte kontaktiere die Serverleitung")


async def error(ctx, message: str, err = None):
    decoratedMessage = f"{ctx.guild.id} | ERROR: {message}\n{err}"
    print(decoratedMessage)
    await dm(ctx, decoratedMessage, err=err)
    
    await ctx.send(":x: Interner Fehler")


async def log(ctx, message: str):
    decoratedMessage = f"{ctx.guild.id} | LOG: {message}"
    print(decoratedMessage)


async def is_admin(ctx):
    if not ctx.author.guild_permissions.administrator:
        ctx.respond(":x: Du musst Administrator sein, um diesen Command auszuführen")
        return False
    else:
        return True



# ======================= SETUP ========================= #

@bot.slash_command(description="Gibt alle Commands zurück, die für die Initialisation des Bots nötig sind") 
async def setup(ctx):
    if await is_admin(ctx) == False:
        return

    db = await init_db(ctx)
    ids = await db.get_discord_ids()
    
    checks = []
    for id in ids:
        if id[2] == None:
            checks.append("❌")
        else:
            checks.append("✅")

    await ctx.respond( \
            f"{checks[0]} Setze die Booster Rolle mit `/{nameof(setze_booster_rolle)}`\n" \
            f"{checks[1]} Setze den Verteiler Channel mit `/{nameof(setze_verteiler_channel)}`\n" \
            f"{checks[2]} Setze die Kategorie, in der die Clubs erstellt werden sollen mit `/{nameof(setze_club_kategorie)}`\n" \
            f"{checks[3]} Setze die Rolle, welche als Clubrollenheader dient mit `/{nameof(setze_clubrollenheader_rolle)}`" \
           )
    return


@bot.slash_command(description="Setzt die Booster Rolle intern im Bot")
async def setze_booster_rolle(ctx, booster_rolle):
    if await is_admin(ctx) == False:
        return

    db = await init_db(ctx)
    err = await db.add_id("booster_role_id", booster_rolle[3:-1]) # [3:-1] to remove @<> around role ping
    if err:
        await error(ctx, "Set-Booster-Role: DB error", err)
        return

    await ctx.respond("✅ Booster Rolle registriert")
    await log(ctx, f"{ctx.author} added {booster_rolle} as booster role")
    return


@bot.slash_command(description="Setzt den Verteiler Channel intern im Bot")
async def setze_verteiler_channel(ctx, verteiler_channel_id):
    if await is_admin(ctx) == False:
        return

    db = await init_db(ctx)
    err = await db.add_id("distributor_channel_id", verteiler_channel_id) 
    if err:
        await error(ctx, "Set-Distributor-Channel: DB error", err)
        return

    await ctx.respond("✅ Verteiler Channel registriert")
    await log(ctx, f"{ctx.author} added {verteiler_channel_id} as distributor channel id")
    return


@bot.slash_command(description="Setzt die Kategorie, in der die Clubs erstellt werden sollen")
async def setze_club_kategorie(ctx, kategorie_id):
    if await is_admin(ctx) == False:
        return
    db = await init_db(ctx)
    err = await db.add_id("new_channel_category_id", kategorie_id) 
    if err:
        await error(ctx, "Set-New-Channel-Category: DB error", err)
        return

    await ctx.respond("✅ Club Kategorie regisitriert")
    await log(ctx, f"{ctx.author} added {kategorie_id} as booster role")


@bot.slash_command(description="Setzt die Rolle für den Clubrollen-Header")
async def setze_clubrollenheader_rolle(ctx, clubrollenheader_rolle: str):
    if await is_admin(ctx) == False:
        return

    clubrollenheader_rolle = clubrollenheader_rolle.strip()

    db = await init_db(ctx)
    err = await db.add_id("club_role_header_role_id", int(clubrollenheader_rolle[3:-1]))
    if err != None:
        await error(ctx, "Database error when adding club role header role id", err)
        return
    
    await ctx.respond(f"✅ Clubrollenheader {clubrollenheader_rolle} registriert")



"""
@bot.slash_command()
async def get_existing_roles(ctx):
    results = ctx.guild.roles
    print(results)
"""


@bot.slash_command()
async def test(ctx):
    await ctx.guild.create_role(name = "hi", color=int("0x"+("#5460D9"[1:]), 16)+0x200, mentionable = False)
    await ctx.respond("hi")

# ======================== ADD CLUB ================================ #

async def check_club_parameters(ctx, db: database.Database, channelName="", channelEmoji="", roleName="", roleColor=""):
    if channelEmoji != "":
        if len(channelEmoji) != 1:
            ctx.respond("❌ Error! Das Emoji-Feld darf nicht länger oder kürzer als 1 sein")
            return 
        if emoji.is_emoji(channelEmoji) != True:
            ctx.respond("❌ Error! Das Emoji-Feld muss mit einem Emoji gefüllt werden")
            return 

    if channelName != "":
        if emoji.emoji_count(channelName) > 0:
            ctx.respond("❌ Error! Der Kanalname darf keine Emojis enthalten")
            return 

        combined_channel_name = f"「{channelEmoji}」{channelName}"
        existing_club = await db.select_club_by_channel_name(combined_channel_name)
        if existing_club != None:
            ctx.respond("❌ Error! Es gibt bereits einen Club mit diesem Kanalnamen")
            return

    if roleName != "":
        existing_club_role = await db.select_club_by_role_name(roleName)
        if existing_club_role != None:
            ctx.respond("❌ Error! Es existiert bereits ein Club mit diesem Rollennamen")
            return 

    if roleColor != "":
        if roleColor[0] == '#':
            roleColor = roleColor[1:]
        try:
            roleColor = int("0x"+roleColor, 16)
        except:
            return("❌ Error! Farbformat falsch angegeben")

    return(roleName, roleColor)


@bot.slash_command(description="Erstellt einen Booster Club")
async def club_hinzufügen(ctx, kanalname, kanalemoji, rollenname, rollenfarbe):
    db = await init_db(ctx)
    kanalemoji = kanalemoji.strip()

    boosterRoleId = await db.get_booster_role_id()
    if boosterRoleId == None:
        await error(ctx, "Role-Creation: No booster role id foundin DB")
        return
    if ctx.author.get_role(boosterRoleId) == None:
        await ctx.respond(":x: Du bist kein Booster")
        return

    if await db.select_role_id_by_owner(ctx.author.id) != None:
        await ctx.respond("❌ Error! Du hast bereits einen Club")
        return

    check_return = await check_club_parameters(ctx, db, kanalname, kanalemoji, rollenname, rollenfarbe)
    if check_return != None:
        roleName, roleColor = check_return
        createdRole = await ctx.guild.create_role(name = roleName, color = roleColor, mentionable = False)
        if createdRole == None:
            await error(ctx, "Role-Creation: Couldn't create role on discord")
            return
        err = await db.create_club(f"「{kanalemoji}」{kanalname}", ctx.author.id, createdRole.id, roleName)
        if err:
            await error(ctx, "Role-Creation: Couldn't create new role in DB", err)
            return
        await log(ctx, f"club {kanalname} created by {ctx.author}")

        await ctx.author.add_roles(createdRole)
        await db.add_member(ctx.author.id, ctx.author.id)
        await log(ctx, f"Role {createdRole} added to {ctx.author}")

        await ctx.respond(f"✅ Club `「{kanalemoji}」{kanalname}` erstellt!")


# ==================== EDIT CLUBS ====================== #

@bot.slash_command(description="Ändern eines Paramaters seines Clubs")
async def club_editieren(ctx, kanalname="", kanalemoji="", rollenname="", rollenfarbe=""):
    db = await init_db(ctx)
    owner_id = ctx.author.id
    if kanalname != "":
        await db.club_edit(owner_id, "channel_name", kanalname)
    if kanalemoji != "":
        pass
    if rollenname != "":
        pass
    if rollenfarbe != "":
        pass

# ========================= dsfsf ======================= #
@bot.slash_command(description="Fügt Member zu eigenem Club hinzu")
async def mitglied_hinzufuegen(ctx, member):
    db = await init_db(ctx)
    response = await db.add_member(member[2:-1], ctx.author.id)
    if response != None:
        await ctx.respond(response)
        return

    member = await member_converter.convert(ctx, member)

    response = await db.select_role_id_by_owner(ctx.author.id)
    if response == None:
        await ctx.respond("Du hast keinen Club")
        return
    role = discord.utils.get(ctx.guild.roles, id=response)


    await member.add_roles(role)
    await ctx.respond(":white_check_mark:")
    await log(ctx, f"Added {member} to {role}")


@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

# ==================== distributor vc ======================= #

async def send_club_list(ctx, user, db_response):
    clubs = ""

    for i in range(len(db_response)):
        clubs += f"\n**{i+1}.** {db_response[i][0]}"                    # create a new numbered line for every club

    if clubs.strip() == "":
        await ctx.send(f":x: {user.name}, du bist in keinen Clubs")     # if no clubs
        return
    else:
        await ctx.send(f" {user.name}, welchen Club-Kanal willst du öffnen?" + clubs)

async def get_and_check_user_response(ctx, user, db_response):
    def check(m):
        return m.author == user and m.channel == ctx
    
    cycle = 1
    while cycle < 3:

        try:
            response = await bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send(":x: Zu spät (joine dem Kanal noch einmal, um die Dialogauswahl wieder zu erhalten)")
            return
        else:
            try: 
                int(response.content)
            except ValueError:
                await ctx.send(":x: Konnte nicht in ganze Zahl umwandeln")
                continue
            if int(response.content) > len(db_response) and int(response.content) <= 0:
                await ctx.send(":x: Nicht zulässige Zahl")
            else:
                return response
        
        cycle += 1

    ctx.send(":x: Zu viele Versuche, trete dem Channel erneut bei, um noch einmal auszuwählen")
    return None

    
async def gather_arguments_for_channel_creation(ctx, db, db_response, userResponse):
    channel_name = db_response[int(userResponse.content)-1][0]

    new_channel_category_id = await db.get_discord_id("new_channel_category_id")
    category = discord.utils.get(ctx.guild.categories, id=new_channel_category_id)
    if category is None:
        await error(ctx, f"Distributor-Channel: Can't find new channel category ({new_channel_category_id}) on Discord")

    roleId = db_response[int(userResponse.content)-1][1]
    role = discord.utils.get(ctx.guild.roles, id=roleId)
    if role is None:
        await error(ctx, f"Distributor-Channel: Can't find club role ({roleId}) on Discord")

    bot_member = ctx.guild.me

    clubOwnerId = await db.get_owner_by_club_id(db_response[int(userResponse.content)-1][2])
    club_owner = discord.utils.get(ctx.guild.members, id=clubOwnerId)
    if club_owner is None:
        await error(ctx, f"Distributor-Channel: Can't find club owner ({clubOwnerId}) on Discord")

    return (channel_name, category, role, bot_member, club_owner)


async def create_permission_overwrites(ctx, role, bot_member, club_owner):
    bot_overwrites = discord.PermissionOverwrite (
        move_members = True,
        view_channel = True,
        manage_channels = True
    )

    club_member_overwrites = discord.PermissionOverwrite (
        view_channel = True
    )

    club_owner_overwrites = discord.PermissionOverwrite (
        manage_channels = True,
        mute_members = True,
        deafen_members = True,
        move_members = True
    )

    default_overwrites = discord.PermissionOverwrite (
        view_channel = False
    )

    overwrites = {
        ctx.guild.default_role: default_overwrites,
        bot_member: bot_overwrites,
        club_owner: club_owner_overwrites,
        role: club_member_overwrites
    }

    return overwrites


async def distributor_channel(user, after, db):
    ctx = after.channel             # ctx is distributor channel
    await log(ctx, f"{user.name} joined distributor channel {ctx.name}")
    db_response = await db.get_channel_name_role_name_by_member(user.id)
    
    await send_club_list(ctx, user, db_response)
    userResponse = await get_and_check_user_response(ctx, user, db_response)
    if userResponse == None:
        return

    channel_name, category, role, bot_member, club_owner = await gather_arguments_for_channel_creation(ctx, db, db_response, userResponse)
    overwrites = await create_permission_overwrites(ctx, role, bot_member, club_owner) 

    voice_channel = await category.create_voice_channel(
        name = channel_name,
        overwrites=overwrites
    )
    await log(ctx, f"New channel {voice_channel} created")
    distributor_vcs.append(voice_channel.id)
    await log(ctx, f"The List of existing club channels is now: {distributor_vcs}")
    
    if user.voice:
        await user.move_to(voice_channel)
        await log(ctx, f"Moved {user} into {voice_channel}")


distributor_vcs = []

@bot.event
async def on_voice_state_update(user, before, after):

    if before.channel != after.channel:     # actually moved channels in some way
        if after.channel:                   # moved and didn't leave
            db = await init_db(after.channel)
            if after.channel.id == await db.get_discord_id("distributor_channel_id"):
                await distributor_channel(user, after, db)



    if before.channel and before.channel.id in distributor_vcs:         # if old channel exists and is a distributor vc
        if len(before.channel.members) == 0:
            await before.channel.delete(reason="Niemand ist mehr verbunden")
            distributor_vcs.remove(before.channel.id)
            await log(before.channel, f"Deleted {before.channel} because it was empty")

                
@bot.slash_command(description="Löscht eigenen Club")
async def club_löschen(ctx, owner = None):
    db = database.Database(f"{ctx.guild.id}.db")
    if owner == None:
        owner = ctx.author.id
    else:
        owner = owner[2:-1]

    club_role_id = await db.select_role_id_by_owner(owner)

    if club_role_id == None:
        await ctx.respond(":x: Der angegebene Benutzer besitzt keinen Club")
        return
    
    err = await db.delete_club(owner)
    if err != None:
        await error(ctx, "Club-Deletion: Club from {owner} could not be deleted from the db", err)
        return
    else:
        print(f"LOG: club from {owner} has been deleted from the db")

    role = discord.utils.get(ctx.guild.roles, id=club_role_id)
    
    # Check if the role exists
    if role == None:
        await error(ctx, f"Club-Deletion: Role {club_role_id} could not be found")
        return
    
    # Attempt to delete the role
    try:
        await role.delete()
        await ctx.respond(f":white_check_mark: Rolle {role.name} und Club von <@{owner}> wurden gelöscht")
        print(f"LOG: role '{role.name}' has been deleted by {ctx.author}")
    except discord.Forbidden:
        await error(ctx, f"Club-Deletion: No permission to delete role ({club_role_id})")
        return
    except discord.HTTPException as e:
        await error(ctx, "Club-Deletion: Error when deleting role", e)
        return





bot.run(bot_token.token)
