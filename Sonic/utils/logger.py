from pyrogram.enums import ParseMode

from Sonic import app
from Sonic.utils.database import is_on_off
from config import LOG_GROUP_ID


async def play_logs(message, streamtype):
    if await is_on_off(2):
        logger_text = f"""
<b>{app.mention} Play Log</b>

<b>Chat id :</b> <code>{message.chat.id}</code>
<b>Chat name :</b> {message.chat.title}
<b>Chat username :</b> @{message.chat.username}

<b>User id :</b> <code>{message.from_user.id}</code>
<b>Name :</b> {message.from_user.mention}
<b>Username :</b> @{message.from_user.username}

<b>Query :</b> {message.text.split(None, 1)[1]}
<b>Streamtype :</b> {streamtype}"""
        if message.chat.id != LOG_GROUP_ID:
            try:
                await app.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=logger_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except:
                pass
        return