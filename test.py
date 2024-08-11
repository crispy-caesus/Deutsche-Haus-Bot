import db
import bot
import asyncio

async def main():
    print(await bot.get_existing_roles())

asyncio.run(main())
