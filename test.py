import db
import asyncio

async def main():
    my_db = db.Database("1170646611236487208.db")
    await my_db.create_tables()
    await my_db.list_tables()
    print(await my_db.select_clubs())
    await my_db.check_if_club_creatable("asdsad", 621759962280099840)

asyncio.run(main())
