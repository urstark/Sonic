from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent
)
from py_yt import VideosSearch

from Sonic import app
from Sonic.utils.inlinequery import answer
from config import BANNED_USERS
import config


@app.on_inline_query(~BANNED_USERS)
async def inline_query_handler(client, query):
    text = query.query.strip().lower()
    answers = []
    if text.strip() == "":
        try:
            await client.answer_inline_query(query.id, results=answer, cache_time=10)
        except:
            return
    elif text.startswith("public") or text.startswith("playlist"):
        from Sonic.utils.playlists_db import get_public_playlists
        playlists = await get_public_playlists(skip=0, limit=50)
        for pl in playlists:
            title = pl["name"]
            owner = pl["user_id"]
            tracks_count = len(pl.get("tracks", []))
            
            description = f"Owner: {owner} | Tracks: {tracks_count}"
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(" Play Playlist", callback_data=f"pl_play|{owner}|{title}")],
                    [InlineKeyboardButton(" Save to My Playlists", callback_data=f"pl_save|{owner}|{title}")],
                ]
            )
            answers.append(
                InlineQueryResultArticle(
                    title=f" Playlist: {title[:30]}",
                    description=description,
                    thumb_url=config.PLAYLIST_IMG_URL,
                    input_message_content=InputTextMessageContent(f" <b>Playlist Content</b>\nName: {title}\nOwner ID: {owner}\nTracks count: {tracks_count}\n\nClick the button below to play this playlist or save it to your collection!"),
                    reply_markup=buttons
                )
            )
        try:
            return await client.answer_inline_query(query.id, results=answers)
        except:
            return
    else:
        a = VideosSearch(text, limit=20)
        result = (await a.next()).get("result")
        for x in range(15):
            title = (result[x]["title"]).title()
            duration = result[x]["duration"]
            views = result[x]["viewCount"]["short"]
            thumbnail = result[x]["thumbnails"][0]["url"].split("?")[0]
            channellink = result[x]["channel"]["link"]
            channel = result[x]["channel"]["name"]
            link = result[x]["link"]
            published = result[x]["publishedTime"]
            description = f"{views} | {duration} minutes | {channel}  | {published}"
            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʏᴏᴜᴛᴜʙᴇ 🎄",
                            url=link,
                        )
                    ],
                ]
            )
            searched_text = f"""
❄ <b>ᴛɪᴛʟᴇ :</b> <a href={link}>{title}</a>

⏳ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {duration} ᴍɪɴᴜᴛᴇs
👀 <b>ᴠɪᴇᴡs :</b> <code>{views}</code>
🎥 <b>ᴄʜᴀɴɴᴇʟ :</b> <a href={channellink}>{channel}</a>
⏰ <b>ᴘᴜʙʟɪsʜᴇᴅ ᴏɴ :</b> {published}


<u><b>➻ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴍᴏᴅᴇ ʙʏ {app.name}</b></u>"""
            answers.append(
                InlineQueryResultPhoto(
                    photo_url=thumbnail,
                    title=title,
                    thumb_url=thumbnail,
                    description=description,
                    caption=searched_text,
                    reply_markup=buttons,
                )
            )
        try:
            return await client.answer_inline_query(query.id, results=answers)
        except:
            return
