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
    
    async def create_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS clubs (
                                    id INTEGER PRIMARY KEY,
                                    channel_name TEXT NOT NULL UNIQUE,
                                    owner INTEGER NOT NULL UNIQUE,
                                    role_id INTEGER NOT NULL UNIQUE);""")
            await db.commit()

    async def create_club(self, channel_name: str, owner: int, role_id: int):
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
            

    
    async def select_clubs(self):
        clubs = []
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM clubs;") as cursor:
                async for row in cursor:
                    clubs.append(row)

"""
    async def select_clubs_of_member(self, member: int):
        clubs = []
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute("SELECT * FROM clubs WHERE ;") as cursor:
                async for row in cursor:
                    clubs.append(row)
"""
# seperate users table with user and foreign key club id
# select * where user=... and translate to club



my_db = Database("test.db")
asyncio.run(my_db.create_table())
asyncio.run(my_db.list_tables())
print(asyncio.run(my_db.create_club("test channel", 123123, 12312)))
print(asyncio.run(my_db.select_clubs()))
