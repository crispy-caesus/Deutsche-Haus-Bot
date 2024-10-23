import discord
import discord.ext.commands
import asyncio

import bot_token
import db as database
import logic

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
    await logic.on_guild_join(guild.id)
    print(f"LOG: guild {guild} joined")


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
    print(f"LOG: {ctx.author} added {booster_rolle} as booster role")

@bot.slash_command(description="Setzt den Verteiler Channel intern im Bot")
async def setze_verteiler_channel(ctx, verteiler_channel_id):
    if not ctx.author.guild_permissions.administrator:
        ctx.respond("Du musst Administrator sein, um diesen Command auszuführen")
        return
    await ctx.respond(await logic.add_distributor_channel(ctx.guild.id, int(verteiler_channel_id)))
    print(f"LOG: {ctx.author} added {verteiler_channel_id} as distributor channel id")

@bot.slash_command(description="Setzt die Kategorie, in der die Clubs erstellt werden sollen")
async def setze_club_kategorie(ctx, kategorie_id):
    if not ctx.author.guild_permissions.administrator:
        ctx.respond("Du musst Administrator sein, um diesen Command auszuführen")
        return
    await ctx.respond(await logic.add_club_category(ctx.guild.id, int(kategorie_id)))
    print(f"LOG: {ctx.author} added {kategorie_id} as booster role")



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

@bot.slash_command(description="Erstellt einen Booster Club")
async def club_hinzufügen(ctx, kanalname, emoji, rollenname, rollenfarbe):

    emoji = emoji.strip()

    if ctx.author.get_role(await logic.add_club(ctx.guild.id, kanalname, emoji, rollenname, rollenfarbe, ctx.author.id, 1))== None:
        await ctx.respond(":x: Du bist kein Booster")
        return
    response = await logic.add_club(ctx.guild.id, kanalname, emoji, rollenname, rollenfarbe, ctx.author.id, 2)
    if type(response) == str:
        await ctx.respond(response)
        return
    else:
        await ctx.guild.create_role(name = response[0], color = response[1], mentionable = False)

    print(f"LOG: club {kanalname} created by {ctx.author}")


    role = await role_converter.convert(ctx, rollenname)

    await ctx.author.add_roles(role)
    
    await ctx.respond(await logic.add_club(ctx.guild.id, kanalname, emoji, rollenname, role.id, ctx.author.id, 3))
    
    db = database.Database(f"{ctx.guild.id}.db")
    await db.add_member(ctx.author.id, ctx.author.id)
    
    print(f"LOG: role {role} added to {ctx.author}")


# ==================== EDIT CLUBS ====================== #

@bot.slash_command(description="Ändert den Channel Name des Clubs")
async def club_channel_name_aendern(ctx, neuer_name):
    await ctx.respond(await logic.club_change_channel_name(ctx.guild.id, ctx.author.id, neuer_name))

# ========================= dsfsf ======================= #
@bot.slash_command(description="Fügt Member zu eigenem Club hinzu")
async def mitglied_hinzufuegen(ctx, member):
    db = database.Database(f"{ctx.guild.id}.db")
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
    print(f"LOG: added {member} to {role}")


@bot.command(description="Sends the bot's latency.") # this decorator makes a slash command
async def ping(ctx): # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")

# ==================== distributor vc ======================= #

distributor_vcs = []

@bot.event
async def on_voice_state_update(user, before, after):
    if before.channel != after.channel:

        if after.channel:
            db = database.Database(f"{after.channel.guild.id}.db")

            

            if after.channel.id == await db.get_discord_id("distributor_channel_id"):
                print(f"LOG: {user.name} joined {after.channel.name}")
                #print(f"LOG: channel members: {after.channel.members}")
                
               


                db_response = await db.get_channel_name_role_name_by_member(user.id)
                message = "Welchen Club-Kanal willst du öffnen?"
                for i in range(len(db_response)):
                    message += f"\n**{i+1}.** {db_response[i][0]}"

                await after.channel.send(message)
                
                def check(m):
                    return m.author == user and m.channel == after.channel
                

                done = False
                while not done:

                    try:
                        response = await bot.wait_for('message', check=check, timeout=30.0)
                    except asyncio.TimeoutError:
                        await after.channel.send(":x: Zu spät (joine dem Kanal noch einmal, um die Dialogauswahl wieder zu erhalten)")
                        return
                    else:
                        try: 
                            int(response.content)
                        except ValueError:
                            await after.channel.send(":x: Konnte nicht in ganze Zahl umwandeln")
                            continue
                        if int(response.content) <= len(db_response) and int(response.content) > 0:
                            channel_name = db_response[int(response.content)-1][0]

                            category = discord.utils.get(after.channel.guild.categories, id=await db.get_discord_id("new_channel_category_id"))
                            if category is None:
                                print("ERROR: Can't find set new_channel_category on server")

                            role = discord.utils.get(after.channel.guild.roles, id=db_response[int(response.content)-1][1])
                            if role is None:
                                print("ERROR: Can't find club role")

                            bot_member = after.channel.guild.me
                            club_owner = discord.utils.get(after.channel.guild.members, id=await db.get_owner_by_club_id(db_response[int(response.content)-1][2]))


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
                                after.channel.guild.default_role: default_overwrites,
                                bot_member: bot_overwrites,
                                club_owner: club_owner_overwrites,
                                role: club_member_overwrites
                            }


                            voice_channel = await category.create_voice_channel(
                                name = channel_name,
                                overwrites=overwrites
                            )
                            print(f"LOG: new channel {voice_channel} created")
                            distributor_vcs.append(voice_channel.id)
                            print(f"LOG: The List of existing club channels is now: {distributor_vcs}")
                            done = True
                        else:
                            await after.channel.send(":x: Nicht zulässige Zahl")

                if user.voice:
                    await user.move_to(voice_channel)
                    print(f"LOG: moved {user} into {voice_channel}")
        

        if before.channel and before.channel.id in distributor_vcs:
            if len(before.channel.members) == 0:
                await before.channel.delete(reason="Niemand ist mehr verbunden")
                distributor_vcs.remove(before.channel.id)
                print(f"LOG: deleted {before.channel} because it was empty")


bot.run(bot_token.token)
