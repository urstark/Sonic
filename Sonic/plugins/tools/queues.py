import asyncio
import os

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message

import config
from Sonic import YouTube, app
from Sonic.core.call import Sonic
from Sonic.misc import db
from Sonic.utils import SonicBin, get_channeplayCB, seconds_to_min
from Sonic.utils.database import get_cmode, is_active_chat, is_music_playing
from Sonic.utils.decorators.language import language, languageCB
from Sonic.utils.inline import queue_back_markup, queue_markup
from Sonic.utils.thumbnails import gen_thumb
from strings import get_string
from config import BANNED_USERS

basic = {}

def get_image(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"
    else:
        return config.YOUTUBE_IMG_URL


def get_duration(playing):
    file_path = playing[0].get("file")
    if not file_path:
        return "Unknown"       
    if "index_" in file_path or "live_" in file_path:
        return "Unknown"       
    duration_seconds = int(playing[0]["seconds"])
    if duration_seconds == 0:
        return "Unknown"
    else:
        return "Inline"

@app.on_message(
    filters.command(["queue", "cqueue", "player", "cplayer", "playing", "cplaying"])
    & filters.group
    & ~BANNED_USERS
)
@language
async def get_queue(client, message: Message, _):
    if message.command[0][0] == "c":
        chat_id = await get_cmode(message.chat.id)
        if chat_id is None:
            return await message.reply_text(_["setting_7"])
        try:
            await app.get_chat(chat_id)
        except:
            return await message.reply_text(_["cplay_4"])
        cplay = True
    else:
        chat_id = message.chat.id
        cplay = False
    if not await is_active_chat(chat_id):
        return await message.reply_text(_["general_5"])
    got = db.get(chat_id)
    if not got:
        return await message.reply_text(_["queue_2"])
    file = got[0]["file"]
    videoid = got[0]["vidid"]
    user = got[0]["by"]
    title = (got[0]["title"]).title()
    stream_type = (got[0]["streamtype"]).title()
    DUR = get_duration(got)
    if "live_" in file:
        IMAGE = get_image(videoid)
    elif "vid_" in file:
        IMAGE = get_image(videoid)
    elif "index_" in file:
        IMAGE = config.STREAM_IMG_URL
    else:
        if videoid == "telegram":
            IMAGE = (
                config.TELEGRAM_AUDIO_URL
                if stream_type == "Audio"
                else config.TELEGRAM_VIDEO_URL
            )
        elif videoid == "soundcloud":
            IMAGE = config.SOUNCLOUD_IMG_URL
        else:
            IMAGE = get_image(videoid)
    send = _["queue_6"] if DUR == "Unknown" else _["queue_7"]
    cap = _["queue_8"].format(app.mention, title, stream_type, user, send)
    upl = (
        queue_markup(_, DUR, "c" if cplay else "g", videoid)
        if DUR == "Unknown"
        else queue_markup(
            _,
            DUR,
            "c" if cplay else "g",
            videoid,
            seconds_to_min(got[0]["played"]),
            got[0]["dur"],
        )
    )
    basic[videoid] = True
    mystic = await message.reply_text(cap, reply_markup=upl)
    if DUR != "Unknown":
        try:
            while db[chat_id][0]["vidid"] == videoid:
                await asyncio.sleep(15)        
                if not await is_active_chat(chat_id) or not basic.get(videoid):
                    break
                if await is_music_playing(chat_id):
                    try:
                        buttons = queue_markup(
                            _,
                            DUR,
                            "c" if cplay else "g",
                            videoid,
                            seconds_to_min(db[chat_id][0]["played"]),
                            db[chat_id][0]["dur"],
                        )
                        await mystic.edit_reply_markup(reply_markup=buttons)
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                    except:
                        pass
        except:
            pass


@app.on_callback_query(filters.regex("GetTimer") & ~BANNED_USERS)
async def quite_timer(client, CallbackQuery: CallbackQuery):
    try:
        await CallbackQuery.answer()
    except:
        pass


@app.on_callback_query(filters.regex("GetQueued") & ~BANNED_USERS)
@languageCB
async def queued_tracks(client, CallbackQuery: CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    what, videoid = callback_request.split("|")
    try:
        chat_id, channel = await get_channeplayCB(_, what, CallbackQuery)
    except:
        return
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True) 
    got = db.get(chat_id)
    if not got:
        return await CallbackQuery.answer(_["queue_2"], show_alert=True)    
    if len(got) == 1:
        return await CallbackQuery.answer(_["queue_5"], show_alert=True)    
    await CallbackQuery.answer()
    basic[videoid] = False
    buttons = queue_back_markup(_, what)   
    med = InputMediaPhoto(
        media="https://telegra.ph//file/6f7d35131f69951c74ee5.jpg",
        caption=_["queue_1"],
    )
    try:
        await CallbackQuery.edit_message_media(media=med)
    except:
        pass
    j = 0
    msg = ""
    # Build queue list with per-song Play Now buttons
    per_song_buttons = []
    for x in got:
        j += 1
        t = x["title"][:20] + ("..." if len(x["title"]) > 40 else "")
        by = x["by"][:10] + ("..." if len(x["by"]) > 18 else "")
        if j == 1:
            msg += f"{_['emo_play']} Streaming :\n\n {_['emo_title']} Title : {t}\n{_['emo_dur']} Duration : {x['dur']}\n{_['emo_req']} By : {by}\n\n"
        elif j == 2:
            msg += f"{_['emo_queue']} Queued :\n\n {_['emo_title']} Title : {t}\n{_['emo_dur']} Duration : {x['dur']}\n{_['emo_req']} By : {by}\n\n"
            per_song_buttons.append([
                InlineKeyboardButton(
                    text=f"{x['title'][:20]}",
                    callback_data=f"PlayNow {chat_id}|{j - 1}",
                )
            ])
        else:
            msg += f"{_['emo_title']} Title : {t}\n{_['emo_dur']} Duration : {x['dur']}\n{_['emo_req']} By : {by}\n\n"
            per_song_buttons.append([
                InlineKeyboardButton(
                    text=f"{x['title'][:18]}",
                    callback_data=f"PlayNow {chat_id}|{j - 1}",
                )
            ])

    # Add Back + Close in last row
    per_song_buttons.append([
        InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data=f"queue_back_timer {what}"),
        InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
    ])
    play_now_markup = InlineKeyboardMarkup(per_song_buttons)

    if "Queued" in msg:
        if len(msg) < 700:
            await asyncio.sleep(1)
            try:
                return await CallbackQuery.edit_message_text(msg, reply_markup=play_now_markup)
            except:
                pass         
        if "" in msg:
            msg = msg.replace("", "")           
        link = await SonicBin(msg)
        med = InputMediaPhoto(media=link, caption=_["queue_3"].format(link))
        try:
            await CallbackQuery.edit_message_media(media=med, reply_markup=play_now_markup)
        except:
            pass
    else:
        await asyncio.sleep(1)
        try:
            return await CallbackQuery.edit_message_text(msg, reply_markup=play_now_markup)
        except:
            pass


@app.on_callback_query(filters.regex("PlayNow") & ~BANNED_USERS)
@languageCB
async def play_now_from_queue(client, CallbackQuery: CallbackQuery, _):
    """
    Force-play a specific song from the queue immediately.
    The song is moved to position 1 (right after currently playing),
    then current song is skipped  so playback jumps to it instantly.
    After that queued song ends, the bot resumes the rest of the queue normally.
    """
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    chat_id_str, position_str = callback_request.split("|")
    
    try:
        chat_id = int(chat_id_str)
        position = int(position_str)  # 1-based index in the queue list (0 = currently playing)
    except (ValueError, IndexError):
        return await CallbackQuery.answer("Invalid request.", show_alert=True)

    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)

    check = db.get(chat_id)
    if not check or len(check) <= position:
        return await CallbackQuery.answer(
            "Song no longer in queue (it may have already played).", show_alert=True
        )

    target = check[position]
    title = target["title"].title()

    # Move the target song to position 1 (right after currently playing track)
    check.pop(position)
    check.insert(1, target)

    await CallbackQuery.answer(f"Playing '{title[:20]}' next!", show_alert=False)

    # Delete the queue card message to keep chat clean
    try:
        await CallbackQuery.message.delete()
    except:
        pass

    # Now trigger a skip  this pops currently playing (index 0) and plays index 1 (our target)
    try:
        queued = check[1]["file"]
        videoid = check[1]["vidid"]
        streamtype = check[1]["streamtype"]
        status = True if str(streamtype) == "video" else None

        # Pop index 0 (current track)
        from Sonic.utils.stream.autoclear import auto_clean
        popped = check.pop(0)
        if popped:
            await auto_clean(popped)

        # Now check[0] is our target  play it
        queued = check[0]["file"]
        videoid = check[0]["vidid"]
        streamtype = check[0]["streamtype"]
        status = True if str(streamtype) == "video" else None
        db[chat_id][0]["played"] = 0

        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0:
                return await app.send_message(chat_id, f"Failed to load stream for {title}.")
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
            await Sonic.skip_stream(chat_id, link, video=status, image=image)

        elif "vid_" in queued:
            language_code = await __import__("Sonic.utils.database", fromlist=["get_lang"]).get_lang(chat_id)
            status_msg = await app.send_message(
                check[0]["chat_id"],
                _["call_7"],
            )
            try:
                file_path, direct = await YouTube.download(videoid, status_msg, videoid=True, video=status)
            except:
                return await status_msg.edit_text(_["call_6"])
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
            try:
                await Sonic.skip_stream(chat_id, file_path, video=status, image=image)
            except:
                return await status_msg.edit_text(_["call_6"])
            await status_msg.delete()

        else:
            try:
                image = await YouTube.thumbnail(videoid, True) if videoid not in ["telegram", "soundcloud"] else None
            except:
                image = None
            await Sonic.skip_stream(chat_id, queued, video=status, image=image)

        # Send the now-playing card
        from Sonic.utils.inline import stream_markup
        from Sonic.utils.thumbnails import gen_thumb
        button = stream_markup(_, chat_id)
        img = await gen_thumb(videoid) if videoid not in ["telegram", "soundcloud"] else (
            config.TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL
        )
        original_chat_id = check[0]["chat_id"]
        run = await app.send_photo(
            chat_id=original_chat_id,
            photo=img,
            caption=_["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{videoid}",
                title[:20],
                check[0]["dur"],
                check[0]["by"],
            ),
            reply_markup=InlineKeyboardMarkup(button),
        )
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = "stream"

    except Exception as e:
        print(f"PlayNow error: {e}")
        try:
            await app.send_message(chat_id, f"Failed to play now: {type(e).__name__}")
        except:
            pass


@app.on_callback_query(filters.regex("queue_back_timer") & ~BANNED_USERS)
@languageCB
async def queue_back(client, CallbackQuery: CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cplay = callback_data.split(None, 1)[1]   
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return       
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)    
    got = db.get(chat_id)
    if not got:
        return await CallbackQuery.answer(_["queue_2"], show_alert=True)       
    await CallbackQuery.answer(_["set_cb_5"], show_alert=True)
    file = got[0]["file"]
    videoid = got[0]["vidid"]
    user = got[0]["by"]
    title = (got[0]["title"]).title()
    stream_type = (got[0]["streamtype"]).title()
    DUR = get_duration(got)    
    if "live_" in file:
        IMAGE = get_image(videoid)
    elif "vid_" in file:
        IMAGE = get_image(videoid)
    elif "index_" in file:
        IMAGE = config.STREAM_IMG_URL
    else:
        if videoid == "telegram":
            IMAGE = (
                config.TELEGRAM_AUDIO_URL
                if stream_type == "Audio"
                else config.TELEGRAM_VIDEO_URL
            )
        elif videoid == "soundcloud":
            IMAGE = config.SOUNCLOUD_IMG_URL
        else:
            IMAGE = get_image(videoid)            
    send = _["queue_6"] if DUR == "Unknown" else _["queue_7"]
    cap = _["queue_8"].format(app.mention, title, stream_type, user, send)    
    upl = (
        queue_markup(_, DUR, cplay, videoid)
        if DUR == "Unknown"
        else queue_markup(
            _,
            DUR,
            cplay,
            videoid,
            seconds_to_min(got[0]["played"]),
            got[0]["dur"],
        )
    ) 
    basic[videoid] = True
    med = InputMediaPhoto(media=IMAGE, caption=cap)
    try:
        mystic = await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except:
        mystic = CallbackQuery.message
    if DUR != "Unknown":
        try:
            while db[chat_id][0]["vidid"] == videoid:
                await asyncio.sleep(5)             
                if await is_active_chat(chat_id):
                    if basic[videoid]:
                        if await is_music_playing(chat_id):
                            try:
                                buttons = queue_markup(
                                    _,
                                    DUR,
                                    cplay,
                                    videoid,
                                    seconds_to_min(db[chat_id][0]["played"]),
                                    db[chat_id][0]["dur"],
                                )
                                await mystic.edit_reply_markup(reply_markup=buttons)
                            except FloodWait:
                                pass
                            except Exception:
                                pass
                        else:
                            pass
                    else:
                        break
                else:
                    break
        except:
            return