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
                                    id_type TEXT UNIQUE NOT NULL,
                                    discord_id INTEGER);""")
            await db.commit()

    async def create_id_rows(self):
        id_types = ["booster_role_id", "distributor_channel_id", "new_channel_category_id", "club_role_header_role_id"]
        for id_type in id_types:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute("""INSERT INTO ids (id_type) VALUES(?);""", (id_type,))
                await db.commit()

# ========================= SETUP ============================ #

    async def get_discord_id(self, id_type: str)->Error|None:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT discord_id FROM ids WHERE id_type = ?;", (id_type,)) as cursor:
                async for row in cursor:
                    return(row[0])

    async def add_id(self, id_type: str, discord_id: int):
        async with aiosqlite.connect(self.db_name) as db:
            try:
                await db.execute("""UPDATE ids
                                    SET discord_id = ?
                                    WHERE id_type = ?;""", (discord_id, id_type))
                await db.commit()
            except Error as e:
                print(e)
                return(e)
        return(None)

    async def get_discord_ids(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM ids;") as cursor:
                result = []
                async for row in cursor:
                    result.append(row)
                return result
                    

# =========================== CREATE CLUB =========================== #

    async def get_booster_role_id(self)-> int | None:
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT discord_id FROM ids WHERE id_type = 'booster_role_id';") as cursor:
                id = await cursor.fetchone()
                if id:
                    return(id[0])
                else:
                    return None

    async def select_role_id_by_owner(self, owner_id):
        async with aiosqlite.connect(self.db_name) as db:
            try:
                async with db.execute("SELECT role_id FROM clubs WHERE owner_id = ?;", (owner_id,)) as cursor:
                    return(await cursor.fetchone()[3])
            except Error as e:
                print(e)
                return(e)


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
        #print(f"DB: create_club received:\n   channel_name: {channel_name}\n   owner: {owner}\n   role_id: {role_id}")
        args = (channel_name, owner, role_id, role_name)
        sql = """INSERT INTO clubs (channel_name,owner_id,role_id,role_name)
                 VALUES(?,?,?,?);"""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(sql, args)
                await db.commit()
        except Error as e:
            return(e)

# ============================ EDIT CLUB ========================== #

    async def club_edit(self, owner_id: int, column: str, value: str):

        #print(f"DB: updating club:\n    owner_id: {owner_id}\n    column: {column}\n    value: {value}")
        async with aiosqlite.connect(self.db_name) as db:
            try:
                await db.execute(f"UPDATE clubs SET {column} = ? WHERE owner_id = ?;", (value, owner_id))
                await db.commit()
                return(None)
            except Error as e:
                print(e)
                return(e)

# ============================ add member ================================== # 

    async def add_member(self, member: int, owner: int):
        #print(f"DB: add_member received:\n   member: {member}\n   owner: {owner}")
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
            return(e)


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




    async def get_channel_name_role_name_by_member(self, user_id)->list:
        clubs = []
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT club_id FROM members WHERE user_id = ?;", (user_id,)) as cursor:
                async for club_id in cursor:
                    async with db.execute("SELECT channel_name, role_id, id FROM clubs WHERE id = ?;", (club_id[0], )) as cursor2:
                        async for club in cursor2:
                            clubs.append(club)

        return clubs

    async def get_owner_by_club_id(self, club_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT owner_id FROM clubs WHERE id = ?;", (club_id, )) as cursor:
                result = await cursor.fetchone()
                return (result[0])


    async def delete_club(self, owner_id):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("DELETE FROM clubs WHERE owner_id = ?", (owner_id,))
            await db.commit()
