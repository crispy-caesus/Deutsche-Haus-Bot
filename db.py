import aiosqlite
from aiosqlite import Error
import asyncio

class Database():

    def __init__(self, db_name: str):
        self.db_name = db_name

    async def list_tables(self):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT name FROM sqlite_master WHERE type = 'table';") as cursor:
                async for row in cursor:
                    print(row)
    
    async def create_tables(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS clubs (
                                    id INTEGER PRIMARY KEY,
                                    channel_name TEXT NOT NULL UNIQUE,
                                    owner INTEGER NOT NULL UNIQUE,
                                    role_id INTEGER NOT NULL UNIQUE);""")
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

    async def create_club(self, channel_name: str, owner: int, role_id: int):
        print(f"DB: received:\n   channel_name: {channel_name}\n   owner: {owner}\n   role_id: {role_id}")
        args = (channel_name, owner, role_id)
        sql = """INSERT INTO clubs (channel_name,owner,role_id)
                 VALUES(?,?,?);"""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(sql, args)
                await db.commit()
        except Error as e:
            print(e)
            return("Club existiert schon")

    async def add_member(self, member: int, owner: int):
        print(f"DB: received:\n   member: {member}\n   owner: {owner}")
        sql = """INSERT INTO members (user_id, club_id)
                 VALUES(?,?);"""
        try:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute("SELECT id FROM clubs WHERE owner = ?;", (owner, )) as cursor:
                    async for row in cursor:
                        args = (member, row[0])
                        await db.execute(sql, args)
                        await db.commit()
        except Error as e:
            print(e)
            return("Member existiert schon")
                
            
            

    
    async def select_clubs(self)-> list:
        clubs = []
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM clubs;") as cursor:
                async for row in cursor:
                    clubs.append(row)
        return clubs


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


