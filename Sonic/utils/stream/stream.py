import asyncio
import os
from random import randint
from typing import Union

from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto

import config
from Sonic import Carbon, YouTube, app
from Sonic.core.call import Sonic
from Sonic.misc import db
from Sonic.utils.database import add_active_video_chat, is_active_chat
from Sonic.utils.exceptions import AssistantErr
from Sonic.utils.inline import aq_markup, close_markup, stream_markup
from Sonic.utils.pastebin import SonicBin
from Sonic.utils.stream.queue import put_queue, put_queue_index
from Sonic.utils.thumbnails import gen_thumb


async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    if not result:
        return

    if forceplay and isinstance(result, list):
        await Sonic.force_stop_stream(chat_id)

        msg = f"{_['play_19']}\n\n"
        count = 0
        first_position = None
        # Parallel detail fetching for speed
        semaphore = asyncio.Semaphore(5)
        async def fetch_and_put(search_query):
            nonlocal count, first_position, msg
            async with semaphore:
                try:
                    (title, duration_min, duration_sec, thumbnail, vidid) = await YouTube.details(search_query, False if spotify else True)
                except:
                    return
                if str(duration_min) == "None" or duration_sec > config.DURATION_LIMIT:
                    return
                
                await put_queue(
                    chat_id, original_chat_id, f"vid_{vidid}", title, duration_min,
                    user_name, vidid, user_id, "video" if video else "audio",
                    mystic=mystic,
                )
                pos = len(db.get(chat_id)) - 1
                if first_position is None:
                    first_position = pos
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {pos}\n\n"

        if await is_active_chat(chat_id):
            tasks = [fetch_and_put(s) for s in result[:config.PLAYLIST_FETCH_LIMIT]]
            await asyncio.gather(*tasks)
        else:
            # For non-active chats, we still play the first song immediately
            # then we could parallelize the rest. 
            # (Simplified for now to keep the first song logic intact)
            for search in result:
                if int(count) == config.PLAYLIST_FETCH_LIMIT:
                    break
                try:
                    (title, duration_min, duration_sec, thumbnail, vidid) = await YouTube.details(search, False if spotify else True)
                except: continue
                if str(duration_min) == "None" or duration_sec > config.DURATION_LIMIT:
                    continue

                if not forceplay:
                    db[chat_id] = []
                status = True if video else None
                try:
                    await mystic.edit_text(_["play_23"])
                    file_path, direct = await YouTube.download(vidid, mystic, video=status, videoid=True)
                except: raise AssistantErr(_["play_14"])
                if not file_path: raise AssistantErr(_["play_14"])

                await put_queue(
                    chat_id, original_chat_id, file_path if direct else f"vid_{vidid}",
                    title, duration_min, user_name, vidid, user_id, "video" if video else "audio",
                    forceplay=forceplay,
                    mystic=mystic,
                )
                await Sonic.join_call(chat_id, original_chat_id, file_path, video=status, image=thumbnail)
                if first_position is None:
                    first_position = 0
                img = await gen_thumb(vidid)
                button = stream_markup(_, chat_id)
                try:
                    await mystic.edit_media(
                        InputMediaPhoto(
                            media=img,
                            caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vidid}", title[:20], duration_min, user_name),
                            has_spoiler=True,
                        ),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                except:
                    try: await mystic.delete()
                    except: pass
                    mystic = await app.send_photo(
                        chat_id=original_chat_id, photo=img,
                        caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vidid}", title[:20], duration_min, user_name),
                        reply_markup=InlineKeyboardMarkup(button),
                        has_spoiler=True,
                    )
                db[chat_id][0]["mystic"] = mystic
                db[chat_id][0]["markup"] = "stream"
                count += 1
                # After starting the first song, parallelize the rest
                remaining = result[result.index(search)+1 : config.PLAYLIST_FETCH_LIMIT]
                if remaining:
                    tasks = [fetch_and_put(s) for s in remaining]
                    await asyncio.gather(*tasks)
                break

        if count == 0:
            return
        else:
            if first_position == 0:
                if count > 1:
                    # Tracks 1 onwards are actual queue additions
                    queued_count = count - 1
                    caption = _["queue_4"].format(
                        f"1-{queued_count}" if queued_count > 1 else "1",
                        f"Playlist ({queued_count} tracks)" if queued_count > 1 else title[:20],
                        "Various" if queued_count > 1 else duration_min,
                        user_name
                    )
                    # Use a separate message for the queue notification to not overwrite the play card
                    await app.send_message(
                        chat_id=original_chat_id,
                        text=caption,
                    )
                return
            
            # Bot was already playing, so we just edit the mystic (which is a text message)
            final_pos = first_position if first_position is not None else (len(db.get(chat_id)) - count)
            caption = _["queue_4"].format(
                f"{final_pos}-{final_pos+count-1}" if count > 1 else f"{final_pos}",
                f"Playlist ({count} tracks)" if count > 1 else title[:20],
                "Various" if count > 1 else duration_min,
                user_name
            )
            upl = aq_markup(_, chat_id, final_pos)
            try:
                await mystic.edit_text(caption, reply_markup=InlineKeyboardMarkup(upl))
            except:
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text=caption,
                    reply_markup=InlineKeyboardMarkup(upl),
                )
                # Update mystic for all newly added songs
                for idx in range(pos - count + 1, pos + 1):
                    try:
                        db[chat_id][idx]["mystic"] = run
                    except:
                        pass
            return

    elif streamtype == "db_playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        first_position = None
        
        # Parallel detail fetching for db_playlist (though details are already in result, we still need to put_queue)
        semaphore = asyncio.Semaphore(5)
        async def put_track(track_data):
            nonlocal count, first_position, msg
            async with semaphore:
                title = track_data.get("title", "Unknown Track")
                duration_min = track_data.get("duration_min", "0:00")
                vidid = track_data.get("vidid")
                if not vidid:
                    return

                await put_queue(
                    chat_id, original_chat_id, f"vid_{vidid}", title, duration_min,
                    user_name, vidid, user_id, "video" if video else "audio",
                    mystic=mystic,
                )
                pos = len(db.get(chat_id)) - 1
                if first_position is None:
                    first_position = pos
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {pos}\n\n"

        if await is_active_chat(chat_id):
            tasks = [put_track(t) for t in result[:config.PLAYLIST_FETCH_LIMIT]]
            await asyncio.gather(*tasks)
        else:
            for track in result:
                if int(count) == config.PLAYLIST_FETCH_LIMIT:
                    break
                
                title = track.get("title", "Unknown Track")
                duration_min = track.get("duration_min", "0:00")
                vidid = track.get("vidid")
                if not vidid:
                    continue

                if not forceplay:
                    db[chat_id] = []
                status = True if video else None
                try:
                    await mystic.edit_text(_["play_23"])
                    file_path, direct = await YouTube.download(vidid, mystic, video=status, videoid=True)
                except: continue
                if not file_path: continue

                await put_queue(
                    chat_id, original_chat_id, file_path if direct else f"vid_{vidid}",
                    title, duration_min, user_name, vidid, user_id, "video" if video else "audio",
                    forceplay=forceplay,
                    mystic=mystic,
                )
                await Sonic.join_call(chat_id, original_chat_id, file_path, video=status, image=config.PLAYLIST_IMG_URL)
                if first_position is None:
                    first_position = 0
                img = await gen_thumb(vidid)
                button = stream_markup(_, chat_id)
                try: await mystic.delete()
                except: pass
                mystic = await app.send_photo(
                    chat_id=original_chat_id, photo=img,
                    caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vidid}", title[:23], duration_min, user_name),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True,
                )
                db[chat_id][0]["mystic"] = mystic
                db[chat_id][0]["markup"] = "stream"
                count += 1
                
                remaining = result[result.index(track)+1 : config.PLAYLIST_FETCH_LIMIT]
                if remaining:
                    tasks = [fetch_and_put(t) for t in remaining]
                    await asyncio.gather(*tasks)
                break
            if first_position == 0:
                if count > 1:
                    queued_count = count - 1
                    caption = _["queue_4"].format(
                        f"1-{queued_count}" if queued_count > 1 else "1",
                        f"Playlist ({queued_count} tracks)" if queued_count > 1 else title[:27],
                        "Various" if queued_count > 1 else duration_min,
                        user_name
                    )
                    await app.send_message(
                        chat_id=original_chat_id,
                        text=caption,
                    )
                return

            final_pos = first_position if first_position is not None else (len(db.get(chat_id)) - count)
            caption = _["queue_4"].format(
                f"{final_pos}-{final_pos+count-1}" if count > 1 else f"{final_pos}",
                f"Playlist ({count} tracks)" if count > 1 else title[:27],
                "Various" if count > 1 else duration_min,
                user_name
            )
            upl = aq_markup(_, chat_id, final_pos)
            try:
                await mystic.edit_text(caption, reply_markup=InlineKeyboardMarkup(upl))
            except:
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text=caption,
                    reply_markup=InlineKeyboardMarkup(upl),
                )
                # Update mystic for all newly added songs
                for idx in range(final_pos, final_pos + count):
                    try:
                        db[chat_id][idx]["mystic"] = run
                    except:
                        pass
            return

    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]
        status = True if video else None

        # For forceplay, stop current stream so we always take the immediate-play path
        if forceplay:
            await Sonic.force_stop_stream(chat_id)

        current_queue = db.get(chat_id)
        if not forceplay and current_queue is not None and len(current_queue) >= 10:
             return await mystic.edit_text("You can't add more than 10 songs to the queue.")

        try:
            await mystic.edit_text(_["play_24"])
            file_path, direct = await YouTube.download(
                vidid, mystic, videoid=True, video=status
            )
        except:
            raise AssistantErr(_["play_14"])
        
        if not file_path:
             raise AssistantErr(_["play_14"])

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                mystic=mystic,
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id, position)
            caption = _["queue_4"].format(position, title[:20], duration_min, user_name)
            try:
                await mystic.edit_text(caption, reply_markup=InlineKeyboardMarkup(button))
            except:
                try:
                    await mystic.delete()
                except:
                    pass
                run = await app.send_message(
                    chat_id=original_chat_id,
                    text=caption,
                    reply_markup=InlineKeyboardMarkup(button),
                )
                try:
                    db[chat_id][position]["mystic"] = run
                except:
                    pass
            db[chat_id][0]["markup"] = "stream"
        else:
            if not forceplay:
                db[chat_id] = []
            # put_queue FIRST so db is populated before join_call starts streaming.
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
                mystic=mystic,
            )
            await Sonic.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail,
            )
            img = await gen_thumb(vidid)
            button = stream_markup(_, chat_id)
            try:
                await mystic.edit_media(
                    InputMediaPhoto(
                        media=img,
                        caption=_["stream_1"].format(
                            f"https://t.me/{app.username}?start=info_{vidid}",
                            title[:20],
                            duration_min,
                            user_name,
                        ),
                        has_spoiler=True,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
            except:
                try:
                    await mystic.delete()
                except:
                    pass
                mystic = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(
                        f"https://t.me/{app.username}?start=info_{vidid}",
                        title[:20],
                        duration_min,
                        user_name,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True,
                )
            db[chat_id][0]["mystic"] = mystic
            db[chat_id][0]["markup"] = "stream"

    elif streamtype == "soundcloud":
        file_path = result["filepath"]
        title = result["title"]
        duration_min = result["duration_min"]
        
        if not file_path:
            raise AssistantErr(_["play_14"])

        # For forceplay, stop current stream so we always take the immediate-play path
        if forceplay:
            await Sonic.force_stop_stream(chat_id)

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
                mystic=mystic,
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id, position)
            await mystic.edit_media(
                InputMediaPhoto(
                    media=config.SOUNCLOUD_IMG_URL,
                    caption=_["queue_4"].format(position, title[:20], duration_min, user_name),
                    has_spoiler=True,
                ),
                reply_markup=InlineKeyboardMarkup(button)
            )
            db[chat_id][0]["markup"] = "tg"
        else:
            if not forceplay:
                db[chat_id] = []
            # put_queue FIRST so db is populated before join_call starts streaming.
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
                forceplay=forceplay,
                mystic=mystic,
            )
            await Sonic.join_call(chat_id, original_chat_id, file_path, video=None)
            button = stream_markup(_, chat_id)
            try:
                await mystic.edit_media(
                    InputMediaPhoto(
                        media=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(
                            config.SUPPORT_GROUP, title[:20], duration_min, user_name
                        ),
                        has_spoiler=True,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
            except:
                try:
                    await mystic.delete()
                except:
                    pass
                mystic = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.SOUNCLOUD_IMG_URL,
                    caption=_["stream_1"].format(
                        config.SUPPORT_GROUP, title[:20], duration_min, user_name
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True,
                )
            db[chat_id][0]["mystic"] = mystic
            db[chat_id][0]["markup"] = "tg"

    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = (result["title"]).title()
        duration_min = result["dur"]
        status = True if video else None
        
        if not file_path:
            raise AssistantErr(_["play_5"])

        # For forceplay, stop current stream so we always take the immediate-play path
        if forceplay:
            await Sonic.force_stop_stream(chat_id)

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
                mystic=mystic,
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id, position)
            try:
                await mystic.edit_media(
                    InputMediaPhoto(
                        media=config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL,
                        caption=_["queue_4"].format(position, title[:20], duration_min, user_name),
                        has_spoiler=True,
                    ),
                    reply_markup=InlineKeyboardMarkup(button)
                )
            except:
                try:
                    await mystic.delete()
                except:
                    pass
                mystic = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL,
                    caption=_["queue_4"].format(position, title[:20], duration_min, user_name),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True,
                )
            db[chat_id][0]["markup"] = "tg"
        else:
            if not forceplay:
                db[chat_id] = []
            # put_queue FIRST so db is populated before join_call starts streaming.
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
                mystic=mystic,
            )
            await Sonic.join_call(chat_id, original_chat_id, file_path, video=status)
            if video:
                await add_active_video_chat(chat_id)
            button = stream_markup(_, chat_id)
            try:
                await mystic.edit_media(
                    InputMediaPhoto(
                        media=config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL,
                        caption=_["stream_1"].format(link, title[:20], duration_min, user_name),
                        has_spoiler=True,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
            except:
                try:
                    await mystic.delete()
                except:
                    pass
                mystic = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL,
                    caption=_["stream_1"].format(link, title[:20], duration_min, user_name),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True,
                )
            db[chat_id][0]["mystic"] = mystic
            db[chat_id][0]["markup"] = "tg"


    elif streamtype == "live":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        thumbnail = result["thumb"]
        duration_min = "Live Track"
        status = True if video else None
        
        # For forceplay, stop current stream so we always take the immediate-play path
        if forceplay:
            await Sonic.force_stop_stream(chat_id)

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                mystic=mystic,
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id, position)
            try:
                await mystic.edit_media(
                    InputMediaPhoto(
                        media=thumbnail,
                        caption=_["queue_4"].format(position, title[:20], duration_min, user_name),
                        has_spoiler=True,
                    ),
                    reply_markup=InlineKeyboardMarkup(button)
                )
            except:
                try:
                    await mystic.delete()
                except:
                    pass
                mystic = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=thumbnail,
                    caption=_["queue_4"].format(position, title[:20], duration_min, user_name),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True,
                )
            db[chat_id][0]["markup"] = "tg"
        else:
            if not forceplay:
                db[chat_id] = []
            n, file_path = await YouTube.video(link)
            if n == 0:
                raise AssistantErr(_["str_3"])
            

            if not file_path:
                raise AssistantErr(_["play_14"])

            # put_queue FIRST so db is populated before join_call starts streaming.
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
                mystic=mystic,
            )
            await Sonic.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status,
                image=thumbnail if thumbnail else None,
            )
            img = await gen_thumb(vidid)
            button = stream_markup(_, chat_id)
            try:
                await mystic.delete()
            except:
                pass
            mystic = await app.send_photo(
                chat_id=original_chat_id,
                photo=img,
                caption=_["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:20],
                    duration_min,
                    user_name,
                ),
                reply_markup=InlineKeyboardMarkup(button),
                has_spoiler=True,
            )
            db[chat_id][0]["mystic"] = mystic
            db[chat_id][0]["markup"] = "tg"


    elif streamtype == "index":
        link = result
        title = "x  38 "
        duration_min = "00:00"
        

        if not link:
             raise AssistantErr(_["play_14"])

        if await is_active_chat(chat_id):
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
                mystic=mystic,
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id, position)
            try:
                await mystic.edit_media(
                    InputMediaPhoto(
                        media=config.STREAM_IMG_URL,
                        caption=_["queue_4"].format(position, title[:20], duration_min, user_name),
                        has_spoiler=True,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
            except:
                try:
                    await mystic.delete()
                except:
                    pass
                mystic = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["queue_4"].format(position, title[:20], duration_min, user_name),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True,
                )
        else:
            if not forceplay:
                db[chat_id] = []
            # put_queue_index FIRST so db is populated before join_call starts streaming.
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if video else "audio",
                forceplay=forceplay,
                mystic=mystic,
            )
            await Sonic.join_call(
                chat_id,
                original_chat_id,
                link,
                video=True if video else None,
            )
            button = stream_markup(_, chat_id)
            try:
                await mystic.edit_media(
                    InputMediaPhoto(
                        media=config.STREAM_IMG_URL,
                        caption=_["stream_2"].format(user_name),
                        has_spoiler=True,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
            except:
                try:
                    await mystic.delete()
                except:
                    pass
                mystic = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(user_name),
                    reply_markup=InlineKeyboardMarkup(button),
                    has_spoiler=True,
                )
            db[chat_id][0]["mystic"] = mystic
            db[chat_id][0]["markup"] = "tg"
