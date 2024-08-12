import db as database


# ========================= INITIALIZATION ========================= #

async def on_guild_join(guild_id):
    db = database.Database(f"{guild_id}.db")
    await db.create_tables()    

# ========================= SETUP ========================== #

async def setup(guild_id):
    db = database.Database(f"{guild_id}.db")
    booster_role_id = await db.get_discord_id("booster_role_id")
    if booster_role_id == None:
        booster_check = "❌"
    else:
        booster_check = "✅"
    distributor_channel_id = await db.get_discord_id("distributor_channel_id")
    if distributor_channel_id == None:
        distributor_check = "❌"
    else:
        distributor_check = "✅"
    new_channel_category_id = await db.get_discord_id("new_channel_category_id")
    if new_channel_category_id == None:
        category_check = "❌"
    else:
        category_check = "✅"

    return( \
            f"{booster_check} Setze die Booster Rolle mit `/setze_booster_rolle`\n" \
            f"{distributor_check} Setze den Verteiler Channel mit `/setze_verteiler_channel`\n" \
            f"{category_check} Setze die Kategorie, in der, die Clubs erstellt werden sollen mit `/setze_club_kategorie`" \
           )

async def add_booster_role(guild_id: int, booster_role_id: int)-> str:
    db = database.Database(f"{guild_id}.db")
    response = await db.add_id("booster_role_id", booster_role_id)
    if response == "Error":
        return(response)
    else:
        return("✅ Booster Rolle registriert")
    
async def add_distributor_channel(guild_id: int, distributor_channel_id: int)-> str:
    db = database.Database(f"{guild_id}.db")
    response = await db.add_id("distributor_channel_id", distributor_channel_id)
    if response == "Error":
        return(response)
    else:
        return("✅ Verteiler Channel registriert")
  
async def add_club_category(guild_id: int, category_id: int)-> str:
    db = database.Database(f"{guild_id}.db")
    response = await db.add_id("new_channel_category_id", category_id)
    if response == "Error":
        return(response)
    else:
        return("✅ Club Kategorie registriert")
 

# ========================== ADD CLUB ======================== #

async def add_club(guild_id: int, channel_name_without_emoji: str, emoji: str, role_name: str, color: str, owner_id: int, cycle: int):
    # ------------------------- check if club creatable ------------------------ #
    db = database.Database(f"{guild_id}.db")

    match cycle:
        case 1: # check if booster
            return(await db.get_booster_role_id())
            
        case 2: # check for ability to create given club
            existing_club_of_owner = await db.select_club_by_owner(owner_id)
            if existing_club_of_owner != None:
                return("Error! Du hast bereits einen Club")
    
            combined_channel_name = f"「{emoji}」{channel_name_without_emoji}"
            existing_club = await db.select_club_by_channel_name(combined_channel_name)
            if existing_club != None:
                return("Error! Es gibt bereits einen Club mit diesem Kanalnamen")

            existing_club_role = await db.select_club_by_role_name(role_name)
            if existing_club_role != None:
                return("Error! Es existiert bereits ein Club mit diesem Rollennamen")
        
            # create club on discord
            if color[0] == '#':
                color = color[1:]
            try:
                color = int("0x"+color, 16)+0x200
            except:
                return("Error! Farbformat falsch angegeben")

            return(role_name, color)
        
        case 3:
            return(await db.create_club(f"「{emoji}」{channel_name_without_emoji}", owner_id, int(color), role_name))
    

    # role id needed
    

