from Sonic import app
from pyrogram import filters, enums
from pyrogram.types import ChatPermissions 
from Sonic.misc import SUDOERS
from config import adminlist
import asyncio

@app.on_message(filters.command("unmuteall") & filters.group)
async def unmute_all(_, msg):
    chat_id = msg.chat.id   
    user_id = msg.from_user.id
    
    if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
        return await msg.reply_text("Sorry, but you can't do that.")

    bot = await app.get_chat_member(chat_id, "self")
    if not bot.privileges or not bot.privileges.can_restrict_members:
        return await msg.reply_text("I don't have enough permissions to unmute users.")

    mystic = await msg.reply_text(" Unmuting all members...")
    
    async def unmute_member(user_id):
        try:
            await app.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_add_web_page_previews=True,
                    can_invite_users=True
                )
            )
            return True
        except:
            return False

    tasks = []
    async for m in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.RESTRICTED):
        tasks.append(unmute_member(m.user.id))
    
    if not tasks:
        return await mystic.edit("No restricted users found.")

    results = await asyncio.gather(*tasks)
    success = results.count(True)
    
    await mystic.edit(f"Successfully unmuted {success} members.")
