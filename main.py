import asyncio
import logging

from pyrogram import Client, idle, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from config import API_HASH, API_ID, BOT_TOKEN
from util import get_random_mail, emails_task

app = Client(
    "Catdns",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    skip_updates=True,
    sleep_threshold=30
)

logging.basicConfig(level=logging.INFO)

@app.on_message(filters.command("start") & filters.private)
async def welcome_message(_, m: Message) -> Message:
    message = (
        "Welcome to **[Catdns emails bot](mail.catdns.in)** 👋.\n"
        "This bot made to make temp mail on **catdns.in** domain.\n"
        "To get random temp mail send : /temp\n\n"
        "Powered by: **DevZaid.t.me**"
    )
    return await m.reply(
        text=message,
        quote=True,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

@app.on_message(filters.command("temp") & filters.private)
async def get_temp_mail(_, m: Message) -> Message:
    random_mail = get_random_mail(m.from_user.id)
    return await m.reply(
        "This is your random e-mail: {}\n\nIt's only available for 1 hour".format(random_mail),
        quote=True
    )

async def main():
    await app.start()
    asyncio.create_task(emails_task(app=app))
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=loop)

    loop.run_until_complete(main())