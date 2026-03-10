from pyrogram import filters
from pyrogram.types import (InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)
from config import BANNED_USERS
from Sonic import app
from Sonic.utils.decorators.language import language, languageCB
import aiohttp
from py_yt import VideosSearch
import random
import urllib.parse
import json


async def get_itunes_suggestions(query: str, limit: int = 5):
    """Fetch up to <i>limit</i> song suggestions from iTunes by keyword."""
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://itunes.apple.com/search?term={encoded_query}&entity=song&limit={limit}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return []
                # iTunes can return JSON with a text/javascript mimetype, so we parse manually
                text = await response.text()
                data = json.loads(text)
                results = data.get("results", [])
                suggestions = []
                for res in results:
                    track_name = res.get("trackName")
                    artist_name = res.get("artistName")
                    if track_name and artist_name:
                        suggestions.append(f"{track_name} {artist_name}")
                return suggestions
    except:
        return []

RANDOM_TERMS = [
    "top hits",
    "phonk music", 
    "bollywood hits", 
    "punjabi top"
    "latest bollywood hits", 
    "punjabi chartbusters", 
    "indie indian pop", 
    "soothing ghazals", 
    "classic 90s bollywood", 
    "desi hip hop", 
    "sufi fusion music", 
    "relaxing indian lofi", 
    "south indian hits",
    "trending indian reels music"
]

@app.on_message(
    filters.command(["suggest", "suggestion", "suggestions"])
    & filters.group
    & ~BANNED_USERS
)
@language
async def suggest_songs(client, message: Message, _):
    if len(message.command) < 2:
        query = random.choice(RANDOM_TERMS)
        text = _["suggest_1"]
    else:
        query = message.text.split(None, 1)[1]
        text = _["suggest_2"].format(query)

    # Get smarter suggestions via iTunes
    try:
        suggestions = await get_itunes_suggestions(query, limit=5)
    except:
        suggestions = []
    
    if not suggestions:
        # Fallback to searching YouTube name only
        try:
            results = (await VideosSearch(query, limit=5).next())["result"]
            suggestions = [res["title"] for res in results]
        except:
            suggestions = []
    
    if not suggestions:
        return await message.reply_text("❌ No suggestions found for your keyword. Try a more common artist or song name.")

    upl = []
    # Deduplicate and limit to 5
    seen = set()
    final_suggestions = []
    for s in suggestions:
        if s.lower() not in seen:
            seen.add(s.lower())
            final_suggestions.append(s)
    
    for song in final_suggestions[:5]:
        upl.append(
            [
                InlineKeyboardButton(
                    # Truncate long titles for readability
                    text=(song[:20] + "…" if len(song) > 20 else song),
                    callback_data=f"SugPlay {song[:20]}|{message.from_user.id}"
                )
            ]
        )
    upl.append(
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close"
            )
        ]
    )
    
    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(upl)
    )

@app.on_callback_query(filters.regex("SugPlay") & ~BANNED_USERS)
@languageCB
async def play_suggested(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    song_name, user_id = callback_request.split("|")
    
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer("This is not for you. Trigger your own /suggest command.", show_alert=True)
        except:
            return

    try:
        await CallbackQuery.answer("Processing your choice...", show_alert=False)
    except:
        pass

    # Single message editing logic (Search -> Download -> PlayCard)
    # We use the existing Suggestion message as the 'mystic'
    mystic = CallbackQuery.message
    await mystic.edit_text(f"🔍 <b>Searching for:</b> <i>{song_name}</i>\n\n<i>Please wait...</i>")

    from Sonic import YouTube
    from Sonic.utils.stream.stream import stream
    
    chat_id = CallbackQuery.message.chat.id
    user_name = CallbackQuery.from_user.first_name
    
    try:
        details, track_id = await YouTube.track(song_name)
    except Exception as e:
        return await mystic.edit_text(f"❌ Error during search: {e}")
        
    if not details:
        return await mystic.edit_text("❌ No results found on YouTube for this suggestion.")
        
    try:
        # The 'stream' function will now edit 'mystic' to 'Downloading...' then to the play card.
        await stream(
            _,
            mystic,
            CallbackQuery.from_user.id,
            details,
            chat_id,
            user_name,
            chat_id,
            video=None,
            streamtype="youtube",
            forceplay=False,
        )
    except Exception as e:
        return await mystic.edit_text(f"❌ Error during playback: {e}")
