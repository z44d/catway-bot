import random
import string
import asyncio

from datetime import datetime, timedelta
from catdns.asyncio import get_inbox
from catdns.types import Mail
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode
from typing import TypedDict, List

def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

class TempMail(TypedDict):
    mail: str
    user: int
    expire_date: datetime
    data: list

emails_db: List["TempMail"] = []

def get_random_mail(user_id: int) -> str:
    random_mail = random_string(random.randint(7, 12)) + "@catdns.in"
    emails_db.append(
        {
            "mail": random_mail,
            "user": user_id,
            "expire_date": datetime.now() + timedelta(hours=1),
            "data": []
        }
    )
    return random_mail

async def process_notif(obj: Mail, user: int, mail: str, app: Client) -> "Message":
    messsage = (
        "- Recived new message from : {} <{}> to <{}>\n"
        "- Date: {}\n"
        "- Subject: {}"
    ).format(
        obj.sent_from.user, obj.sent_from.email, mail, obj.date, obj.subject
    )
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Show HTML Content", url="https://email.catdns.in/{}".format(mail.split("@catdns.in")[0]))
            ]
        ]
    )
    try:
        return await app.send_message(
            user,
            messsage,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=ParseMode.DISABLED
        )
    except FloodWait as f:
        await asyncio.sleep(f.value)
    except Exception:
        return False


async def emails_task(app: Client):
    print("TASK STARTED")
    while not await asyncio.sleep(0.5):
        for i in emails_db:
            try:
                if i["expire_date"] <= datetime.now():
                    emails_db.remove(i)
                    continue

                inbox = await get_inbox(i["mail"])

                if inbox.mail_data is not None:
                    for _ in inbox.mail_data:
                        if hash(_.data.content) not in i["data"]:
                            await process_notif(obj=_, user=i["user"], mail=i["mail"], app=app)
                            i["data"].append(hash(_.data.content))

            except Exception as e:
                print("Error: ", str(e))
                continue
