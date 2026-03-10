from datetime import datetime
import html
import random

from pyrogram import enums, filters
from pyrogram.types import Message

from Sonic import app
from Sonic.core.call import Sonic
from Sonic.utils import bot_sys_stats
from Sonic.utils.decorators.language import language
from Sonic.utils.inline import supp_markup
from config import BANNED_USERS, STARK_IMG


@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    response = await message.reply_photo(
        photo=random.choice(STARK_IMG),
        caption=_["ping_1"].format(html.escape(app.first_name)),
        parse_mode=enums.ParseMode.HTML,
    )
    pytgping = await Sonic.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_caption(
        caption=_["ping_2"].format(resp, html.escape(app.first_name), UP, RAM, CPU, DISK, pytgping),
        reply_markup=supp_markup(_),
        parse_mode=enums.ParseMode.HTML,
    )
