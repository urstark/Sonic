from pyrogram import filters
from pyrogram.types import Message

from Sonic import app
from Sonic.misc import SUDOERS
from Sonic.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)


@app.on_message(filters.command(["ac"]) & SUDOERS)
async def active_vc(_, message: Message):
    achats = len(await get_active_chats())
    vchats = len(await get_active_video_chats())
    await message.reply_text(f"<b>Active voice chats:</b>\n\nVoice: {achats}\nVideo: {vchats}")


@app.on_message(filters.command(["activevc", "activevoice"]) & SUDOERS)
async def activevc(_, message: Message):
    mystic = await message.reply_text("Fetching active voice chats...")
    served_chats = await get_active_chats()
    text = ""
    j = 0
    for x in served_chats:
        chat = await app.get_chat(x)
        try:
            title = chat.title
        except:
            await remove_active_chat(x)
            continue
        try:
            if chat.username:
                user = chat.username
                text += f"<b>{j + 1}.</b> <a href=https://t.me/{user}>{title}</a> [<code>{x}</code>]\n"
            else:
                text += (
                    f"<b>{j + 1}.</b> {title} [<code>{x}</code>]\n"
                )
            j += 1
        except:
            continue
    if not text:
        await mystic.edit_text(f"No active voice chats found.")
    else:
        await mystic.edit_text(
            f"<b>List of currently active voice chats:</b>\n\n{text}",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command(["activev", "activevideo"]) & SUDOERS)
async def activevi_(_, message: Message):
    mystic = await message.reply_text("Fetching active video chats...")
    served_chats = await get_active_video_chats()
    text = ""
    j = 0
    for x in served_chats:
        chat = await app.get_chat(x)
        try:
            title = chat.title
        except:
            await remove_active_video_chat(x)
            continue
        try:
            if chat.username:
                user = chat.username
                text += f"<b>{j + 1}.</b> <a href=https://t.me/{user}>{title}</a> [<code>{x}</code>]\n"
            else:
                text += (
                    f"<b>{j + 1}.</b> {title} [<code>{x}</code>]\n"
                )
            j += 1
        except:
            continue
    if not text:
        await mystic.edit_text(f"No active voice chats on {app.mention}.")
    else:
        await mystic.edit_text(
            f"<b>List of current active video chats:</b>\n\n{text}",
            disable_web_page_preview=True,
        )
