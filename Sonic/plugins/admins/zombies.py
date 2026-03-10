
from pyrogram import Client, enums, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from Sonic import app
from Sonic.misc import SUDOERS
from config import adminlist
import asyncio
from typing import List

chatQueue: set[int] = set()
stopProcess: bool = False

async def scan_deleted_members(chat_id: int) -> List:
    return [member.user async for member in app.get_chat_members(chat_id) if member.user and member.user.is_deleted]

async def safe_edit(msg: Message, text: str):
    try:
        await msg.edit(text)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await msg.edit(text)
    except Exception:
        pass

@app.on_message(filters.command(["zombies"]) & filters.group)
async def prompt_zombie_cleanup(_: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
        return await message.reply(" | <b>Only admins can execute this command.</b>")

    deleted_list = await scan_deleted_members(message.chat.id)
    if not deleted_list:
        return await message.reply(" | <b>No deleted accounts found in this chat.</b>")

    total = len(deleted_list)
    est_time = max(1, total // 5)

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(" Yes, Clean", callback_data=f"confirm_zombies:{message.chat.id}"),
                InlineKeyboardButton(" Cancel", callback_data="cancel_zombies"),
            ]
        ]
    )

    await message.reply(
        (
            f" | <b>Found `{total}` deleted accounts.</b>\n"
            f" | <b>Estimated cleanup time:</b> `{est_time}s`\n\n"
            "Do you want to clean them?"
        ),
        reply_markup=keyboard,
    )

@app.on_callback_query(filters.regex(r"^confirm_zombies"))
async def execute_zombie_cleanup(_: Client, cq: CallbackQuery):
    global stopProcess
    chat_id = int(cq.data.split(":")[1])
    user_id = cq.from_user.id

    if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
        return await cq.answer(" | Only admins can confirm this action.", show_alert=True)

    if chat_id in chatQueue:
        return await cq.answer(" | Cleanup already in progress.", show_alert=True)

    bot_me = await app.get_chat_member(chat_id, "self")
    if bot_me.status != ChatMemberStatus.ADMINISTRATOR:
        try:
            return await cq.edit_message_text(" | <b>I need admin rights to remove deleted accounts.</b>")
        except:
            return

    chatQueue.add(chat_id)
    deleted_list = await scan_deleted_members(chat_id)
    total = len(deleted_list)

    try:
        status = await cq.edit_message_text(
            f" | <b>Found `{total}` deleted accounts.</b>\n | <b>Starting cleanup...</b>"
        )
    except:
        status = cq.message

    removed = 0

    async def ban_member(user_id):
        try:
            await app.ban_chat_member(chat_id, user_id)
            return True
        except FloodWait as e:
            await asyncio.sleep(e.value)
            return await ban_member(user_id)
        except Exception:
            return False

    tasks = []
    for user in deleted_list:
        if stopProcess:
            break
        tasks.append(ban_member(user.id))

    batch_size = 20
    for i in range(0, len(tasks), batch_size):
        results = await asyncio.gather(*tasks[i:i + batch_size], return_exceptions=True)
        removed += sum(1 for r in results if r is True)
        await safe_edit(status, f" | <b>Removed {removed}/{total} deleted accounts...</b>")
        await asyncio.sleep(2)

    chatQueue.discard(chat_id)
    await safe_edit(status, f" | <b>Successfully removed `{removed}` out of `{total}` zombies.</b>")

@app.on_message(filters.command(["admins", "staff"]) & filters.group)
async def list_admins(_: Client, message: Message):
    try:
        owners, admins = [], []
        async for m in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if m.user.is_bot:
                continue
            if m.status == ChatMemberStatus.OWNER:
                owners.append(m.user)
            else:
                admins.append(m.user)

        txt = f"<b>Group Staff  {message.chat.title}</b>\n\n"
        owner_line = owners[0].mention if owners else "<i>Hidden</i>"
        txt += f" Owner\n {owner_line}\n\n Admins\n"

        if not admins:
            txt += " <i>No visible admins</i>"
        else:
            for i, adm in enumerate(admins):
                branch = "" if i == len(admins) - 1 else ""
                txt += f"{branch} {'@'+adm.username if adm.username else adm.mention}\n"
        txt += f"\n | <b>Total Staff</b>: {len(owners) + len(admins)}"
        await app.send_message(message.chat.id, txt)
    except FloodWait as e:
        await asyncio.sleep(e.value)

@app.on_message(filters.command("bots") & filters.group)
async def list_bots(_: Client, message: Message):
    try:
        bots = [b.user async for b in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS)]
        txt = f"<b>Bot List  {message.chat.title}</b>\n\n Bots\n"
        for i, bt in enumerate(bots):
            branch = "" if i == len(bots) - 1 else ""
            txt += f"{branch} @{bt.username}\n"
        txt += f"\n | <b>Total Bots</b>: {len(bots)}"
        await app.send_message(message.chat.id, txt)
    except FloodWait as e:
        await asyncio.sleep(e.value)