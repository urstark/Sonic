import random
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Sonic import app

def get_random_message(love_percentage, command="love"):
    """Returns a witty message based on the calculated percentage and command."""
    if command == "love":
        if love_percentage <= 30:
            return random.choice([
                "Love is in the air but needs a little spark.",
                "A good start but there's room to grow.",
                "It's just the beginning of something beautiful."
            ])
        elif love_percentage <= 70:
            return random.choice([
                "A strong connection is there. Keep nurturing it.",
                "You've got a good chance. Work on it.",
                "Love is blossoming, keep going."
            ])
        else:
            return random.choice([
                "Wow! It's a match made in heaven!",
                "Perfect match! Cherish this bond.",
                "Destined to be together. Congratulations!"
            ])
    elif command == "crush":
        if love_percentage <= 30:
            return random.choice([
                "Just a passing thought, maybe?",
                "Not much of a crush, more of a 'who'?",
                "They might not even know you exist yet!"
            ])
        elif love_percentage <= 70:
            return random.choice([
                "There's definitely some chemistry here!",
                "They've caught your eye, haven't they?",
                "A solid crush. Maybe it's time to talk?"
            ])
        else:
            return random.choice([
                "You're head over heels! 💖",
                "Total infatuation! They're all you think about.",
                "It's a huge crush! Don't let them get away."
            ])
    else: # propose
        if love_percentage <= 50:
            return random.choice([
                "Maybe wait for a better moment?",
                "The timing doesn't seem right.",
                "Friendzone alert! 🚨"
            ])
        else:
            return random.choice([
                "Go for it! They're likely to say yes!",
                "Fortune favors the bold! Propose now!",
                "A diamond in the making. Do it!"
            ])

@app.on_message(filters.command(["love", "crush", "propose"], prefixes="/") & filters.group)
async def love_crush_propose_handler(client, message: Message):
    command = message.command[0].lower()
    chat_id = message.chat.id
    
    # 1. Identify the 'Subject'
    subject = None
    if message.reply_to_message:
        subject = message.reply_to_message.from_user
    else:
        subject = message.from_user

    if not subject:
        return

    # 2. Get a random target from the group
    list_of_users = []
    try:
        async for m in client.get_chat_members(chat_id, limit=200):
            if not m.user.is_bot and m.user.id != subject.id:
                list_of_users.append(m.user)
        
        if not list_of_users:
            return await message.reply_text("<b>I couldn't find anyone else in this group to match!</b>")

        target = random.choice(list_of_users)
        
        # 3. Calculation
        percentage = random.randint(10, 100)
        content_msg = get_random_message(percentage, command)

        # 4. Final Formatting based on command
        if command == "love":
            header = f"❤️ <b>LOVE PERCENTAGE</b>"
            formula = f"{subject.mention} + {target.mention}"
        elif command == "crush":
            header = f"💖 <b>CRUSH DETECTOR</b>"
            formula = f"{target.mention} is the secret crush of {subject.mention}"
        else: # propose
            header = f"💍 <b>PROPOSAL CHANCE</b>"
            formula = f"{subject.mention} proposing to {target.mention}"

        response = (
            f"{header}\n\n"
            f"{formula}\n"
            f"<b>Result:</b> <code>{percentage}%</code>\n\n"
            f"<i>{content_msg}</i>"
        )
        
        if command == "propose":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Accept", callback_data=f"propose_accept_{target.id}"),
                    InlineKeyboardButton("Reject", callback_data=f"propose_reject_{target.id}")
                ]
            ])
            await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=buttons)
        else:
            await message.reply_text(response, parse_mode=ParseMode.HTML)

    except Exception as e:
        print(f"Error in {command} command: {e}")

@app.on_callback_query(filters.regex(r"^propose_(accept|reject)_(\d+)$"))
async def propose_callback(client, callback_query):
    action = callback_query.matches[0].group(1)
    target_id = int(callback_query.matches[0].group(2))
    
    if callback_query.from_user.id != target_id:
        return await callback_query.answer("Only the recipient can accept or reject this proposal!", show_alert=True)
    
    await callback_query.edit_message_reply_markup(reply_markup=None)
    
    if action == "accept":
        await callback_query.message.reply_text(f"🎉 <b>{callback_query.from_user.mention} accepted the proposal!</b>")
    else:
        await callback_query.message.reply_text(f"😢 <b>{callback_query.from_user.mention} rejected the proposal.</b>")
