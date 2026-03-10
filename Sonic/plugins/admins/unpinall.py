from pyrogram import filters, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
)
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    UserAdminInvalid,
    BadRequest
)
import datetime
from Sonic import app
from Sonic.misc import SUDOERS
from config import adminlist


@app.on_callback_query(filters.regex(r"^unpin"))
async def unpin_callbacc(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    chat_id = CallbackQuery.message.chat.id
    
    if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
        return await CallbackQuery.answer("You dont have rights, baka!", show_alert=True)

    member = await app.get_chat_member(chat_id, user_id)
    if not (member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_pin_messages):
        return await CallbackQuery.answer("You dont have rights, baka!", show_alert=True)
    
    msg_id = CallbackQuery.data.split("=")[1]
    try:
        msg_id = int(msg_id)
    except:
        if msg_id == "yes":
            await client.unpin_all_chat_messages(chat_id)
            textt = "I have unpinned all the pinned messages"
        else:
            textt = "Ok, i wont unpin all the messages"

        await CallbackQuery.message.edit_caption(
            textt,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text="Delete", callback_data="delete_btn=admin")]
                ]
            )
        )
        return
        
    await client.unpin_chat_message(chat_id, msg_id)
    await CallbackQuery.message.edit_caption(
        "unpinned!!", 
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Delete", callback_data="delete_btn=admin")]
            ]
        )
    )

@app.on_message(filters.command(["unpinall"]) & filters.group)
async def unpin_command_handler(client, message):
    chat = message.chat
    chat_id = chat.id
    admin_id = message.from_user.id
    
    if admin_id not in SUDOERS and admin_id not in adminlist.get(chat_id, []):
        return await message.reply_text("Sorry, but you can't do that.")

    if admin_id not in SUDOERS:
        member = await chat.get_member(admin_id)
        if not (member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] and member.privileges.can_pin_messages):
            return await message.reply_text("Sorry, but you can't do that.")
    
    await message.reply_text(
        "Are you sure ? to unpinall message in this group.",
        reply_markup=InlineKeyboardMarkup(
            [   
                [
                    InlineKeyboardButton(text="YES", callback_data="unpinall=yes"),
                    InlineKeyboardButton(text="NO", callback_data="unpinall=no")
                ]
            ]
        )
    )
