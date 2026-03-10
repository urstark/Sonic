import asyncio
import importlib
import logging

# 1. Create and set the loop BEFORE anything from Sonic is imported.
# This ensures module-level instantiations capture this loop.
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Sonic import LOGGER, app, userbot
from Sonic.core.call import Sonic
from Sonic.misc import sudo
from Sonic.plugins import ALL_MODULES
from Sonic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    # Set up logging early
    logging.basicConfig(level=logging.INFO)
    
    # 2. Re-assign loop to all clients just in case they missed it.
    # On Python 3.12+, Pyrogram sometimes caches a dummy loop during import.
    running_loop = asyncio.get_running_loop()
    app.loop = running_loop
    userbot.one.loop = running_loop
    userbot.two.loop = running_loop
    userbot.three.loop = running_loop
    userbot.four.loop = running_loop
    userbot.five.loop = running_loop
    # Also update Sonic (Call) internal userbots if they exist
    # (Sonic in call.py also creates its own Clients)
    if hasattr(Sonic, "one"): Sonic.one._app.loop = running_loop
    if hasattr(Sonic, "two"): Sonic.two._app.loop = running_loop
    if hasattr(Sonic, "three"): Sonic.three._app.loop = running_loop
    if hasattr(Sonic, "four"): Sonic.four._app.loop = running_loop
    if hasattr(Sonic, "five"): Sonic.five._app.loop = running_loop

    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        return
        
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
        
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("Sonic.plugins" + all_module.replace("\\", "."))
    LOGGER("Sonic.plugins").info("Successfully Imported Modules...")
    
    await userbot.start()
    await Sonic.start()
    
    try:
        await Sonic.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("Sonic").error(
            "Please turn on the videochat of your log group\\channel.\n\nStopping Bot..."
        )
        return
    except Exception as e:
        LOGGER("Sonic").error(f"Error starting stream: {e}")
        
    await Sonic.decorators()
    LOGGER("Sonic").info(
        "\x53\x6f\x6e\x69\x63\x20\x4d\x75\x73\x69\x63\x20\x53\x74\x61\x72\x74\x65\x64\x20\x53\x75\x63\x63\x65\x73\x73\x66\x75\x6c\x6c\x79\x2e\x20\x44\x6f\x6e\x27\x74\x20\x66\x6f\x72\x67\x65\x74\x20\x74\x6f\x20\x76\x69\x73\x69\x74\x20\x40\x53\x6f\x6e\x69\x63\x73\x48\x75\x62"
    )
    await idle()
    
    await app.stop()
    await userbot.stop()
    LOGGER("Sonic").info("Stopping Sonic...")


if __name__ == "__main__":
    try:
        loop.run_until_complete(init())
    except KeyboardInterrupt:
        pass

