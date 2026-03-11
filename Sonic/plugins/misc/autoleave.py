import asyncio
from datetime import datetime
from pyrogram.enums import ChatType
from pytgcalls.exceptions import NoActiveGroupCall
import config
from Sonic import app, LOGGER
from Sonic.misc import db
from Sonic.core.call import Sonic, autoend, counter
from Sonic.utils.database import get_client, set_loop, is_active_chat, is_autoend, is_autoleave, group_assistant
import logging

# auto_leave task removed to prevent event loop blocking and audio lag

async def auto_end(): 
    global autoend, counter
    while True:
        await asyncio.sleep(60)
        try:
            ender = await is_autoend()
            if not ender:
                continue

            chatss = autoend
            keys_to_remove = []

            for chat_id in chatss:
                nocall = False
                try:
                    assistant = await group_assistant(Sonic, chat_id)
                    participants = await assistant.get_participants(chat_id)
                    users = len(participants)
                except NoActiveGroupCall:
                    users = 1
                    nocall = True
                except Exception:
                    users = 100

                timer = autoend.get(chat_id)
                if users == 1 and isinstance(timer, datetime):
                    if datetime.now() >= timer:
                        await set_loop(chat_id, 0)
                        keys_to_remove.append(chat_id)

                        try:
                            await db[chat_id][0]["mystic"].delete()
                        except Exception:
                            pass

                        try:
                            await Sonic.stop_stream(chat_id)
                        except Exception:
                            pass

                        try:
                            if not nocall:
                                await app.send_message(
                                    chat_id,
                                    "Â» Ê™á´á´› á´€á´œá´›á´á´á´€á´›Éªá´„á´€ÊŸÊŸÊ ÊŸá´‡Ò“á´› á´ Éªá´…á´‡á´á´„Êœá´€á´› "
                                    "Ê™á´‡á´„á´€á´œsá´‡ É´á´ á´É´á´‡ á´¡á´€s ÊŸÉªsá´›á´‡É´ÉªÉ´É¢ á´É´ á´ Éªá´…á´‡á´á´„Êœá´€á´›.",
                                )
                        except Exception:
                            pass

            for chat_id in keys_to_remove:
                try:
                    del autoend[chat_id]
                except Exception:
                    pass

        except Exception as e:
            LOGGER(__name__).exception(f"Error in auto_end loop: {e}")


asyncio.create_task(auto_end())
