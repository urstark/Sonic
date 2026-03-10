import platform
import html
from sys import version as pyver

import psutil
from pyrogram import __version__ as pyrover
from pyrogram import enums, filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message, CallbackQuery
from pytgcalls.__version__ import __version__ as pytgver
from ntgcalls import __version__ as ntgver

import config
from Sonic import app
from Sonic.core.userbot import assistants
from Sonic.misc import SUDOERS, mongodb
from Sonic.plugins import ALL_MODULES
from Sonic.utils.database import (
    get_served_chats,
    get_served_users,
    get_sudoers,
    is_autoend,
    is_autoleave,
)
from Sonic.utils.decorators.language import language, languageCB
from Sonic.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS

async def answer_callback(query: CallbackQuery, text: str = None, alert: bool = False):
    try:
        await query.answer(text, show_alert=alert)
    except:
        pass

@app.on_message(filters.command(["stats", "gstats"]) & filters.group & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    is_sudo = message.from_user.id in SUDOERS
    markup = stats_buttons(_, is_sudo)
    
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=_["gstats_2"].format(html.escape(app.first_name)),
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML,
    )


@app.on_callback_query(filters.regex("stats_back") & ~BANNED_USERS)
@languageCB
async def home_stats(client, CallbackQuery, _):
    await answer_callback(CallbackQuery)
    is_sudo = CallbackQuery.from_user.id in SUDOERS
    markup = stats_buttons(_, is_sudo)
    
    try:
        await CallbackQuery.edit_message_caption(
            caption=_["gstats_2"].format(html.escape(app.first_name)),
            reply_markup=markup,
            parse_mode=enums.ParseMode.HTML,
        )
    except:
        pass


@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    await answer_callback(CallbackQuery)
    markup = back_stats_buttons(_)
    try:
        await CallbackQuery.edit_message_caption(
            caption=_["gstats_1"].format(html.escape(app.first_name)),
            parse_mode=enums.ParseMode.HTML,
        )
    except:
        pass
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    text = _["gstats_3"].format(
        html.escape(app.first_name),
        len(assistants),
        len(BANNED_USERS),
        served_chats,
        served_users,
        len(ALL_MODULES),
        len(SUDOERS),
        await is_autoleave(),
        config.DURATION_LIMIT_MIN,
        await is_autoend(),
    )
    media = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text, parse_mode=enums.ParseMode.HTML)
    try:
        await CallbackQuery.edit_message_media(media=media, reply_markup=markup)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, 
            caption=text, 
            reply_markup=markup,
            parse_mode=enums.ParseMode.HTML,
        )
@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def bot_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id not in SUDOERS:
        return await answer_callback(CallbackQuery, _["gstats_4"], alert=True)   
    await answer_callback(CallbackQuery)
    markup = back_stats_buttons(_)    
    try:
        await CallbackQuery.edit_message_caption(
            caption=_["gstats_1"].format(html.escape(app.first_name)),
            parse_mode=enums.ParseMode.HTML,
        )
    except:
        pass
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"  
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)} GHz"
        else:
            cpu_freq = f"{round(cpu_freq, 2)} MHz"
    except:
        cpu_freq = "Failed to fetch"
    hdd = psutil.disk_usage("/")
    total = str(hdd.total / (1024.0**3))[:4]
    used = str(hdd.used / (1024.0**3))[:4]
    free = str(hdd.free / (1024.0**3))[:4]
    try:
        call = await mongodb.command("dbstats")
        datasize = str(call["dataSize"] / 1024)[:6]
        storage = str(call["storageSize"] / 1024)
        collections = call["collections"]
        objects = call["objects"]
    except:
        datasize = "0"
        storage = "0"
        collections = "0"
        objects = "0"

    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    version_info = f"{pytgver} (Ntg {ntgver})"
    text = _["gstats_5"].format(
        html.escape(app.first_name),
        len(ALL_MODULES),
        platform.system(),
        ram,
        p_core,
        t_core,
        cpu_freq,
        pyver.split()[0],
        pyrover,
        version_info,
        total,
        used,
        free,
        served_chats,
        served_users,
        len(BANNED_USERS),
        len(await get_sudoers()),
        datasize,
        storage,
        collections,
        objects,
    )
    media = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text, parse_mode=enums.ParseMode.HTML)  
    try:
        await CallbackQuery.edit_message_media(media=media, reply_markup=markup)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, 
            caption=text, 
            reply_markup=markup,
            parse_mode=enums.ParseMode.HTML,
        )