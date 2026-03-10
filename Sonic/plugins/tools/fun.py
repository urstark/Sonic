import random
import asyncio
from typing import Optional
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from Sonic import app as bot, LOGGER
import httpx
import config 

COMMAND_PREFIXES = ["/", "!", "."]

# Define missing variables locally to fix ModuleNotFoundError
SEX_IMAGES = ["https://telegra.ph/file/d30d11c4365c025c25e3e.jpg"]

command_to_category = {
    "neko": "neko",
    "shinobu": "shinobu",
    "megumin": "megumin",
    "bully": "bully",
    "cuddle": "cuddle",
    "cry": "cry",
    "hug": "hug",
    "awoo": "awoo",
    "kiss": "kiss",
    "lick": "lick",
    "pat": "pat",
    "smug": "smug",
    "bonk": "bonk",
    "yeet": "yeet",
    "blush": "blush",
    "smile": "smile",
    "wave": "wave",
    "highfive": "highfive",
    "handhold": "handhold",
    "nom": "nom",
    "bite": "bite",
    "glomp": "glomp",
    "slap": "slap",
    "kill": "kill",
    "happy": "happy",
    "wink": "wink",
    "poke": "poke",
    "dance": "dance",
    "cringe": "cringe",
}

# Command handler for /lick
@bot.on_message(filters.command("lick" , prefixes=COMMAND_PREFIXES) & filters.group)
async def lick_command(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        msg = await message.reply_text("You need to reply to a user's message or provide a username to lick them.")
        asyncio.create_task(delete_after(msg))
        return

    user_a = message.from_user
    if message.reply_to_message:
        user_b = message.reply_to_message.from_user
    else:
        username = message.command[1]
        try:
            user_b = await client.get_users(username)
        except Exception:
            msg = await message.reply_text(f"Could not find user {username}.")
            asyncio.create_task(delete_after(msg))
            return

    bot_id = (await client.get_me()).id
    if user_b.id == bot_id:
        msg = await message.reply_text("Ew, don't lick me!")
        asyncio.create_task(delete_after(msg))
        return

    if user_a.id == user_b.id:
        msg = await message.reply_text("Licking yourself? That's quite unique.")
        asyncio.create_task(delete_after(msg))
        return

    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Accept", callback_data=f"accept_lick:{user_a.id}:{user_b.id}"),
                InlineKeyboardButton("Reject", callback_data=f"reject_lick:{user_a.id}:{user_b.id}")
            ]
        ]
    )

    msg = await message.reply_text(
        f"👅 <b>{user_b.first_name}</b>, <b>{user_a.first_name}</b> wants to 👅 <b>lick</b> you!\n\n"
        "<i>Will you allow this?</i>",
        reply_markup=inline_keyboard,
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(delete_after(msg))

# Callback handler for accepting the lick
@bot.on_callback_query(filters.regex(r"^accept_lick:(\d+):(\d+)$"))
async def accept_lick_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can accept this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    lick_image_url = await fetch_image("lick")
    await callback_query.message.delete()

    if lick_image_url:
        msg = await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=lick_image_url,
            caption=f"👅 <b>{user_a.first_name}</b> licked <b>{user_b.first_name}</b>! Tasty?",
            parse_mode=ParseMode.HTML
        )
    else:
        msg = await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"👅 <b>{user_a.first_name}</b> licked <b>{user_b.first_name}</b>! Tasty?",
            parse_mode=ParseMode.HTML
        )
    asyncio.create_task(delete_after(msg))
    await callback_query.answer()

# Callback handler for rejecting the lick
@bot.on_callback_query(filters.regex(r"^reject_lick:(\d+):(\d+)$"))
async def reject_lick_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can reject this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    await callback_query.message.edit_text(
        f"😛 <b>{user_b.first_name}</b> said NO to being licked by <b>{user_a.first_name}</b>. Stay dry!",
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer("You rejected the lick!")

async def delete_after(message: Message, delay: int = 600):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception:
        pass
    
COMMAND_PREFIXES = ["/", "!", "."]
BASE_URL = getattr(config, "BASE_URL", "https://waifu.pics/api")

# Command handler for /hug
@bot.on_message(filters.command("hug" , prefixes=COMMAND_PREFIXES) & filters.group)
async def hug_command(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        msg = await message.reply_text("You need to reply to a user's message or provide a username to send a hug request.")
        asyncio.create_task(delete_after(msg))
        return

    user_a = message.from_user

    if message.reply_to_message:
        user_b = message.reply_to_message.from_user
    else:
        username = message.command[1]
        try:
            user_b = await client.get_users(username)
        except Exception as e:
            msg = await message.reply_text(f"Could not find user {username}.")
            asyncio.create_task(delete_after(msg))
            return

    # Check if the bot is replying to its own message
    bot_id = (await client.get_me()).id
    if user_b.id == bot_id:
        msg = await message.reply_text("No thanks, I don't need a hug right now.")
        asyncio.create_task(delete_after(msg))
        return

    if user_a.id == user_b.id:
        msg = await message.reply_text("You cannot send a hug request to yourself.")
        asyncio.create_task(delete_after(msg))
        return

    # Create inline button for User B to accept or reject
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Accept", callback_data=f"accept_hug:{user_a.id}:{user_b.id}"),
                InlineKeyboardButton("Reject", callback_data=f"reject_hug:{user_a.id}:{user_b.id}")
            ]
        ]
    )

    # Send the hug request message
    msg = await message.reply_text(
        f"<b>{user_b.first_name}</b>, <b>{user_a.first_name}</b> wants to send you a 🫂 <b>hug</b>!\n\n"
        "<i>Will you accept?</i>",
        reply_markup=inline_keyboard,
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(delete_after(msg))

# Callback handler for accepting the hug
@bot.on_callback_query(filters.regex(r"^accept_hug:(\d+):(\d+)$"))
async def accept_hug_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    if callback_query.from_user.id != user_b.id:
        await callback_query.answer("only the recipient can accept this hug request.", show_alert=True)
        return

    # Get a random hug image URL
    hug_image_url = await fetch_image("hug")

    # Delete the acceptance message with the inline button
    await callback_query.message.delete()

    if hug_image_url:
        # Send the hug accepted message with the image
        msg = await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=hug_image_url,
            caption=f"🫂 <b>{user_b.first_name}</b> accepted the hug from <b>{user_a.first_name}</b>!",
            parse_mode=ParseMode.HTML
        )
    else:
        msg = await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"🫂 <b>{user_b.first_name}</b> accepted the hug from <b>{user_a.first_name}</b>!",
            parse_mode=ParseMode.HTML
        )
    asyncio.create_task(delete_after(msg))

    await callback_query.answer()

# Callback handler for rejecting the hug
@bot.on_callback_query(filters.regex(r"^reject_hug:(\d+):(\d+)$"))
async def reject_hug_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can reject this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    await callback_query.message.edit_text(
        f"💔 <b>{user_b.first_name}</b> has rejected the hug from <b>{user_a.first_name}</b>. How sad!",
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer("You rejected the hug!")

# Command handler for /kill
@bot.on_message(filters.command("kill"  , prefixes=COMMAND_PREFIXES) & filters.group)
async def kill_command(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        msg = await message.reply_text("You need to reply to a user's message or provide a username to kill them.")
        asyncio.create_task(delete_after(msg))
        return

    user_a = message.from_user

    if message.reply_to_message:
        user_b = message.reply_to_message.from_user
    else:
        username = message.command[1]
        try:
            user_b = await client.get_users(username)
        except Exception as e:
            msg = await message.reply_text(f"Could not find user {username}.")
            asyncio.create_task(delete_after(msg))
            return

    # Check if the bot is being killed
    bot_id = (await client.get_me()).id
    if user_b.id == bot_id:
        msg = await message.reply_text("You can't kill a bot! 🤖")
        asyncio.create_task(delete_after(msg))
        return

    if user_a.id == user_b.id:
        msg = await message.reply_text("You can't kill yourself. That's a bit dramatic.")
        asyncio.create_task(delete_after(msg))
        return

    # Create inline button for User B to accept or reject
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Accept", callback_data=f"accept_kill:{user_a.id}:{user_b.id}"),
                InlineKeyboardButton("Reject", callback_data=f"reject_kill:{user_a.id}:{user_b.id}")
            ]
        ]
    )

    # Send the kill request message
    msg = await message.reply_text(
        f"⚔️ <b>{user_b.first_name}</b>, <b>{user_a.first_name}</b> wants to 💀 <b>kill</b> you!\n\n"
        "<i>Will you allow this to happen?</i>",
        reply_markup=inline_keyboard,
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(delete_after(msg))

# Callback handler for accepting the kill
@bot.on_callback_query(filters.regex(r"^accept_kill:(\d+):(\d+)$"))
async def accept_kill_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can accept this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    kill_image_url = await fetch_image("kill")
    await callback_query.message.delete()

    if kill_image_url:
        msg = await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=kill_image_url,
            caption=f"💀 <b>{user_a.first_name}</b> has brutally killed <b>{user_b.first_name}</b>!",
            parse_mode=ParseMode.HTML
        )
    else:
        msg = await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"💀 <b>{user_a.first_name}</b> has brutally killed <b>{user_b.first_name}</b>!",
            parse_mode=ParseMode.HTML
        )
    asyncio.create_task(delete_after(msg))
    await callback_query.answer()

# Callback handler for rejecting the kill
@bot.on_callback_query(filters.regex(r"^reject_kill:(\d+):(\d+)$"))
async def reject_kill_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can reject this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    await callback_query.message.edit_text(
        f"🛡️ <b>{user_b.first_name}</b> managed to survive the murder attempt by <b>{user_a.first_name}</b>! A legendary escape.",
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer("You survived!")

# Command handler for /kiss
@bot.on_message(filters.command("kiss"  , prefixes=COMMAND_PREFIXES) & filters.group)
async def kiss_command(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        msg = await message.reply_text("You need to reply to a user's message or provide a username to send a kiss request.")
        asyncio.create_task(delete_after(msg))
        return

    user_a = message.from_user

    if message.reply_to_message:
        user_b = message.reply_to_message.from_user
    else:
        username = message.command[1]
        try:
            user_b = await client.get_users(username)
        except Exception as e:
            msg = await message.reply_text(f"Could not find user {username}.")
            asyncio.create_task(delete_after(msg))
            return

    # Check if the bot is replying to its own message
    bot_id = (await client.get_me()).id
    if user_b.id == bot_id:
        msg = await message.reply_text("Get lost!, I don't want a kiss from you.")
        asyncio.create_task(delete_after(msg))
        return

    if user_a.id == user_b.id:
        msg = await message.reply_text("Why are you single? You know, nowadays everyone is committed except you!")
        asyncio.create_task(delete_after(msg))
        return

    # Create inline button for User B to accept or reject
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Accept", callback_data=f"accept_kiss:{user_a.id}:{user_b.id}"),
                InlineKeyboardButton("Reject", callback_data=f"reject_kiss:{user_a.id}:{user_b.id}")
            ]
        ]
    )

    # Send the kiss request message
    msg = await message.reply_text(
        f"<b>{user_b.first_name}</b>, see <b>{user_a.first_name}</b> wants to 💋 <b>kiss</b> you!\n\n"
        "<i>Will you accept the kiss?</i>",
        reply_markup=inline_keyboard,
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(delete_after(msg))

# Callback handler for accepting the kiss
@bot.on_callback_query(filters.regex(r"^accept_kiss:(\d+):(\d+)$"))
async def accept_kiss_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    if callback_query.from_user.id != user_b.id:
        await callback_query.answer("only the recipient can accept this kiss request.", show_alert=True)
        return

    # Get a random kiss image URL
    kiss_image_url = await fetch_image("kiss")

    # Delete the acceptance message with the inline button
    await callback_query.message.delete()

    if kiss_image_url:
        # Send the kiss accepted message with the image
        msg = await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=kiss_image_url,
            caption=f"💋 <b>{user_b.first_name}</b> accepted the kiss from <b>{user_a.first_name}</b>!",
            parse_mode=ParseMode.HTML
        )
    else:
        msg = await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"💋 <b>{user_b.first_name}</b> accepted the kiss from <b>{user_a.first_name}</b>!",
            parse_mode=ParseMode.HTML
        )
    asyncio.create_task(delete_after(msg))

    await callback_query.answer()

# Callback handler for rejecting the kiss
@bot.on_callback_query(filters.regex(r"^reject_kiss:(\d+):(\d+)$"))
async def reject_kiss_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can reject this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    await callback_query.message.edit_text(
        f"🚫 <b>{user_b.first_name}</b> has rejected the kiss from <b>{user_a.first_name}</b>. Better luck next time!",
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer("You rejected the kiss!")

# Command handler for /pat
@bot.on_message(filters.command("pat"  , prefixes=COMMAND_PREFIXES) & filters.group)
async def pat_command(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        msg = await message.reply_text("You need to reply to a user's message or provide a username to pat them.")
        asyncio.create_task(delete_after(msg))
        return

    user_a = message.from_user

    if message.reply_to_message:
        user_b = message.reply_to_message.from_user
    else:
        username = message.command[1]
        try:
            user_b = await client.get_users(username)
        except Exception as e:
            msg = await message.reply_text(f"Could not find user {username}.")
            asyncio.create_task(delete_after(msg))
            return

    # Check if the bot is being patted
    bot_id = (await client.get_me()).id
    if user_b.id == bot_id:
        msg = await message.reply_text("You can't pat a bot, but thanks for the gesture!")
        asyncio.create_task(delete_after(msg))
        return

    if user_a.id == user_b.id:
        msg = await message.reply_text("You can't pat yourself. You deserve pats from others!")
        asyncio.create_task(delete_after(msg))
        return

    # Create inline button for User B to accept or reject
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Accept", callback_data=f"accept_pat:{user_a.id}:{user_b.id}"),
                InlineKeyboardButton("Reject", callback_data=f"reject_pat:{user_a.id}:{user_b.id}")
            ]
        ]
    )

    # Send the pat request message
    msg = await message.reply_text(
        f"<b>{user_b.first_name}</b>, <b>{user_a.first_name}</b> wants to give you a 🫶 <b>pat</b>!\n\n"
        "<i>Will you accept?</i>",
        reply_markup=inline_keyboard,
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(delete_after(msg))

# Callback handler for accepting the pat
@bot.on_callback_query(filters.regex(r"^accept_pat:(\d+):(\d+)$"))
async def accept_pat_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can accept this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    pat_image_url = await fetch_image("pat")
    await callback_query.message.delete()

    if pat_image_url:
        msg = await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=pat_image_url,
            caption=f"💖 <b>{user_a.first_name}</b> gave a warm pat to <b>{user_b.first_name}</b>! So sweet!",
            parse_mode=ParseMode.HTML
        )
    else:
        msg = await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"💖 <b>{user_a.first_name}</b> gave a warm pat to <b>{user_b.first_name}</b>! So sweet!",
            parse_mode=ParseMode.HTML
        )
    asyncio.create_task(delete_after(msg))
    await callback_query.answer()

# Callback handler for rejecting the pat
@bot.on_callback_query(filters.regex(r"^reject_pat:(\d+):(\d+)$"))
async def reject_pat_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can reject this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    await callback_query.message.edit_text(
        f"😔 <b>{user_b.first_name}</b> rejected the pat from <b>{user_a.first_name}</b>. Oh well...",
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer("You rejected the pat!")


# Command handler for /sex
@bot.on_message(filters.command("sex"  , prefixes=COMMAND_PREFIXES) & filters.group)
async def sex_command(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        msg = await message.reply_text("You need to reply to a user's message or provide a username to send a sex request.")
        asyncio.create_task(delete_after(msg))
        return

    user_a = message.from_user

    if message.reply_to_message:
        user_b = message.reply_to_message.from_user
    else:
        username = message.command[1]
        try:
            user_b = await client.get_users(username)
        except Exception as e:
            msg = await message.reply_text(f"Could not find user {username}.")
            asyncio.create_task(delete_after(msg))
            return

    # Check if the bot is the target of the request
    bot_id = (await client.get_me()).id
    if user_b.id == bot_id:
        msg = await message.reply_text("Get lost, I don't want to have sex with you.")
        asyncio.create_task(delete_after(msg))
        return

    if user_a.id == user_b.id:
        msg = await message.reply_text("Why are you single? You know, nowadays everyone is committed except you!")
        asyncio.create_task(delete_after(msg))
        return

    # Create inline button for User B to accept or reject
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Accept", callback_data=f"accept_sex:{user_a.id}:{user_b.id}"),
                InlineKeyboardButton("Reject", callback_data=f"reject_sex:{user_a.id}:{user_b.id}")
            ]
        ]
    )

    # Send the sex request message
    msg = await message.reply_text(
        f"🔥 <b>{user_b.first_name}</b>, <b>{user_a.first_name}</b> wants to have 👉👌 <b>sex</b> with you!\n\n"
        "<i>Will you accept?</i>",
        reply_markup=inline_keyboard,
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(delete_after(msg))

# Callback handler for accepting the sex request
@bot.on_callback_query(filters.regex(r"^accept_sex:(\d+):(\d+)$"))
async def accept_sex_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    if callback_query.from_user.id != user_b.id:
        await callback_query.answer("Only the recipient can accept this sex request.", show_alert=True)
        return

    # Get a random sex image URL
    sex_image_url = random.choice(SEX_IMAGES)

    # Delete the acceptance message with the inline button
    await callback_query.message.delete()

    if sex_image_url:
        # Send the sex accepted message with the image
        msg = await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=sex_image_url,
            caption=f"🔥 <b>{user_b.first_name}</b> had <b>sex</b> with <b>{user_a.first_name}</b>!\n\n<i>What do you think, will they have a baby?</i> 👶",
            parse_mode=ParseMode.HTML
        )
    else:
        msg = await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"🔥 <b>{user_b.first_name}</b> had <b>sex</b> with <b>{user_a.first_name}</b>!\n\n<i>What do you think, will they have a baby?</i> 👶",
            parse_mode=ParseMode.HTML
        )
    asyncio.create_task(delete_after(msg))

    await callback_query.answer()

# Callback handler for rejecting the sex request
@bot.on_callback_query(filters.regex(r"^reject_sex:(\d+):(\d+)$"))
async def reject_sex_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can reject this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    await callback_query.message.edit_text(
        f"🥶 <b>{user_b.first_name}</b> has rejected the sex proposal from <b>{user_a.first_name}</b>! Cold as ice.",
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer("You rejected the proposal!")



# Command handler for /slap
@bot.on_message(filters.command("slap"  , prefixes=COMMAND_PREFIXES) & filters.group)
async def slap_command(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        msg = await message.reply_text("You need to reply to a user's message or provide a username to slap them.")
        asyncio.create_task(delete_after(msg))
        return

    user_a = message.from_user

    if message.reply_to_message:
        user_b = message.reply_to_message.from_user
    else:
        username = message.command[1]
        try:
            user_b = await client.get_users(username)
        except Exception as e:
            msg = await message.reply_text(f"Could not find user {username}.")
            asyncio.create_task(delete_after(msg))
            return

    # Check if the bot is being slapped
    bot_id = (await client.get_me()).id
    if user_b.id == bot_id:
        msg = await message.reply_text("Hey, don't slap me! I'm just a bot.")
        asyncio.create_task(delete_after(msg))
        return

    if user_a.id == user_b.id:
        msg = await message.reply_text("You cannot slap yourself. That's weird.")
        asyncio.create_task(delete_after(msg))
        return

    # Create inline button for User B to accept or reject
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Accept", callback_data=f"accept_slap:{user_a.id}:{user_b.id}"),
                InlineKeyboardButton("Reject", callback_data=f"reject_slap:{user_a.id}:{user_b.id}")
            ]
        ]
    )

    # Send the slap request message
    msg = await message.reply_text(
        f"💥 <b>{user_b.first_name}</b>, <b>{user_a.first_name}</b> wants to 👋 <b>slap</b> you!\n\n"
        "<i>Will you allow this?</i>",
        reply_markup=inline_keyboard,
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(delete_after(msg))

# Callback handler for accepting the slap
@bot.on_callback_query(filters.regex(r"^accept_slap:(\d+):(\d+)$"))
async def accept_slap_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can accept this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    slap_image_url = await fetch_image("slap")
    await callback_query.message.delete()

    if slap_image_url:
        msg = await client.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=slap_image_url,
            caption=f"💥 <b>{user_a.first_name}</b> slapped <b>{user_b.first_name}</b>! That must've hurt!",
            parse_mode=ParseMode.HTML
        )
    else:
        msg = await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"💥 <b>{user_a.first_name}</b> slapped <b>{user_b.first_name}</b>! That must've hurt!",
            parse_mode=ParseMode.HTML
        )
    asyncio.create_task(delete_after(msg))
    await callback_query.answer()

# Callback handler for rejecting the slap
@bot.on_callback_query(filters.regex(r"^reject_slap:(\d+):(\d+)$"))
async def reject_slap_callback(client: Client, callback_query):
    data = callback_query.data.split(":")
    user_a_id = int(data[1])
    user_b_id = int(data[2])

    if callback_query.from_user.id != user_b_id:
        await callback_query.answer("Only the target user can reject this!", show_alert=True)
        return

    user_a = await client.get_users(user_a_id)
    user_b = await client.get_users(user_b_id)

    await callback_query.message.edit_text(
        f"🛡️ <b>{user_b.first_name}</b> dodged the slap from <b>{user_a.first_name}</b>! Close call.",
        parse_mode=ParseMode.HTML
    )
    await callback_query.answer("You rejected the slap!")
    

# Function to fetch the image from the API
async def fetch_image(category: str) -> Optional[str]:
    """Fetch an image URL from multiple APIs for extreme reliability."""
    
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        # 1. waifu.pics (Primary)
        try:
            url = f"https://waifu.pics/api/sfw/{category}"
            response = await client.get(url)
            if response.status_code == 200:
                image_url = response.json().get("url")
                if image_url:
                    return image_url
            else:
                LOGGER(__name__).warning(f"waifu.pics [{category}] returned {response.status_code}")
        except Exception as e:
            LOGGER(__name__).error(f"waifu.pics error ({category}): {str(e)}")

        # 2. nekos.best (First Fallback)
        try:
            # Map some categories if necessary for nekos.best
            nb_category = category
            if category == "kill":
                nb_category = "shoot"
            elif category == "bite":
                nb_category = "bite"
                
            url = f"https://nekos.best/api/v2/{nb_category}"
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if "results" in data and data["results"]:
                    image_url = data["results"][0].get("url")
                    if image_url:
                        return image_url
            else:
                LOGGER(__name__).warning(f"nekos.best [{nb_category}] returned {response.status_code}")
        except Exception as e:
            LOGGER(__name__).error(f"nekos.best error ({category}): {str(e)}")

        # 3. nekos.life (Second Fallback)
        try:
            url = f"https://nekos.life/api/v2/img/{category}"
            response = await client.get(url)
            if response.status_code == 200:
                image_url = response.json().get("url")
                if image_url:
                    return image_url
        except Exception:
            pass

    LOGGER(__name__).error(f"Failed to fetch fun image for category: {category} from all providers.")
    return None

# Separate commands that have interactive handlers (group only) from those that don't.
# Interactive commands should only trigger the generic handler in private chats.
interactive_cmds = ["hug", "kill", "kiss", "pat", "slap", "sex", "lick"]
interactive_in_keys = [c for c in command_to_category.keys() if c in interactive_cmds]
other_cmds = [c for c in command_to_category.keys() if c not in interactive_cmds]

@bot.on_message(filters.command(other_cmds, prefixes=COMMAND_PREFIXES) | (filters.command(interactive_in_keys, prefixes=COMMAND_PREFIXES) & filters.private))
async def send_waifu_image(client: Client, message: Message):
    """Send an image for the requested category."""
    # Extract command and resolve the category
    command = message.command[0].lower()
    category = command_to_category.get(command) or command  # Get mapped category or fallback to the command itself

    try:
        image_url = await fetch_image(category)
        if image_url:
            msg = await message.reply_photo(photo=image_url)
            asyncio.create_task(delete_after(msg))
        else:
            msg = await message.reply_text(
                f"Sorry, I couldn't fetch an image for '{category}'. Please try again later."
            )
            asyncio.create_task(delete_after(msg))
    except Exception as e:
        msg = await message.reply_text(
            "An unexpected error occurred. Please try again later or contact the bot admin."
        )
        asyncio.create_task(delete_after(msg))
    
__module__ = "Fun"


__help__ = """<b><u>ꜰᴜɴ ᴄᴏᴍᴍᴀɴᴅs :</b></u>

<b>ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ (ᴡɪᴛʜ ᴀᴄᴄᴇᴘᴛ/ʀᴇᴊᴇᴄᴛ):</b>
/hug, /kiss, /lick, /pat, /slap, /sex, /kill

<b>ᴏᴛʜᴇʀs:</b>
/neko, /shinobu, /megumin, /bully, /cuddle, /cry, /awoo, /smug, /bonk, /yeet, /blush, /smile, /wave, /highfive, /handhold, /nom, /bite, /glomp, /happy, /wink, /poke, /dance, /cringe

Use these commands to interact with group members with anime-style visuals.
"""
