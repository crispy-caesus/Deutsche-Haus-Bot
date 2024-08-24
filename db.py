import aiosqlite
from aiosqlite import Error

class Database():

    def __init__(self, db_name: str):
        self.db_name = db_name

# ====================== INITIALIZATION ======================== #
# could be done more flexibly somehow probably, receiving the schema from the logic.py, but ehhhhhhhhhhh (also not databse independent then)
    async def create_tables(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS clubs (
                                    id INTEGER PRIMARY KEY,
                                    channel_name TEXT NOT NULL UNIQUE,
                                    owner_id INTEGER NOT NULL UNIQUE,
                                    role_id INTEGER NOT NULL UNIQUE,
                                    role_name TEXT NOT NULL UNIQUE);""")
            await db.commit()                                                        
            await db.execute("""CREATE TABLE IF NOT EXISTS members (
                                    id INTEGER PRIMARY KEY,
                                    user_id INTEGER NOT NULL,
                                    club_id INTEGER NOT NULL,
                                    UNIQUE(user_id, club_id) ON CONFLICT REPLACE,
                                    FOREIGN KEY (club_id)
                                        REFERENCES clubs (id)
                                            ON UPDATE CASCADE
                                            ON DELETE CASCADE);""")
            await db.commit()
            await db.execute("""CREATE TABLE IF NOT EXISTS existing_roles (
                                    id INTEGER PRIMARY KEY,
                                    roles TEXT NOT NULL UNIQUE);""")
            await db.commit()
            await db.execute("""CREATE TABLE IF NOT EXISTS ids (
                                    id INTEGER PRIMARY KEY,
                                    id_type INTEGER UNIQUE NOT NULL,
                                    discord_id INTEGER NOT NULL);""")
            await db.commit()

# ========================= SETUP ============================ #

    async def get_discord_id(self, id_type: str):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT discord_id FROM ids WHERE id_type = ?;", (id_type,)) as cursor:
                async for row in cursor:
                    return(row[0])

    async def add_id(self, id_type: str, discord_id: int):
        async with aiosqlite.connect(self.db_name) as db:
            try:
                await db.execute("""INSERT INTO ids (id_type, discord_id)
                                     VALUES(?,?);""", (id_type, discord_id))
                await db.commit()
            except Error as e:
                print(e)
                return("Error")
        return(None)

# =========================== CREATE CLUB =========================== #

    async def get_booster_role_id(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT discord_id FROM ids WHERE id_type = 'booster_role_id';") as cursor:
                return((await cursor.fetchone())[0])

    async def select_club_by_owner(self, owner_id):
        async with aiosqlite.connect(self.db_name) as db:
            try:
                async with db.execute("SELECT * FROM clubs WHERE owner_id = ?;", (owner_id,)) as cursor:
                    return(await cursor.fetchone())
            except Error as e:
                print(e)
                return("❌ Error! Du besitzt keinen Club")


    async def select_club_by_channel_name(self, channel_name):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM clubs WHERE channel_name = ?;", (channel_name,)) as cursor:
                async for row in cursor:
                    return row

    async def select_club_by_role_name(self, role_name):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM clubs WHERE role_name = ?;", (role_name,)) as cursor:
                async for row in cursor:
                    return row


    async def create_club(self, channel_name: str, owner: int, role_id: int, role_name: str):
        print(f"DB: received:\n   channel_name: {channel_name}\n   owner: {owner}\n   role_id: {role_id}")
        args = (channel_name, owner, role_id, role_name)
        sql = """INSERT INTO clubs (channel_name,owner_id,role_id,role_name)
                 VALUES(?,?,?,?);"""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(sql, args)
                await db.commit()
        except Error as e:
            print(e)
            return("❌ Error!")

# ============================ EDIT CLUB ========================== #

    async def club_edit(self, owner_id: int, column, value):

        print(f"DB: updating club:\n    owner_id: {owner_id}\n    column: {column}\n    value: {value}")
        async with aiosqlite.connect(self.db_name) as db:
            try:
                await db.execute(f"UPDATE clubs SET {column} = ? WHERE owner_id = ?;", (value, owner_id))
                await db.commit()
                return(None)
            except Error as e:
                print(e)
                return("❌ Error!")

# ============================ add member ================================== # 

    async def add_member(self, member: int, owner: int):
        print(f"DB: received:\n   member: {member}\n   owner: {owner}")
        sql = """INSERT INTO members (user_id, club_id)
                 VALUES(?,?);"""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute("SELECT id FROM clubs WHERE owner_id = ?;", (owner, )) as cursor:
                    async for row in cursor:
                        args = (member, row[0])
                        await db.execute(sql, args)
                        await db.commit()
        except Error as e:
            print(e)
            return("❌ Error!")


    async def select_role_id_by_owner(self, member: int):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT role_id FROM clubs WHERE owner_id = ?;", (member,)) as cursor:
                async for row in cursor:
                    return(row[0])

# ============================= list member clubs ========================== #

    async def select_clubs_of_member(self, member: int)-> list:
        clubs = []
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute("SELECT club_id FROM members WHERE user_id = ?;", (member, )) as cursor:
                    async for row in cursor:
                        async with db.execute("SELECT channel_name, role_id FROM clubs WHERE id = ?;", (row[0], )) as cursor2:
                            async for row2 in cursor2:
                                clubs.append(row2)
        except Error as e:
            print(e)
        return clubs

# ============================= list random stuff ================================ # 

    async def list_tables(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT name FROM sqlite_master WHERE type = 'table';") as cursor:
                async for row in cursor:
                    print(row)

    
    async def select_clubs(self)-> list:
        clubs = []
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM clubs;") as cursor:
                async for row in cursor:
                    clubs.append(row)
        return clubs


