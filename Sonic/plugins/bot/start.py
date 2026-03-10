import asyncio
import random
import time
import html

from pyrogram import filters
from pyrogram.enums import ChatType, ChatAction, ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    InputMediaPhoto
)
from py_yt import VideosSearch

import config
from Sonic import app
from Sonic.misc import _boot_
from Sonic.plugins.sudo.sudoers import sudoers_list
from Sonic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Sonic.utils.decorators.language import LanguageStart
from Sonic.utils.formatters import get_readable_time
from Sonic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# Assets 
EMOJIOS = ["❤️", "😁", "👀", "⚡️", "🕊", "❤️🔥", "💅", "👻",]

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # 1. Reaction to the User's message
    try:
        await message.react(random.choice(EMOJIOS))
    except:
        pass

    # 2. Set Bot Status to Typing
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    # 4. Layer 2: Separate "Starting" Message
    _text = "Hiee Sweetie"
    starting_msg = await message.reply_text(f"{_text[0]}")
    for i in range(1, len(_text)):
        try:
            await asyncio.sleep(0.1)
            await starting_msg.edit_text(f"{_text[:i+1]}")
        except Exception:
            pass
    try:
        await starting_msg.edit_text(f"{_text} <emoji id='6226413607974868029'>✨</emoji>")
    except:
        pass
    await asyncio.sleep(0.6)
    await starting_msg.delete()

    # 6. Main Start Logic (Deep Links)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            return await message.reply_photo(
                photo=random.choice(config.STARK_IMG),
                caption=_["help_1"].format(config.SUPPORT_GROUP),
                reply_markup=keyboard,
            )

        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=(
                        f"{message.from_user.mention} checked <b>sudo list</b>.\n\n"
                        f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                        f"<b>Username:</b> @{message.from_user.username}"
                    ),
                )
            return

        if name.startswith("inf"):
            m = await message.reply_text("Searching song info...")
            query = name.replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_8"], url=link),
                        InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_GROUP),
                    ]
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            return

    # Standard Main Start Panel
    out = private_panel(_)
    
    await message.reply_photo(
        photo=random.choice(config.STARK_IMG),
        caption=_["start_2"].format(
            message.from_user.mention, 
            app.mention
        ),
        reply_markup=InlineKeyboardMarkup(out),
        parse_mode=ParseMode.HTML,
    )

    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=(
                f"{message.from_user.mention} started the bot.\n\n"
                f"<b>User ID:</b> <code>{message.from_user.id}</code>\n"
                f"<b>Username:</b> @{message.from_user.username}"
            ),
        )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    out = start_panel(_)
    uptime = int(time.time() - _boot_)

    await message.reply_photo(
        photo=random.choice(config.STARK_IMG),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
        parse_mode=ParseMode.HTML,
    )
    await add_served_chat(message.chat.id)


@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_cb(client, query: CallbackQuery):
    language = await get_lang(query.message.chat.id)
    _ = get_string(language)

    out = private_panel(_)
    try:
        await query.message.edit_media(
            media=InputMediaPhoto(
                media=random.choice(config.STARK_IMG),
                caption=_["start_2"].format(
                    query.from_user.mention, 
                    app.mention
                ),
            ),
            reply_markup=InlineKeyboardMarkup(out),
        )
    except:
        await query.message.edit_caption(
            caption=_["start_2"].format(
                query.from_user.mention, 
                app.mention
            ),
            reply_markup=InlineKeyboardMarkup(out),
        )


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_GROUP,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                await message.reply_photo(
                    photo=random.choice(config.STARK_IMG),
                    caption=_["start_3"].format(
                        html.escape(member.first_name if member.id == app.id else message.from_user.first_name),
                        app.mention,
                        html.escape(message.chat.title),
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)