import random
import string
import asyncio

from datetime import datetime, timedelta
from catway.asyncio import CatMail
from catway.types import Mail
from catway.utils import convert_to_str
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode
from typing import TypedDict, List

def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

class TempMail(TypedDict):
    mail: "str"
    user: "int"
    expire_date: "datetime"
    data: "list"
    cat_mail: "CatMail"

emails_db: List["TempMail"] = []

def get_random_mail(user_id: int) -> str:
    random_mail = random_string(random.randint(7, 12)) + "@catway.org"
    emails_db.append(
        {
            "mail": random_mail,
            "user": user_id,
            "expire_date": datetime.now() + timedelta(hours=1),
            "data": [],
            "cat_mail": CatMail(random_mail)
        }
    )
    return random_mail

async def process_notif(obj: Mail, user: int, mail: str, app: Client) -> "Message":
    messsage = (
        "- Recived new message from : {} <{}> to <{}>\n"
        "- Date: {}\n"
        "- Subject: {}"
    ).format(
        obj.sender_name, obj.sender_email, mail, convert_to_str(obj.created_at), obj.subject
    )
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Show HTML Content", url=obj.view_link)
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
    while not await asyncio.sleep(2.5):
        for i in emails_db:
            try:
                if i["expire_date"] <= datetime.now():
                    emails_db.remove(i)
                    continue

                async for mail in i["cat_mail"].get_inboxes():
                    if mail.id not in i["data"]:
                        await process_notif(
                            mail, i["user"], i["mail"], app
                        )
                        i["data"].append(mail.id)
            except Exception as e:
                print(e)
                continue
