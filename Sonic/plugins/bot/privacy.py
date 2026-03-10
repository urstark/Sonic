from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from Sonic import app
import config

def get_privacy_text(_):
    return f"""
{_['emo_start']}

 <b>Privacy Policy for {app.mention} !</b>

Your privacy is important to us. To learn more about how we collect, use, and protect your data, please review our Privacy Policy here: [Privacy Policy]({config.PRIVACY_LINK}).

If you have any questions or concerns, feel free to reach out to our [support team](https://t.me/sonicshub).
"""

from Sonic.utils.database import get_lang
from strings import get_string

@app.on_message(filters.command("privacy"))
async def privacy(client, message: Message):
    try:
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    except:
        _ = get_string("en")

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "View Privacy Policy", url=config.SUPPORT_GROUP
                )
            ]
        ]
    )
    await message.reply_text(
        get_privacy_text(_), 
        reply_markup=keyboard, 
        parse_mode=ParseMode.HTML, 
        disable_web_page_preview=True
    )
