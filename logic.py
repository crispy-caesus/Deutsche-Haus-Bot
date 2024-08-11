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

async def add_club(channel_name_without_emoji, emoji, role_name, color, owner_id):
    # ------------------------- check if club creatable ------------------------ #
    existing_club_of_owner = db.get_club_by_owner(owner_id)
    if existing_club_of_owner == None:
        return("Du hast bereits einen Club")
    
    combined_channel_name = f"「{emoji}」{channel_name_without_emoji}"
    existing_club = db.check_if_channel_exists(combined_channel_name)
    if existing_club != None:
        return("Es gibt bereits einen Club mit diesem Kanalnamen")

    existing_club_role = bot.check_if_role_exists(role_name)
    if existing_club_role != None:
        return("Es existiert bereits ein Club mit diesem Rollennamen")

    existing_role

    # role id needed
    

