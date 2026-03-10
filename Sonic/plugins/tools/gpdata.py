
from pyrogram import enums
from pyrogram.enums import ChatType
from pyrogram import filters, Client
from Sonic import app
from config import OWNER_ID, adminlist
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from Sonic.misc import SUDOERS

# ------------------------------------------------------------------------------- #

@app.on_message(filters.command("pin") & filters.group)
async def pin(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
        return
    
    replied = message.reply_to_message
    chat_title = message.chat.title
    chat_id = message.chat.id
    user_id = message.from_user.id
    name = message.from_user.mention
    
    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply_text("This command works only in groups.")
    elif not replied:
        await message.reply_text("Reply to a message to pin it.")
    else:
        user_stats = await app.get_chat_member(chat_id, user_id)
        if user_stats.privileges.can_pin_messages and message.reply_to_message:
            try:
                await message.reply_to_message.pin()
                await message.reply_text("Successfully pinned message.")
            except Exception as e:
                await message.reply_text(str(e))


@app.on_message(filters.command("pinned"))
async def pinned(_, message):
    chat = await app.get_chat(message.chat.id)
    if not chat.pinned_message:
        return await message.reply_text("No pinned messages found !")
    try:        
        await message.reply_text("Here's the latest pinned message.",reply_markup=
        InlineKeyboardMarkup([[InlineKeyboardButton(text="View Message",url=chat.pinned_message.link)]]))  
    except Exception as er:
        await message.reply_text(er)


# ------------------------------------------------------------------------------- #

@app.on_message(filters.command("unpin") & filters.group)
async def unpin(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
        return
        
    replied = message.reply_to_message
    chat_title = message.chat.title
    chat_id = message.chat.id
    user_id = message.from_user.id
    name = message.from_user.mention
    
    if message.chat.type == enums.ChatType.PRIVATE:
        await message.reply_text("This command works only in groups.")
    elif not replied:
        await message.reply_text("Reply to a message to unpin it.")
    else:
        user_stats = await app.get_chat_member(chat_id, user_id)
        if user_stats.privileges.can_pin_messages and message.reply_to_message:
            try:
                await message.reply_to_message.unpin()
                await message.reply_text("Successfully unpinned message.")
            except Exception as e:
                await message.reply_text(str(e))

# --------------------------------------------------------------------------------- #

@app.on_message(filters.command("removephoto") & filters.group)
async def deletechatphoto(_, message):
      chat_id = message.chat.id
      user_id = message.from_user.id
      
      if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
          return
      msg = await message.reply_text("Processing....")
      admin_check = await app.get_chat_member(chat_id, user_id)
      if message.chat.type == enums.ChatType.PRIVATE:
           await msg.edit("This command works only in groups.") 
      try:
         if admin_check.privileges.can_change_info:
             await app.delete_chat_photo(chat_id)
             await msg.edit("Successfully deleted group photo \n {}".format(message.from_user.mention))    
      except:
          await msg.edit("You don't have permission to delete group photo.")


# --------------------------------------------------------------------------------- #

@app.on_message(filters.command("setphoto") & filters.group)
async def setchatphoto(_, message):
      chat_id = message.chat.id
      user_id = message.from_user.id
      
      if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
          return
          
      reply = message.reply_to_message
      chat_id = message.chat.id
      user_id = message.from_user.id
      msg = await message.reply_text("Processing....")
      admin_check = await app.get_chat_member(chat_id, user_id)
      if message.chat.type == enums.ChatType.PRIVATE:
           await msg.edit("This command works only in groups.") 
      elif not reply:
           await msg.edit("Please reply to a message to set it as group photo.")
      elif reply:
          try:
             if admin_check.privileges.can_change_info:
                photo = await reply.download()
                await message.chat.set_photo(photo=photo)
                await msg.edit_text("Successfully set group photo \nBy {}".format(message.from_user.mention))
             else:
                await msg.edit("Something went wrong, try again.")
     
          except:
              await msg.edit("You don't have permission to set group photo.")


# --------------------------------------------------------------------------------- #

@app.on_message(filters.command("settitle") & filters.group)
async def setgrouptitle(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
        return
        
    reply = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("Processing....")
    if message.chat.type == enums.ChatType.PRIVATE:
          await msg.edit("This command works only in groups.")
    elif reply:
          try:
            title = message.reply_to_message.text
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
               await message.chat.set_title(title)
               await msg.edit("Successfully set group title \nBy {}".format(message.from_user.mention))
          except AttributeError:
                await msg.edit("You don't have permissions to set group title.")   
    elif len(message.command) >1:
        try:
            title = message.text.split(None, 1)[1]
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
               await message.chat.set_title(title)
               await msg.edit("Successfully set group title \nBy {}".format(message.from_user.mention))
        except AttributeError:
               await msg.edit("You don't have permissions to set group title.")
          

    else:
       await msg.edit("Please reply to a message to set it as group title.")


# --------------------------------------------------------------------------------- #



@app.on_message(filters.command(["setdescription", "setdiscription"]) & filters.group)
async def setg_description(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id not in SUDOERS and user_id not in adminlist.get(chat_id, []):
        return
        
    reply = message.reply_to_message
    chat_id = message.chat.id
    user_id = message.from_user.id
    msg = await message.reply_text("Processing....")
    if message.chat.type == enums.ChatType.PRIVATE:
        await msg.edit("This command works only in groups.")
    elif reply:
        try:
            discription = message.reply_to_message.text
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_description(discription)
                await msg.edit("Successfully set group description \nBy {}".format(message.from_user.mention))
        except AttributeError:
            await msg.edit("You don't have permissions to set group description.")   
    elif len(message.command) > 1:
        try:
            discription = message.text.split(None, 1)[1]
            admin_check = await app.get_chat_member(chat_id, user_id)
            if admin_check.privileges.can_change_info:
                await message.chat.set_description(discription)
                await msg.edit("Successfully set group description \nBy {}".format(message.from_user.mention))
        except AttributeError:
            await msg.edit("You don't have permissions to set group description.")
    else:
        await msg.edit("Please reply to a message to set it as group description.")


# --------------------------------------------------------------------------------- #

@app.on_message(filters.command("cd")& filters.user(OWNER_ID))
async def bot_leave(_, message):
    chat_id = message.chat.id
    text = "Leaving group..."
    await message.reply_text(text)
    await app.leave_chat(chat_id=chat_id, delete=True)


# --------------------------------------------------------------------------------- #


