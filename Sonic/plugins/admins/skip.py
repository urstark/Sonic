from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message, LinkPreviewOptions

import config
from Sonic import YouTube, app
from Sonic.core.call import Sonic
from Sonic.misc import db
from Sonic.utils.database import get_loop
from Sonic.utils.decorators import AdminRightsCheck
from Sonic.utils.inline import close_markup, stream_markup
from Sonic.utils.stream.autoclear import auto_clean
from Sonic.utils.thumbnails import gen_thumb
from config import BANNED_USERS


@app.on_message(
    filters.command(["skip", "cskip", "next", "cnext"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    loop = await get_loop(chat_id)
    if loop != 0:
        return await message.reply_text(_["admin_8"])
    check = db.get(chat_id)
    if not check:
        return await message.reply_text(_["queue_2"])
    queue_len = len(check)
    if len(message.command) > 1:
        query = message.text.split(None, 1)[1].strip()
        if not query.isnumeric():
            return await message.reply_text(_["admin_9"])
        skip_count = int(query)
        skippable_tracks = queue_len - 1
        if queue_len > 2:
            if 1 <= skip_count <= skippable_tracks:
                for count in range(skip_count):
                    if not check: break
                    popped = check.pop(0)
                    if popped:
                        await auto_clean(popped)
                if not check:
                    await message.reply_text(
                        text=_["admin_6"].format(
                            message.from_user.mention, message.chat.title
                        ),
                        reply_markup=close_markup(_),
                    )
                    try:
                        return await Sonic.stop_stream(chat_id)
                    except:
                        return
            else:
                return await message.reply_text(_["admin_11"].format(skippable_tracks))
        else:
            return await message.reply_text(_["admin_10"])
    else:
        popped = check.pop(0)
        if popped:
            await auto_clean(popped)
        if not check:
            await message.reply_text(
                text=_["admin_6"].format(
                    message.from_user.mention, message.chat.title
                ),
                reply_markup=close_markup(_),
            )
            try:
                return await Sonic.stop_stream(chat_id)
            except:
                return
    queued = check[0]["file"]
    title = (check[0]["title"]).title()
    user = check[0]["by"]
    streamtype = check[0]["streamtype"]
    videoid = check[0]["vidid"]
    status = True if str(streamtype) == "video" else None
    try:
        await check[0]["mystic"].delete()
    except:
        pass
    db[chat_id][0]["played"] = 0
    if "old_dur" in check[0]:
        db[chat_id][0]["dur"] = check[0]["old_dur"]
        db[chat_id][0]["seconds"] = check[0]["old_second"]
        db[chat_id][0]["speed_path"] = None
        db[chat_id][0]["speed"] = 1.0
    try:
        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0:
                return await message.reply_text(_["admin_7"].format(title))
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
            try:
                await Sonic.skip_stream(chat_id, link, video=status, image=image)
            except:
                return await message.reply_text(_["call_6"])
            await send_now_playing(message, None, videoid, title, check[0]["dur"], user, _, chat_id, "tg")

        elif "vid_" in queued:
            # Show "downloading..." status  we'll edit this into the now-playing card
            mystic = await message.reply_text(_["call_7"], link_preview_options=LinkPreviewOptions(is_disabled=True))
            try:
                file_path, direct = await YouTube.download(
                    videoid, mystic, videoid=True, video=status
                )
            except:
                return await mystic.edit_text(_["call_6"])
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
            try:
                await Sonic.skip_stream(chat_id, file_path, video=status, image=image)
            except:
                return await mystic.edit_text(_["call_6"])
            # Edit the "downloading..." message into the now-playing card (no delete + re-send)
            await send_now_playing(message, mystic, videoid, title, check[0]["dur"], user, _, chat_id, "stream")

        elif "index_" in queued:
            try:
                await Sonic.skip_stream(chat_id, videoid, video=status)
            except:
                return await message.reply_text(_["call_6"])
            button = stream_markup(_, chat_id)
            run = await message.reply_photo(
                photo=config.STREAM_IMG_URL,
                caption=_["stream_2"].format(user),
                reply_markup=InlineKeyboardMarkup(button),
                has_spoiler=True,
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

        else:
            if videoid == "telegram":
                image = None
            elif videoid == "soundcloud":
                image = None
            else:
                try:
                    image = await YouTube.thumbnail(videoid, True)
                except:
                    image = None
            try:
                await Sonic.skip_stream(chat_id, queued, video=status, image=image)
            except:
                return await message.reply_text(_["call_6"])

            if videoid == "telegram":
                await send_custom_ui(
                    message, None,
                    config.TELEGRAM_AUDIO_URL, config.TELEGRAM_VIDEO_URL,
                    streamtype, config.SUPPORT_GROUP,
                    title, check[0]["dur"], user, _, chat_id,
                )
            elif videoid == "soundcloud":
                await send_custom_ui(
                    message, None,
                    config.SOUNCLOUD_IMG_URL, config.TELEGRAM_VIDEO_URL,
                    streamtype, config.SUPPORT_GROUP,
                    title, check[0]["dur"], user, _, chat_id,
                )
            else:
                await send_now_playing(message, None, videoid, title, check[0]["dur"], user, _, chat_id, "stream")
    except Exception:
        return await message.reply_text(_["call_6"])


async def send_now_playing(message, mystic, videoid, title, duration, user, _, chat_id, markup_type):
    """
    Show the now-playing card.
    If `mystic` is provided, attempts to edit it in-place via edit_media (no flicker).
    Falls back to reply_photo if edit fails (e.g. message type mismatch).
    """
    button = stream_markup(_, chat_id)
    img = await gen_thumb(videoid)
    caption = _["stream_1"].format(
        f"https://t.me/{app.username}?start=info_{videoid}",
        title[:20],
        duration,
        user,
    )
    run = None
    if mystic:
        try:
            run = await mystic.edit_media(
                InputMediaPhoto(media=img, caption=caption, has_spoiler=True),
                reply_markup=InlineKeyboardMarkup(button),
            )
        except:
            try:
                await mystic.delete()
            except:
                pass

    if not run:
        run = await message.reply_photo(
            photo=img,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(button),
            has_spoiler=True,
        )
    db[chat_id][0]["mystic"] = run
    db[chat_id][0]["markup"] = markup_type


async def send_custom_ui(message, mystic, audio_img, video_img, streamtype, link, title, duration, user, _, chat_id):
    """
    Show a custom now-playing card (Telegram/SoundCloud files).
    Uses edit_media on `mystic` if provided, with fallback to reply_photo.
    """
    button = stream_markup(_, chat_id)
    photo = audio_img if str(streamtype) == "audio" else video_img
    caption = _["stream_1"].format(link, title[:20], duration, user)
    run = None
    if mystic:
        try:
            run = await mystic.edit_media(
                InputMediaPhoto(media=photo, caption=caption, has_spoiler=True),
                reply_markup=InlineKeyboardMarkup(button),
            )
        except:
            try:
                await mystic.delete()
            except:
                pass

    if not run:
        run = await message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(button),
            has_spoiler=True,
        )
    db[chat_id][0]["mystic"] = run
    db[chat_id][0]["markup"] = "tg"