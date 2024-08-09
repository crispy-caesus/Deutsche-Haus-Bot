import db
import asyncio

async def main():
    my_db = db.Database("test.db")
    await my_db.create_tables()
    await my_db.list_tables()
    print(await my_db.create_club("test channel2", 123, 23))
    print(await my_db.select_clubs())
    await my_db.add_member(3, 23)
    print(await my_db.select_clubs_of_member(3))

asyncio.run(main())
