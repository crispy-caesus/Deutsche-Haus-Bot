import db as database
import asyncio

async def main():
    db = database.Database("1170646611236487208.db")
    await db.select_club_by_owner(621759962280099840)

asyncio.run(main())
