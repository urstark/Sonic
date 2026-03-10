import os
import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from py_yt import VideosSearch

from Sonic import app, YouTube
from Sonic.utils.decorators.language import language
from Sonic.utils.inline.help import help_back_markup
from config import BANNED_USERS, SONG_DOWNLOAD_LIMIT

# Command for downloading songs
@app.on_message(filters.command(["song"]) & ~BANNED_USERS)
@language
async def song_command(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text(_["song_1"])
    
    infog = message.text.split(None, 1)[1]
    mystic = await message.reply_text(_["song_2"])
    
    try:
        results = VideosSearch(infog, limit=1)
        res = (await results.next())["result"]
        if not res:
            return await mystic.edit_text(_["song_3"])
            
        result = res[0]
        title = result["title"]
        duration = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        videoid = result["id"]
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(" Audio", callback_data=f"song_audio|{videoid}"),
                InlineKeyboardButton(" Video", callback_data=f"song_video|{videoid}")
            ],
            [
                InlineKeyboardButton(_["CLOSE_BUTTON"], callback_data="close")
            ]
        ])
        
        await mystic.delete()
        await message.reply_photo(
            photo=thumbnail,
            caption=f"<b>Title:</b> {title}\n<b>Duration:</b> {duration}\n\n{_['song_4']}",
            reply_markup=buttons
        )
    except Exception as e:
        await mystic.edit_text(f"{_['song_3']}\n\n<code>{str(e)}</code>")

@app.on_callback_query(filters.regex(r"^song_") & ~BANNED_USERS)
@language
async def song_callback(client, callback_query: CallbackQuery, _):
    data = callback_query.data.split("|")
    cmd = data[0]
    videoid = data[1]
    
    await callback_query.answer(_["song_5"])
    mystic = await callback_query.message.reply_text(_["song_5"])
    
    try:
        # Get video details to get a clean title
        results = VideosSearch(videoid, limit=1)
        res = (await results.next())["result"]
        title = res[0]["title"] if res else "song"
        # Clean title for filename
        clean_title = "".join([c for c in title if c.isalnum() or c in (" ", ".", "_")]).strip()
        
        if cmd == "song_audio":
            file_path, direct = await YouTube.download(
                videoid, 
                mystic, 
                songaudio=True, 
                videoid=True,
                title=clean_title,
                format_id="bestaudio/best"
            )
            
            if not file_path:
                return await mystic.edit_text(_["song_7"])
                
            await mystic.edit_text(_["song_6"])
            await callback_query.message.reply_audio(
                audio=file_path,
                title=title,
                performer=app.name,
                caption=f"<b>Title:</b> {title}\n\n<b>By:</b> {app.name}"
            )
            
        elif cmd == "song_video":
            file_path, direct = await YouTube.download(
                videoid, 
                mystic, 
                songvideo=True, 
                videoid=True,
                title=clean_title,
                format_id="bestvideo[height<=?720]+bestaudio/best"
            )
            
            if not file_path:
                return await mystic.edit_text(_["song_7"])
                
            await mystic.edit_text(_["song_6"])
            await callback_query.message.reply_video(
                video=file_path,
                caption=f"<b>Title:</b> {title}\n\n<b>By:</b> {app.name}"
            )
            
        await mystic.delete()
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await mystic.edit_text(f"{_['song_7']}\n\n<code>{str(e)}</code>")
