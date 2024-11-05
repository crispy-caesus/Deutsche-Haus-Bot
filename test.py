import db as database
import asyncio

async def error_test(hi="", hey=""):
    print(hi, hey)
    


async def db_reset():
    db = database.Database("1170646611236487208.db")
    await db.create_tables()
    await db.create_id_rows()


async def main():
    await error_test("hallo", "was geht")
    

asyncio.run(main())
